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
        
        Args:
            peer_id: Unique peer identifier
            capabilities: {"cpu_cores": int, "ram_gb": float, "gpu": bool}
        
        Returns:
            bool: True if registered successfully
        
        TODO: Add peer to available pool
        TODO: Track peer capabilities
        """
        raise NotImplementedError("YOU IMPLEMENT THIS")
    
    def submit_task(self, task: dict, requester_id: str) -> str:
        """
        Gamer submits a task that needs processing
        
        Args:
            task: {
                "task_type": str,
                "data": bytes,
                "params": dict,
                "priority": int
            }
            requester_id: ID of the gamer
        
        Returns:
            str: task_id for tracking
        
        TODO: Queue the task
        TODO: Assign to best available peer
        TODO: Return task_id immediately
        """
        raise NotImplementedError("YOU IMPLEMENT THIS")
    
    def get_result(self, task_id: str, timeout: float = 5.0) -> dict:
        """
        Get result for a task (blocks until ready or timeout)
        
        Returns:
            dict: {
                "task_id": str,
                "result": bytes,
                "success": bool,
                "processing_time_ms": float
            }
        
        TODO: Wait for result from peer
        TODO: Handle timeout
        TODO: Handle peer failure and retry
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
