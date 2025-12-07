"""
P2C2R User Client - Gamer/Renter

A user client represents a gamer who:
1. Connects to the cloud coordinator
2. Submits tasks (game frames, AI, physics, etc.)
3. Receives results back
4. Assembles the final output
"""

import asyncio
import websockets
import json
import time
import uuid
import logging
from typing import Optional, Dict, Any, Callable

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class UserClient:
    """
    User Client - Gamer consuming distributed compute.
    
    In production, this would:
    - Send G-buffers for ray tracing
    - Request AI inference for NPC behavior
    - Submit physics simulation chunks
    - Assemble results into final game frame
    
    For demo, we submit test tasks.
    """
    
    def __init__(self, user_id: str, coordinator_url: str = "ws://localhost:8765"):
        self.user_id = user_id
        self.coordinator_url = coordinator_url
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.running = False
        self.logger = logging.getLogger(f"User-{user_id}")
        
        # Track pending tasks
        self.pending_tasks: Dict[str, Dict[str, Any]] = {}
        
        # Result callbacks
        self.result_callbacks: Dict[str, Callable] = {}
    
    async def start(self):
        """Connect to coordinator."""
        self.running = True
        self.logger.info(f"🎮 Starting user client: {self.user_id}")
        self.logger.info(f"   Connecting to: {self.coordinator_url}")
        
        while self.running:
            try:
                async with websockets.connect(self.coordinator_url) as websocket:
                    self.websocket = websocket
                    self.logger.info("✓ Connected to coordinator")
                    
                    # Register as user
                    await self.register()
                    
                    # Listen for responses
                    async for message in websocket:
                        await self.handle_message(message)
                
            except websockets.exceptions.ConnectionClosed:
                self.logger.warning("Connection closed by coordinator")
                if self.running:
                    self.logger.info("Retrying in 3 seconds...")
                    await asyncio.sleep(3)
            except Exception as e:
                self.logger.error(f"Connection error: {e}")
                if self.running:
                    self.logger.info("Retrying in 3 seconds...")
                    await asyncio.sleep(3)
    
    async def register(self):
        """Register with the coordinator."""
        msg = {
            'msg_type': 'register_user',
            'msg_id': str(uuid.uuid4()),
            'timestamp': time.time(),
            'data': {
                'user_id': self.user_id,
                'client_info': {
                    'version': '1.0.0',
                    'platform': 'demo'
                }
            }
        }
        
        await self.websocket.send(json.dumps(msg))
        self.logger.info("Sent registration request")
    
    async def handle_message(self, message: str):
        """Handle messages from coordinator."""
        try:
            msg = json.loads(message)
            msg_type = msg['msg_type']
            
            if msg_type == 'registration_ack':
                self.logger.info("✓ Registration confirmed by coordinator")
            
            elif msg_type == 'task_result':
                await self.handle_task_result(msg)
            
            elif msg_type == 'task_failure':
                await self.handle_task_failure(msg)
            
            elif msg_type == 'peer_count_update':
                peer_count = msg['data']['peer_count']
                self.logger.info(f"📊 Peers available: {peer_count}")
            
            elif msg_type == 'error':
                self.logger.error(f"Error from coordinator: {msg['data'].get('error')}")
            
            else:
                self.logger.debug(f"Received: {msg_type}")
        
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
    
    async def handle_task_result(self, msg: dict):
        """Handle task result from coordinator."""
        task_id = msg['data']['task_id']
        result = msg['data']['result']
        execution_time = msg['data'].get('execution_time', 0)
        peer_id = msg['data'].get('peer_id', 'unknown')
        
        self.logger.info(f"✓ Task completed: {task_id[:8]}...")
        self.logger.info(f"  Peer: {peer_id}")
        self.logger.info(f"  Time: {execution_time:.2f}s")
        
        # Call result callback if registered
        if task_id in self.result_callbacks:
            callback = self.result_callbacks.pop(task_id)
            callback(result)
        
        # Remove from pending
        if task_id in self.pending_tasks:
            self.pending_tasks.pop(task_id)
    
    async def handle_task_failure(self, msg: dict):
        """Handle task failure from coordinator."""
        task_id = msg['data']['task_id']
        error = msg['data'].get('error', 'Unknown error')
        
        self.logger.error(f"✗ Task failed: {task_id[:8]}...")
        self.logger.error(f"  Error: {error}")
        
        # Remove from pending
        if task_id in self.pending_tasks:
            self.pending_tasks.pop(task_id)
    
    async def submit_task(
        self,
        task_type: str,
        task_data: dict,
        callback: Optional[Callable] = None
    ) -> str:
        """
        Submit a task to the coordinator.
        
        Args:
            task_type: Type of task (ray_tracing, ai_inference, physics, etc.)
            task_data: Task-specific data
            callback: Optional callback to call when result is received
        
        Returns:
            task_id: Unique task identifier
        """
        task_id = str(uuid.uuid4())
        
        msg = {
            'msg_type': 'task_request',
            'msg_id': str(uuid.uuid4()),
            'timestamp': time.time(),
            'data': {
                'task_id': task_id,
                'user_id': self.user_id,
                'task_data': {
                    'type': task_type,
                    **task_data
                }
            }
        }
        
        self.pending_tasks[task_id] = {
            'type': task_type,
            'submitted_at': time.time(),
            'data': task_data
        }
        
        if callback:
            self.result_callbacks[task_id] = callback
        
        await self.websocket.send(json.dumps(msg))
        self.logger.info(f"📤 Task submitted: {task_type} ({task_id[:8]}...)")
        
        return task_id
    
    async def submit_ray_tracing(
        self,
        complexity: int = 100,
        num_lights: int = 1,
        num_reflective: int = 0,
        resolution: tuple = (1920, 1080)
    ) -> str:
        """Submit a ray tracing task."""
        return await self.submit_task(
            'ray_tracing',
            {
                'complexity': complexity,
                'num_lights': num_lights,
                'num_reflective': num_reflective,
                'resolution': list(resolution)
            }
        )
    
    async def submit_ai_inference(
        self,
        model: str = 'npc_behavior',
        input_data: dict = None
    ) -> str:
        """Submit an AI inference task."""
        return await self.submit_task(
            'ai_inference',
            {
                'model': model,
                'input': input_data or {}
            }
        )
    
    async def submit_physics(
        self,
        num_objects: int = 10,
        timestep: float = 0.016
    ) -> str:
        """Submit a physics simulation task."""
        return await self.submit_task(
            'physics',
            {
                'num_objects': num_objects,
                'timestep': timestep
            }
        )
    
    def stop(self):
        """Stop the user client."""
        self.running = False
        self.logger.info("Stopping user client...")


