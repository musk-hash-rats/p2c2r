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
        
        PERFORMANCE OPTIMIZATION: This method should be non-blocking for best
        performance. Implement as async or use connection pooling.
        
        BATCHING STRATEGY:
        When submitting many tasks, consider batching to reduce overhead:
        ```python
        # Instead of many small requests:
        for frame in frames:
            task_id = gamer.submit_task("upscale", frame)  # 100 round-trips
        
        # Batch tasks together:
        task_ids = gamer.submit_tasks_batch([
            {"type": "upscale", "data": frame} for frame in frames
        ])  # 1 round-trip
        ```
        
        CONNECTION POOLING:
        Maintain persistent connections to avoid TCP handshake overhead:
        - Reuse WebSocket connections
        - Keep connection alive between tasks
        - Implement connection pool if using multiple coordinators
        
        Args:
            task_type: "upscale", "ai", "physics", etc.
            data: Raw data (frame, game state, etc.)
            params: Additional parameters
        
        Returns:
            str: task_id for tracking
        
        TODO: Send task to coordinator
        TODO: Return task_id immediately (non-blocking)
        TODO: Consider implementing submit_tasks_batch() for bulk operations
        """
        raise NotImplementedError("YOU IMPLEMENT THIS")
    
    def get_result(self, task_id: str, timeout: float = 0.016) -> bytes:
        """
        Get result for a task (with timeout for 60fps)
        
        PERFORMANCE NOTE: The default timeout of 16ms is extremely aggressive and
        unrealistic for network operations. Consider these recommendations:
        
        TIMEOUT GUIDELINES:
        - Local network (LAN): 50-100ms minimum
        - Internet: 200-500ms minimum
        - Complex tasks (ray tracing, AI): 1-5 seconds
        - Real-time gaming: Use predictive rendering or frame interpolation
        
        OPTIMIZATION STRATEGIES:
        1. Pipeline requests: Submit next frame while waiting for current
        2. Implement result caching: Cache repeated computations
        3. Use progressive results: Return low-quality fast, high-quality later
        4. Implement timeouts per task type, not global
        
        Args:
            task_id: ID returned from submit_task()
            timeout: Max wait time in seconds (default: 16ms - MAY BE TOO SHORT!)
        
        Returns:
            bytes: Processed result
        
        TODO: Wait for result from coordinator
        TODO: Handle timeout (return None or raise exception)
        TODO: Consider implementing retry logic with exponential backoff
        TODO: Add connection pooling to reduce latency
        """
        raise NotImplementedError("YOU IMPLEMENT THIS")
    
    def submit_and_wait(self, task_type: str, data: bytes, params: dict = None, timeout: float = 5.0) -> bytes:
        """
        Convenience method: submit task and wait for result
        
        PERFORMANCE WARNING: This is a blocking operation that should be avoided
        in performance-critical code. Consider using async/await patterns instead:
        
        RECOMMENDED APPROACH:
        ```python
        # Instead of blocking:
        result = gamer.submit_and_wait(task_type, data)  # SLOW - blocks thread
        
        # Use async pattern:
        task_id = await gamer.submit_task(task_type, data)
        result = await gamer.get_result(task_id)  # Non-blocking
        
        # Or batch multiple tasks:
        task_ids = [await gamer.submit_task(t, d) for t, d in tasks]
        results = await asyncio.gather(*[gamer.get_result(tid) for tid in task_ids])
        ```
        
        Args:
            task_type: Type of task to execute
            data: Task input data
            params: Optional task parameters
            timeout: Maximum wait time in seconds (default: 5.0)
        
        Returns:
            bytes: Processed result
        
        TODO: Call submit_task() then get_result()
        TODO: Consider implementing async version: submit_and_wait_async()
        """
        task_id = self.submit_task(task_type, data, params)
        return self.get_result(task_id, timeout=timeout)


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
