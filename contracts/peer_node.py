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
        
        PERFORMANCE OPTIMIZATION: The event loop is critical for throughput.
        
        EVENT LOOP PATTERNS:
        Use async/await for non-blocking I/O:
        ```python
        async def run(self):
            while True:
                task = await self.receive_task()  # Non-blocking
                asyncio.create_task(self.execute_and_respond(task))  # Parallel
        ```
        
        CONCURRENCY STRATEGIES:
        1. Task parallelism: Execute multiple tasks concurrently
        2. Pipeline parallelism: Receive next task while processing current
        3. Batch processing: Group small tasks together
        
        RESOURCE THROTTLING:
        - Limit concurrent tasks based on available resources
        - Use semaphore to control parallelism level
        - Monitor resource usage and back-pressure when overloaded
        
        CONNECTION MANAGEMENT:
        - Implement reconnection logic with exponential backoff
        - Keep connection alive with periodic pings
        - Handle connection drops gracefully
        
        TODO: Implement message loop (use asyncio.Queue for task buffer)
        TODO: Call execute_task() for each task received
        TODO: Handle disconnection and reconnection (don't crash on network errors)
        TODO: Implement task queue with configurable size
        TODO: Add concurrent task execution (asyncio.gather or ThreadPoolExecutor)
        TODO: Monitor resource usage and throttle if overloaded
        """
        raise NotImplementedError("YOU IMPLEMENT THIS")
    
    def execute_task(self, task_data: dict) -> dict:
        """
        Execute a task using local resources
        
        PERFORMANCE CRITICAL: This is where the actual computation happens.
        Optimize for:
        1. Fast task execution
        2. Efficient resource utilization
        3. Minimal overhead
        
        OPTIMIZATION TECHNIQUES:
        
        PRELOADING AND CACHING:
        - Preload ML models and keep in memory
        - Cache compiled shaders for rendering tasks
        - Reuse allocated buffers to avoid GC pressure
        
        PARALLEL PROCESSING:
        - Use multiprocessing for CPU-bound tasks
        - Use GPU acceleration when available
        - Process multiple sub-tasks in parallel
        
        RESOURCE MANAGEMENT:
        - Monitor CPU/GPU usage and throttle if needed
        - Implement task timeout to prevent hangs
        - Clean up resources after each task
        
        ERROR HANDLING:
        - Catch and report errors without crashing
        - Return partial results if computation fails midway
        - Implement circuit breaker for repeated failures
        
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
                "processing_time_ms": float,
                "resource_usage": {  # Add for monitoring
                    "cpu_percent": float,
                    "memory_mb": float,
                    "gpu_percent": float  # if applicable
                }
            }
        
        TODO: Implement actual computation (image upscaling, AI, physics, etc.)
        TODO: Add error handling (try/except with detailed error info)
        TODO: Measure processing time (use time.perf_counter for accuracy)
        TODO: Implement task timeout mechanism
        TODO: Add resource monitoring and throttling
        TODO: Preload models/resources to reduce per-task overhead
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
