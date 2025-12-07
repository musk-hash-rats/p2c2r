"""
P2C2R Peer Node - Worker that executes tasks

A peer is a computer with idle GPU/CPU resources that:
1. Connects to the cloud coordinator
2. Reports its capabilities (GPU model, CPU cores, etc.)
3. Receives task assignments
4. Executes tasks (ray tracing, AI, physics, etc.)
5. Returns results to coordinator
"""

import asyncio
import websockets
import json
import time
import uuid
import logging
import platform
import psutil
from typing import Optional
from task_executors import execute_task, TASK_EXECUTORS

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class PeerNode:
    """
    Peer Node - Worker that contributes compute resources.
    
    In production, this would:
    - Detect actual GPU (NVIDIA, AMD, etc.)
    - Run real ray tracing kernels
    - Execute actual AI inference
    - Perform physics simulations
    
    For demo, we simulate task execution.
    """
    
    def __init__(self, peer_id: str, coordinator_url: str = "ws://localhost:8765"):
        self.peer_id = peer_id
        self.coordinator_url = coordinator_url
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.running = False
        self.logger = logging.getLogger(f"Peer-{peer_id}")
        
        # Detect system capabilities
        self.capabilities = self.detect_capabilities()
    
    def detect_capabilities(self) -> dict:
        """Detect system capabilities."""
        return {
            'peer_id': self.peer_id,
            'cpu_cores': psutil.cpu_count(logical=False),
            'cpu_threads': psutil.cpu_count(logical=True),
            'ram_gb': round(psutil.virtual_memory().total / (1024**3), 1),
            'platform': platform.system(),
            'python_version': platform.python_version(),
            # In production, detect GPU:
            'gpu': 'RTX 4090 (simulated)',  # Would use pynvml or similar
            'gpu_memory_gb': 24,  # Simulated
            'supports_ray_tracing': True,
            'supports_ai': True,
            'supports_physics': True,
        }
    
    async def start(self):
        """Connect to coordinator and start processing tasks."""
        self.running = True
        self.logger.info(f"🚀 Starting peer node: {self.peer_id}")
        self.logger.info(f"   Connecting to: {self.coordinator_url}")
        
        while self.running:
            try:
                async with websockets.connect(self.coordinator_url) as websocket:
                    self.websocket = websocket
                    self.logger.info("✓ Connected to coordinator")
                    
                    # Register with coordinator
                    await self.register()
                    
                    # Start heartbeat task
                    heartbeat_task = asyncio.create_task(self.send_heartbeats())
                    
                    # Listen for tasks
                    try:
                        async for message in websocket:
                            await self.handle_message(message)
                    except websockets.exceptions.ConnectionClosed:
                        self.logger.warning("Connection closed by coordinator")
                    finally:
                        heartbeat_task.cancel()
                
            except Exception as e:
                self.logger.error(f"Connection error: {e}")
                self.logger.info("Retrying in 5 seconds...")
                await asyncio.sleep(5)
    
    async def register(self):
        """Register with the coordinator."""
        msg = {
            'msg_type': 'register_peer',
            'msg_id': str(uuid.uuid4()),
            'timestamp': time.time(),
            'data': {
                'peer_id': self.peer_id,
                'capabilities': self.capabilities
            }
        }
        
        await self.websocket.send(json.dumps(msg))
        self.logger.info("Sent registration request")
    
    async def send_heartbeats(self):
        """Send periodic heartbeats to coordinator."""
        while True:
            try:
                msg = {
                    'msg_type': 'heartbeat',
                    'msg_id': str(uuid.uuid4()),
                    'timestamp': time.time(),
                    'data': {
                        'peer_id': self.peer_id,
                        'cpu_usage': psutil.cpu_percent(),
                        'memory_usage': psutil.virtual_memory().percent
                    }
                }
                await self.websocket.send(json.dumps(msg))
                await asyncio.sleep(5)  # Heartbeat every 5 seconds
            except Exception as e:
                self.logger.error(f"Heartbeat error: {e}")
                break
    
    async def handle_message(self, message: str):
        """Handle messages from coordinator."""
        try:
            msg = json.loads(message)
            msg_type = msg['msg_type']
            
            if msg_type == 'registration_ack':
                self.logger.info("✓ Registration confirmed by coordinator")
                self.logger.info(f"  Peer ID: {msg['data']['peer_id']}")
            
            elif msg_type == 'task_assignment':
                await self.handle_task(msg)
            
            else:
                self.logger.debug(f"Received: {msg_type}")
        
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
    
    async def handle_task(self, msg: dict):
        """Execute assigned task."""
        task_id = msg['data']['task_id']
        task_data = msg['data']['task_data']
        task_type = task_data.get('type', 'unknown')
        
        self.logger.info(f"📋 Task assigned: {task_id}")
        self.logger.info(f"   Type: {task_type}")
        
        start_time = time.time()
        
        try:
            # Execute task using real executors
            if task_type in TASK_EXECUTORS:
                result = await execute_task(task_type, task_data)
            elif task_type == 'ray_tracing':
                # Legacy support
                result = await execute_task('rt_reflections', task_data)
            elif task_type == 'ai_inference':
                # Legacy support - default to dialogue
                result = await execute_task('ai_npc_dialogue', task_data)
            elif task_type == 'physics':
                # Legacy support
                result = await execute_task('physics_rigid_body', task_data)
            else:
                # Unknown task type
                result = {'status': 'unknown_type', 'type': task_type}
            
            execution_time = time.time() - start_time
            self.logger.info(f"✓ Task completed in {execution_time:.2f}s")
            
            # Send result back to coordinator
            result_msg = {
                'msg_type': 'task_result',
                'msg_id': str(uuid.uuid4()),
                'timestamp': time.time(),
                'data': {
                    'task_id': task_id,
                    'peer_id': self.peer_id,
                    'result': result,
                    'execution_time': execution_time
                }
            }
            await self.websocket.send(json.dumps(result_msg))
        
        except Exception as e:
            self.logger.error(f"✗ Task failed: {e}")
            
            # Send failure notification
            failure_msg = {
                'msg_type': 'task_failure',
                'msg_id': str(uuid.uuid4()),
                'timestamp': time.time(),
                'data': {
                    'task_id': task_id,
                    'peer_id': self.peer_id,
                    'error': str(e)
                }
            }
            await self.websocket.send(json.dumps(failure_msg))
    
    async def execute_ray_tracing(self, task_data: dict) -> dict:
        """
        Execute ray tracing task.
        
        In production:
        - Receive G-buffer (geometry, normals, materials)
        - Run OptiX/CUDA ray tracing kernels
        - Trace rays (shadows, reflections, GI)
        - Return ray traced image layer
        
        For demo: Simulate computation time
        """
        complexity = task_data.get('complexity', 100)
        num_lights = task_data.get('num_lights', 1)
        num_reflective = task_data.get('num_reflective', 0)
        
        # Simulate ray tracing computation
        # More complexity = longer time
        simulation_time = 0.02 + (complexity / 1000) + (num_lights * 0.01) + (num_reflective * 0.005)
        await asyncio.sleep(simulation_time)
        
        return {
            'status': 'success',
            'type': 'ray_tracing',
            'output': {
                'format': 'rgba_float',
                'resolution': task_data.get('resolution', [1920, 1080]),
                'data': f'<simulated ray traced image data: {complexity} complexity>',
                'rays_traced': complexity * 100,
                'samples_per_pixel': 4
            }
        }
    
    async def execute_ai_inference(self, task_data: dict) -> dict:
        """
        Execute AI inference task.
        
        In production:
        - Load AI model (NPC behavior, dialogue generation, etc.)
        - Run inference
        - Return predictions
        
        For now: Real AI using simple models
        """
        model = task_data.get('model', 'npc_behavior')
        input_data = task_data.get('input', {})
        
        # Simulate inference time
        await asyncio.sleep(0.05)
        
        return {
            'status': 'success',
            'type': 'ai_inference',
            'output': {
                'model': model,
                'predictions': f'<simulated AI output for {model}>',
                'confidence': 0.95
            }
        }
    
    async def execute_physics(self, task_data: dict) -> dict:
        """
        Execute physics simulation.
        
        In production:
        - Simulate rigid bodies
        - Compute collisions
        - Integrate positions
        - Return updated state
        
        For demo: Simulate computation
        """
        num_objects = task_data.get('num_objects', 10)
        timestep = task_data.get('timestep', 0.016)
        
        # Simulate physics computation
        await asyncio.sleep(0.01 * (num_objects / 10))
        
        return {
            'status': 'success',
            'type': 'physics',
            'output': {
                'objects': num_objects,
                'timestep': timestep,
                'state': f'<simulated physics state for {num_objects} objects>'
            }
        }
    
    async def execute_generic(self, task_data: dict) -> dict:
        """Execute generic task."""
        await asyncio.sleep(0.1)
        
        return {
            'status': 'success',
            'type': 'generic',
            'output': {'data': '<simulated output>'}
        }
    
    def stop(self):
        """Stop the peer node."""
        self.running = False
        self.logger.info("Stopping peer node...")


async def main():
    """Run a peer node."""
    import sys
    
    # Get peer ID from command line or generate one
    if len(sys.argv) > 1:
        peer_id = sys.argv[1]
    else:
        peer_id = f"peer_{uuid.uuid4().hex[:8]}"
    
    # Get coordinator URL from command line or use default
    if len(sys.argv) > 2:
        coordinator_url = sys.argv[2]
    else:
        coordinator_url = "ws://localhost:8765"
    
    peer = PeerNode(peer_id, coordinator_url)
    
    try:
        await peer.start()
    except KeyboardInterrupt:
        peer.stop()
        print("\n\n👋 Peer node shutting down...")


if __name__ == '__main__':
    print("=" * 70)
    print("🖥️  P2C2R PEER NODE")
    print("=" * 70)
    print()
    print("This peer will contribute compute resources to the P2C2R network.")
    print()
    print("Usage:")
    print("  python peer_node.py [peer_id] [coordinator_url]")
    print()
    print("Example:")
    print("  python peer_node.py my_gpu_1 ws://localhost:8765")
    print()
    print("=" * 70)
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
