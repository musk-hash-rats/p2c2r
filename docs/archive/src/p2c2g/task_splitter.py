"""
Task Splitting Strategies for P2C2G

Decomposes large tasks into smaller subtasks that can be
distributed across multiple peers.
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import numpy as np

from .models import Task


@dataclass
class TileBounds:
    """Represents a rectangular region of the screen."""
    x: int
    y: int
    width: int
    height: int
    
    @property
    def area(self) -> int:
        return self.width * self.height


class TaskSplitter:
    """Base class for task splitting strategies."""
    
    def split(self, task: Task, num_peers: int) -> List[Task]:
        """
        Split a task into subtasks.
        
        Args:
            task: Original task
            num_peers: Number of peers to split across
            
        Returns:
            List of subtasks
        """
        raise NotImplementedError


class SpatialSplitter(TaskSplitter):
    """
    Split rendering tasks spatially (divide screen into tiles).
    
    Strategy: Adaptive tiling based on estimated complexity
    """
    
    def split(self, task: Task, num_peers: int) -> List[Task]:
        """
        Split rendering task into tiles.
        
        For ray tracing, we want tiles of equal COMPUTATIONAL cost,
        not equal size. This balances load across peers.
        """
        
        # Get resolution from task
        resolution = task.constraints.get('resolution', (1920, 1080))
        width, height = resolution
        
        # Estimate complexity (in production, use actual scene analysis)
        complexity_map = self._estimate_complexity(task, width, height)
        
        # Create adaptive tiles
        tiles = self._create_tiles(complexity_map, num_peers)
        
        # Create subtask for each tile
        subtasks = []
        for i, tile in enumerate(tiles):
            subtask = Task(
                job_id=task.job_id,
                task_id=f"{task.task_id}_tile_{i}",
                payload={
                    **task.payload,
                    'tile_bounds': {
                        'x': tile.x,
                        'y': tile.y,
                        'width': tile.width,
                        'height': tile.height
                    }
                },
                deadline_ms=task.deadline_ms,
                constraints={
                    **task.constraints,
                    'tile_index': i,
                    'total_tiles': num_peers,
                    'estimated_complexity': self._tile_complexity(complexity_map, tile)
                }
            )
            subtasks.append(subtask)
        
        return subtasks
    
    def _estimate_complexity(self, task: Task, width: int, height: int) -> np.ndarray:
        """
        Estimate computational complexity for each pixel.
        
        In production, this would analyze:
        - Geometry density (triangles per pixel)
        - Material complexity (shader cost)
        - Lighting complexity (number of lights)
        - Reflection depth (ray bounces)
        
        For now, use simplified model.
        """
        
        task_type = task.constraints.get('type', 'generic')
        
        if task_type == 'ray_tracing':
            # Ray tracing: center is more complex (more geometry)
            complexity = np.zeros((height, width))
            center_y, center_x = height // 2, width // 2
            
            for y in range(height):
                for x in range(width):
                    # Distance from center (normalized)
                    dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                    max_dist = np.sqrt(center_x**2 + center_y**2)
                    normalized_dist = dist / max_dist
                    
                    # More complex near center
                    complexity[y, x] = 1.0 + (1.0 - normalized_dist) * 2.0
            
            return complexity
        
        else:
            # Default: uniform complexity
            return np.ones((height, width))
    
    def _create_tiles(self, complexity_map: np.ndarray, num_tiles: int) -> List[TileBounds]:
        """
        Create tiles with equal computational cost.
        
        Uses simple grid partitioning. In production, use
        binary space partitioning (BSP) for better balance.
        """
        
        height, width = complexity_map.shape
        
        # Simple grid approach: sqrt(n) x sqrt(n)
        grid_size = int(np.ceil(np.sqrt(num_tiles)))
        tile_width = width // grid_size
        tile_height = height // grid_size
        
        tiles = []
        for row in range(grid_size):
            for col in range(grid_size):
                if len(tiles) >= num_tiles:
                    break
                
                x = col * tile_width
                y = row * tile_height
                
                # Last tile in row/col takes remainder
                w = tile_width if col < grid_size - 1 else width - x
                h = tile_height if row < grid_size - 1 else height - y
                
                tiles.append(TileBounds(x=x, y=y, width=w, height=h))
        
        return tiles
    
    def _tile_complexity(self, complexity_map: np.ndarray, tile: TileBounds) -> float:
        """Calculate total complexity for a tile."""
        
        region = complexity_map[
            tile.y:tile.y + tile.height,
            tile.x:tile.x + tile.width
        ]
        return float(region.sum())
    
    def merge_results(self, results: List, resolution: Tuple[int, int]) -> np.ndarray:
        """
        Merge tile results back into full image.
        
        Args:
            results: List of Result objects with rendered tiles
            resolution: Output resolution (width, height)
            
        Returns:
            Merged image as numpy array
        """
        
        width, height = resolution
        merged_image = np.zeros((height, width, 4), dtype=np.uint8)  # RGBA
        
        for result in results:
            if result.status != 'success':
                continue
            
            # Extract tile data from result
            tile_data = result.output.get('pixels')
            tile_bounds = result.output.get('tile_bounds')
            
            if tile_data is None or tile_bounds is None:
                continue
            
            # Place tile in merged image
            x, y = tile_bounds['x'], tile_bounds['y']
            w, h = tile_bounds['width'], tile_bounds['height']
            
            merged_image[y:y+h, x:x+w] = tile_data
        
        return merged_image


class FunctionalSplitter(TaskSplitter):
    """
    Split tasks by function/subsystem.
    
    Example: Physics, AI, Rendering, Audio, Particles
    """
    
    def split(self, task: Task, num_peers: int) -> List[Task]:
        """
        Split task into functional components.
        
        Good for heterogeneous workloads where different
        peers specialize in different task types.
        """
        
        task_type = task.constraints.get('type', 'generic')
        
        if task_type == 'game_frame':
            # Split game frame into subsystems
            return self._split_game_frame(task, num_peers)
        
        else:
            # Can't split functionally, return as-is
            return [task]
    
    def _split_game_frame(self, task: Task, num_peers: int) -> List[Task]:
        """
        Split a game frame into subsystems.
        
        Subsystems:
        1. Physics simulation
        2. AI/NPC behavior
        3. Rendering (geometry + lighting)
        4. Post-processing (ray tracing, bloom, etc.)
        5. Audio processing
        """
        
        subsystems = [
            {
                'name': 'physics',
                'deadline_factor': 1.0,  # Must complete in real-time
                'requires': {'cpu_cores': 4}
            },
            {
                'name': 'ai',
                'deadline_factor': 2.0,  # Can be 2x slower (predict ahead)
                'requires': {'cpu_cores': 2}
            },
            {
                'name': 'rendering',
                'deadline_factor': 1.0,
                'requires': {'gpu': True}
            },
            {
                'name': 'ray_tracing',
                'deadline_factor': 6.0,  # Can be much slower (denoising helps)
                'requires': {'rtx': True}
            },
            {
                'name': 'audio',
                'deadline_factor': 1.5,
                'requires': {'cpu_cores': 1}
            }
        ]
        
        # Limit to available peers
        subsystems = subsystems[:num_peers]
        
        # Create subtask for each subsystem
        subtasks = []
        for i, subsystem in enumerate(subsystems):
            subtask = Task(
                job_id=task.job_id,
                task_id=f"{task.task_id}_{subsystem['name']}",
                payload={
                    **task.payload,
                    'subsystem': subsystem['name']
                },
                deadline_ms=int(task.deadline_ms * subsystem['deadline_factor']),
                constraints={
                    **task.constraints,
                    'type': subsystem['name'],
                    **subsystem['requires']
                }
            )
            subtasks.append(subtask)
        
        return subtasks


class PipelineSplitter(TaskSplitter):
    """
    Split tasks by pipeline stage.
    
    Example: Geometry → Lighting → Post-processing
    """
    
    def split(self, task: Task, num_peers: int) -> List[Task]:
        """
        Split rendering into pipeline stages.
        
        Stages execute sequentially, with output of one
        stage feeding into the next.
        """
        
        task_type = task.constraints.get('type', 'generic')
        
        if task_type == 'rendering':
            return self._split_rendering_pipeline(task, num_peers)
        else:
            return [task]
    
    def _split_rendering_pipeline(self, task: Task, num_peers: int) -> List[Task]:
        """
        Split rendering into stages:
        1. Geometry pass (vertex shading, rasterization)
        2. Lighting pass (compute lighting)
        3. Post-processing (bloom, tone mapping, etc.)
        """
        
        stages = [
            {'name': 'geometry', 'requires': {'gpu': True}},
            {'name': 'lighting', 'requires': {'gpu': True}},
            {'name': 'post_processing', 'requires': {'gpu': True}}
        ]
        
        stages = stages[:num_peers]
        
        subtasks = []
        for i, stage in enumerate(stages):
            subtask = Task(
                job_id=task.job_id,
                task_id=f"{task.task_id}_stage_{i}",
                payload={
                    **task.payload,
                    'stage': stage['name'],
                    'stage_index': i,
                    'depends_on': f"{task.task_id}_stage_{i-1}" if i > 0 else None
                },
                deadline_ms=task.deadline_ms,
                constraints={
                    **task.constraints,
                    'pipeline_stage': stage['name'],
                    **stage['requires']
                }
            )
            subtasks.append(subtask)
        
        return subtasks


class HybridSplitter(TaskSplitter):
    """
    Combine multiple splitting strategies.
    
    Example: Spatial + Functional
    - Divide screen into tiles (spatial)
    - Within each tile, split rendering stages (pipeline)
    """
    
    def __init__(self):
        self.spatial_splitter = SpatialSplitter()
        self.functional_splitter = FunctionalSplitter()
        self.pipeline_splitter = PipelineSplitter()
    
    def split(self, task: Task, num_peers: int) -> List[Task]:
        """
        Apply best splitting strategy based on task type.
        """
        
        task_type = task.constraints.get('type', 'generic')
        
        # Choose strategy based on task type
        if task_type == 'ray_tracing':
            # Ray tracing: Spatial decomposition works best
            return self.spatial_splitter.split(task, num_peers)
        
        elif task_type == 'game_frame':
            # Game frame: Functional decomposition
            return self.functional_splitter.split(task, num_peers)
        
        elif task_type == 'rendering':
            # Rendering: Pipeline decomposition
            return self.pipeline_splitter.split(task, num_peers)
        
        else:
            # Unknown type: Don't split
            return [task]
