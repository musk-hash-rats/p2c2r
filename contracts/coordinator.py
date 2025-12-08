"""
COORDINATOR CONTRACT

You implement this. I just define the interface.
"""

class Coordinator:
    """
    CONTRACT: Central server that distributes tasks to peers
    
    YOU IMPLEMENT:
    - WebSocket/HTTP server
    - Task queuing
    - Load balancing
    - Failover logic
    """
    
    def __init__(self, listen_port: int = 8765):
        """
        Args:
            listen_port: Port to listen on for connections
        
        TODO: Implement server setup
        """
        raise NotImplementedError("YOU IMPLEMENT THIS")
    
    def start(self):
        """
        Start the coordinator server
        
        TODO: Start WebSocket/HTTP server
        TODO: Accept peer and gamer connections
        TODO: Run message loop
        """
        raise NotImplementedError("YOU IMPLEMENT THIS")
    
    def register_peer(self, peer_id: str, capabilities: dict) -> bool:
        """
        Register a new peer that wants to contribute compute
        
        PERFORMANCE OPTIMIZATION: Fast peer registration is critical for
        system scalability.
        
        DATA STRUCTURES:
        Use efficient data structures for peer tracking:
        - Hash map for O(1) peer lookup: {peer_id: PeerInfo}
        - Priority queue for capability-based selection
        - Spatial index for latency-aware routing (if geo-distributed)
        
        CAPABILITY TRACKING:
        Store detailed capabilities for intelligent task assignment:
        - CPU cores, speed, architecture
        - RAM size and availability
        - GPU model, VRAM, compute capability
        - Network bandwidth and latency
        - Historical performance metrics
        
        Args:
            peer_id: Unique peer identifier
            capabilities: {
                "cpu_cores": int,
                "ram_gb": float,
                "gpu": bool,
                "gpu_model": str,        # Add for better task matching
                "network_mbps": float,   # Add for latency prediction
                "location": str          # Add for geo-routing
            }
        
        Returns:
            bool: True if registered successfully
        
        TODO: Add peer to available pool (O(1) insertion)
        TODO: Track peer capabilities for intelligent scheduling
        TODO: Initialize peer performance metrics
        TODO: Set up heartbeat monitoring
        """
        raise NotImplementedError("YOU IMPLEMENT THIS")
    
    def submit_task(self, task: dict, requester_id: str) -> str:
        """
        Gamer submits a task that needs processing
        
        PERFORMANCE OPTIMIZATION: This method is critical for system throughput.
        
        TASK QUEUING STRATEGIES:
        1. Priority Queue: Urgent tasks first (e.g., frame rendering > AI)
        2. Fair Scheduling: Round-robin across gamers to prevent starvation
        3. Task Affinity: Assign similar tasks to same peer (cache locality)
        4. Load Balancing: Distribute based on peer capabilities and load
        
        OPTIMIZATION TECHNIQUES:
        - Use lock-free queues for high concurrency
        - Pre-allocate task slots to reduce memory allocation overhead
        - Implement task deduplication for repeated computations
        - Cache results for identical tasks
        
        PEER SELECTION ALGORITHM:
        Instead of simple round-robin, consider:
        - Peer capability matching (GPU tasks → GPU peers)
        - Load-based selection (assign to least loaded peer)
        - Latency-aware routing (prefer nearby peers)
        - ML-based prediction (use historical performance data)
        
        Args:
            task: {
                "task_type": str,
                "data": bytes,
                "params": dict,
                "priority": int  # Higher = more urgent
            }
            requester_id: ID of the gamer
        
        Returns:
            str: task_id for tracking
        
        TODO: Queue the task
        TODO: Assign to best available peer (consider load, capabilities, latency)
        TODO: Return task_id immediately (O(1) operation, don't block)
        TODO: Implement task prioritization
        TODO: Add task deduplication
        """
        raise NotImplementedError("YOU IMPLEMENT THIS")
    
    def get_result(self, task_id: str, timeout: float = 5.0) -> dict:
        """
        Get result for a task (blocks until ready or timeout)
        
        PERFORMANCE CRITICAL: This method can become a bottleneck if not
        implemented efficiently.
        
        ASYNC/AWAIT PATTERN:
        Instead of blocking, use async/await:
        ```python
        # Blocking (SLOW):
        result = coordinator.get_result(task_id, timeout=5.0)
        
        # Non-blocking (FAST):
        result = await coordinator.get_result_async(task_id, timeout=5.0)
        ```
        
        RESULT CACHING:
        Implement result cache to avoid recomputation:
        - Use LRU cache with configurable size
        - Cache key = hash(task_type, data, params)
        - Invalidate on timeout or manual clear
        
        TIMEOUT HANDLING:
        - Implement exponential backoff for retries
        - Don't use busy-wait loops (use events/futures)
        - Consider partial results for progressive rendering
        
        Returns:
            dict: {
                "task_id": str,
                "result": bytes,
                "success": bool,
                "processing_time_ms": float
            }
        
        TODO: Wait for result from peer (use asyncio.Event, not busy-wait)
        TODO: Handle timeout gracefully
        TODO: Handle peer failure and retry on different peer
        TODO: Implement result caching
        TODO: Add telemetry for performance monitoring
        """
        raise NotImplementedError("YOU IMPLEMENT THIS")
    
    def handle_peer_failure(self, peer_id: str):
        """
        Called when a peer disconnects or times out
        
        TODO: Remove peer from pool
        TODO: Reassign pending tasks to other peers
        """
        raise NotImplementedError("YOU IMPLEMENT THIS")


# EXAMPLE USAGE (you write the actual code):
"""
coordinator = Coordinator(listen_port=8765)
coordinator.start()  # Blocking - runs forever
"""
