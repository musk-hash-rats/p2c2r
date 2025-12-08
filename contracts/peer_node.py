"""
PEER NODE CONTRACT

You implement this. I just define the interface.
"""

class PeerNode:
    """
    CONTRACT: Worker node that executes tasks from coordinator
    
    YOU IMPLEMENT:
    - Connection logic
    - Task execution
    - Resource management
    - Error handling
    """
    
    def __init__(self, peer_id: str, coordinator_url: str):
        """
        Args:
            peer_id: Unique identifier for this peer
            coordinator_url: WebSocket URL of coordinator (e.g., "ws://example.com:8765")
        
        TODO: Implement connection setup
        """
        raise NotImplementedError("YOU IMPLEMENT THIS")
    
    def connect(self) -> bool:
        """
        Connect to the coordinator and register this peer
        
        Returns:
            bool: True if connected successfully
        
        TODO: Implement WebSocket/HTTP/TCP connection
        TODO: Send registration message with capabilities
        TODO: Handle connection errors
        """
        raise NotImplementedError("YOU IMPLEMENT THIS")
    
    def run(self):
        """
        Main loop: receive tasks, execute them, send results
        
        TODO: Implement message loop
        TODO: Call execute_task() for each task received
        TODO: Handle disconnection and reconnection
        """
        raise NotImplementedError("YOU IMPLEMENT THIS")
    
    def execute_task(self, task_data: dict) -> dict:
        """
        Execute a task using local resources
        
        Args:
            task_data: {
                "task_id": str,
                "task_type": str,  # "upscale", "ai", "physics", etc.
                "data": bytes or str,
                "params": dict
            }
        
        Returns:
            dict: {
                "task_id": str,
                "result": bytes or str,
                "success": bool,
                "processing_time_ms": float
            }
        
        TODO: Implement actual computation (image upscaling, AI, physics, etc.)
        TODO: Add error handling
        TODO: Measure processing time
        """
        raise NotImplementedError("YOU IMPLEMENT THIS")
    
    def send_heartbeat(self):
        """
        Send periodic heartbeat to coordinator
        
        TODO: Implement keep-alive mechanism
        TODO: Include current load/status
        """
        raise NotImplementedError("YOU IMPLEMENT THIS")


# EXAMPLE USAGE (you write the actual code):
"""
peer = PeerNode(
    peer_id="peer_laptop_001",
    coordinator_url="ws://p2c2r.example.com:8765"
)

if peer.connect():
    print("Connected to coordinator")
    peer.run()  # Blocking - runs forever
"""