async def demo_workflow(user: UserClient):
    """Run a demo workflow submitting various tasks."""
    print("\n" + "="*70)
    print("🎮 DEMO WORKFLOW")
    print("="*70)
    print()
    
    # Wait for connection
    await asyncio.sleep(2)
    
    print("Submitting tasks to the P2C2R network...")
    print()
    
    # Submit ray tracing task
    print("1️⃣  Submitting ray tracing task...")
    await user.submit_ray_tracing(complexity=150, num_lights=3, num_reflective=2)
    await asyncio.sleep(1)
    
    # Submit AI inference task
    print("2️⃣  Submitting AI inference task...")
    await user.submit_ai_inference(model='npc_pathfinding')
    await asyncio.sleep(1)
    
    # Submit physics task
    print("3️⃣  Submitting physics simulation task...")
    await user.submit_physics(num_objects=50)
    await asyncio.sleep(2)
    
    # Submit batch of tasks
    print("4️⃣  Submitting batch of 5 ray tracing tasks...")
    for i in range(5):
        await user.submit_ray_tracing(complexity=100 + i*20)
        await asyncio.sleep(0.2)
    
    print()
    print("✓ All tasks submitted!")
    print("  Waiting for results...")
    print()
    
    # Wait for results
    await asyncio.sleep(10)
    
    print("="*70)
    print("✓ Demo workflow complete!")
    print("="*70)


async def interactive_mode(user: UserClient):
    """Interactive mode for manual task submission."""
    print("\n" + "="*70)
    print("🎮 INTERACTIVE MODE")
    print("="*70)
    print()
    print("Commands:")
    print("  rt  - Submit ray tracing task")
    print("  ai  - Submit AI inference task")
    print("  ph  - Submit physics task")
    print("  10  - Submit 10 ray tracing tasks")
    print("  q   - Quit")
    print()
    print("="*70)
    print()
    
    # Wait for connection
    await asyncio.sleep(1)
    
    while user.running:
        try:
            # Read command (note: in async context, this blocks)
            cmd = await asyncio.get_event_loop().run_in_executor(
                None, 
                input, 
                "\n> "
            )
            
            if cmd == 'q':
                break
            elif cmd == 'rt':
                await user.submit_ray_tracing()
            elif cmd == 'ai':
                await user.submit_ai_inference()
            elif cmd == 'ph':
                await user.submit_physics()
            elif cmd == '10':
                print("Submitting 10 tasks...")
                for i in range(10):
                    await user.submit_ray_tracing(complexity=100 + i*10)
                    await asyncio.sleep(0.1)
            else:
                print(f"Unknown command: {cmd}")
        
        except EOFError:
            break
    
    user.stop()


async def main():
    """Run the user client."""
    import sys
    
    # Get user ID from command line or generate one
    if len(sys.argv) > 1:
        user_id = sys.argv[1]
    else:
        user_id = f"user_{uuid.uuid4().hex[:8]}"
    
    # Get coordinator URL from command line or use default
    if len(sys.argv) > 2:
        coordinator_url = sys.argv[2]
    else:
        coordinator_url = "ws://localhost:8765"
    
    # Check for demo mode
    demo_mode = '--demo' in sys.argv or '-d' in sys.argv
    
    user = UserClient(user_id, coordinator_url)
    
    # Start user client and demo/interactive mode concurrently
    try:
        if demo_mode:
            await asyncio.gather(
                user.start(),
                demo_workflow(user)
            )
        else:
            await asyncio.gather(
                user.start(),
                interactive_mode(user)
            )
    except KeyboardInterrupt:
        user.stop()
        print("\n\n👋 User client shutting down...")


if __name__ == '__main__':
    print("=" * 70)
    print("🎮 P2C2R USER CLIENT")
    print("=" * 70)
    print()
    print("This client submits tasks to the P2C2R network.")
    print()
    print("Usage:")
    print("  python user_client.py [user_id] [coordinator_url] [--demo]")
    print()
    print("Example:")
    print("  python user_client.py gamer1 ws://localhost:8765")
    print("  python user_client.py gamer1 ws://localhost:8765 --demo")
    print()
    print("=" * 70)
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
