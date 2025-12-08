"""
TASK TYPES CONTRACT

You implement the actual processing logic.
These are just interface definitions.
"""


class FrameUpscaler:
    """
    CONTRACT: Upscale low-resolution frames to high-resolution
    
    YOU IMPLEMENT:
    - Image loading/decoding
    - Upscaling algorithm (OpenCV, PIL, ML model, etc.)
    - Image encoding/compression
    """
    
    @staticmethod
    def upscale(input_data: bytes, params: dict) -> bytes:
        """
        Upscale a frame from low-res to high-res
        
        Args:
            input_data: JPEG/PNG compressed frame
            params: {
                "input_res": [width, height],
                "output_res": [width, height],
                "quality": "fast" | "balanced" | "quality",
                "algorithm": "bicubic" | "lanczos" | "ml"  # optional
            }
        
        Returns:
            bytes: Upscaled frame (JPEG/PNG compressed)
        
        TODO: Decode input_data
        TODO: Apply upscaling algorithm
        TODO: Encode result
        TODO: Return compressed bytes
        """
        raise NotImplementedError("YOU IMPLEMENT THIS")


class AIExecutor:
    """
    CONTRACT: Execute AI/ML tasks
    
    YOU IMPLEMENT:
    - AI model loading
    - Inference
    - Result formatting
    """
    
    @staticmethod
    def npc_dialogue(input_data: dict) -> dict:
        """
        Generate NPC dialogue
        
        Args:
            input_data: {
                "player_input": str,
                "npc_name": str,
                "npc_personality": str,
                "context": dict
            }
        
        Returns:
            dict: {
                "dialogue": str,
                "emotion": str,
                "animation": str
            }
        
        TODO: Load or use AI model
        TODO: Generate contextual response
        """
        raise NotImplementedError("YOU IMPLEMENT THIS")
    
    @staticmethod
    def pathfinding(input_data: dict) -> dict:
        """
        Calculate path from start to goal
        
        Args:
            input_data: {
                "start": [x, y],
                "goal": [x, y],
                "obstacles": [[x, y], ...],
                "algorithm": "astar" | "dijkstra"  # optional
            }
        
        Returns:
            dict: {
                "path": [[x, y], ...],
                "distance": float,
                "algorithm_used": str
            }
        
        TODO: Implement pathfinding algorithm (A*, Dijkstra, etc.)
        """
        raise NotImplementedError("YOU IMPLEMENT THIS")


class PhysicsExecutor:
    """
    CONTRACT: Execute physics simulations
    
    YOU IMPLEMENT:
    - Physics engine setup
    - Simulation stepping
    - State serialization
    """
    
    @staticmethod
    def simulate(input_data: dict) -> dict:
        """
        Run physics simulation
        
        Args:
            input_data: {
                "objects": [{"position": [x,y,z], "velocity": [x,y,z], ...}],
                "timestep": float,
                "num_steps": int,
                "gravity": [x, y, z]
            }
        
        Returns:
            dict: {
                "objects": [{"position": [x,y,z], "velocity": [x,y,z], ...}],
                "collisions": [[obj1_id, obj2_id], ...]
            }
        
        TODO: Implement physics integration (Euler, Verlet, etc.)
        TODO: Detect and resolve collisions
        """
        raise NotImplementedError("YOU IMPLEMENT THIS")


class RayTracingExecutor:
    """
    CONTRACT: Execute ray tracing computations
    
    YOU IMPLEMENT:
    - Ray-object intersection
    - Light calculations
    - Image rendering
    """
    
    @staticmethod
    def trace(input_data: dict) -> bytes:
        """
        Render scene using ray tracing
        
        Args:
            input_data: {
                "camera": {"position": [x,y,z], "direction": [x,y,z]},
                "objects": [{"type": "sphere", "position": [x,y,z], ...}],
                "lights": [{"position": [x,y,z], "color": [r,g,b], ...}],
                "resolution": [width, height],
                "samples_per_pixel": int
            }
        
        Returns:
            bytes: Rendered image (JPEG/PNG)
        
        TODO: Implement ray-object intersection
        TODO: Calculate lighting and shadows
        TODO: Render to image
        """
        raise NotImplementedError("YOU IMPLEMENT THIS")


# TASK TYPE REGISTRY (you populate this with your implementations)
TASK_EXECUTORS = {
    "upscale": FrameUpscaler.upscale,
    "ai_dialogue": AIExecutor.npc_dialogue,
    "ai_pathfinding": AIExecutor.pathfinding,
    "physics": PhysicsExecutor.simulate,
    "raytracing": RayTracingExecutor.trace,
    # Add more task types as you implement them
}


def execute_task(task_type: str, input_data, params: dict = None):
    """
    Route task to appropriate executor
    
    Args:
        task_type: Type of task to execute
        input_data: Task-specific input
        params: Additional parameters
    
    Returns:
        Task-specific output
    
    TODO: Look up executor in TASK_EXECUTORS
    TODO: Call executor with input_data and params
    TODO: Handle errors
    """
    if task_type not in TASK_EXECUTORS:
        raise ValueError(f"Unknown task type: {task_type}")
    
    executor = TASK_EXECUTORS[task_type]
    return executor(input_data, params) if params else executor(input_data)
