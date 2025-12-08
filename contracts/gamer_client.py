"""
GAMER CLIENT CONTRACT

You implement this. I just define the interface.
"""

class GamerClient:
    """
    CONTRACT: Client that submits work and receives results
    
    YOU IMPLEMENT:
    - Connection to coordinator
    - Frame capture (optional)
    - Task submission
    - Result retrieval
    """
    
    def __init__(self, client_id: str, coordinator_url: str):
        """
        Args:
            client_id: Unique identifier for this gamer
            coordinator_url: WebSocket URL of coordinator
        
        TODO: Implement initialization
        """
        raise NotImplementedError("YOU IMPLEMENT THIS")
    
    def connect(self) -> bool:
        """
        Connect to the coordinator
        
        Returns:
            bool: True if connected
        
        TODO: Implement connection logic
        """
        raise NotImplementedError("YOU IMPLEMENT THIS")
    
    def submit_task(self, task_type: str, data: bytes, params: dict = None) -> str:
        """
        Submit a task to be processed by peers
        
        Args:
            task_type: "upscale", "ai", "physics", etc.
            data: Raw data (frame, game state, etc.)
            params: Additional parameters
        
        Returns:
            str: task_id for tracking
        
        TODO: Send task to coordinator
        TODO: Return task_id immediately (non-blocking)
        """
        raise NotImplementedError("YOU IMPLEMENT THIS")
    
    def get_result(self, task_id: str, timeout: float = 0.016) -> bytes:
        """
        Get result for a task (with timeout for 60fps)
        
        Args:
            task_id: ID returned from submit_task()
            timeout: Max wait time in seconds (default: 16ms for 60fps)
        
        Returns:
            bytes: Processed result
        
        TODO: Wait for result from coordinator
        TODO: Handle timeout (return None or raise exception)
        """
        raise NotImplementedError("YOU IMPLEMENT THIS")
    
    def submit_and_wait(self, task_type: str, data: bytes, params: dict = None) -> bytes:
        """
        Convenience method: submit task and wait for result
        
        Returns:
            bytes: Processed result
        
        TODO: Call submit_task() then get_result()
        """
        task_id = self.submit_task(task_type, data, params)
        return self.get_result(task_id)


# EXAMPLE USAGE (you write the actual code):
"""
gamer = GamerClient(
    client_id="gamer_pc_001",
    coordinator_url="ws://p2c2r.example.com:8765"
)

if gamer.connect():
    # Submit frame for upscaling
    frame_data = b"..."  # Your frame data
    task_id = gamer.submit_task("upscale", frame_data, {"target_res": (1920, 1080)})
    
    # Get result (blocks up to 16ms)
    upscaled_frame = gamer.get_result(task_id, timeout=0.016)
    
    # Use upscaled_frame in your game
"""
