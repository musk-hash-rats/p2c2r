# P2C2G Implementation Contract

## Overview
This document defines the interfaces and contracts for the P2C2G distributed computing system.
**ALL IMPLEMENTATION DETAILS ARE LEFT TO YOU.**

---

## Core Contracts

### 1. Peer Node Contract

```python
"""
CONTRACT: PeerNode
PURPOSE: Receive tasks, execute them, return results
YOU IMPLEMENT: How tasks are executed, resource management
"""

class PeerNode:
    def __init__(self, peer_id: str, capabilities: dict):
        """
        Args:
            peer_id: Unique identifier for this peer
            capabilities: {"cpu_cores": int, "ram_gb": float, "gpu": bool}
        
        YOU IMPLEMENT: Connection setup, resource allocation
        """
        pass
    
    def connect_to_coordinator(self, coordinator_url: str) -> bool:
        """
        Connect to the central coordinator
        
        Returns:
            bool: True if connected successfully
        
        YOU IMPLEMENT: WebSocket/HTTP/TCP connection logic
        """
        pass
    
    def receive_task(self) -> dict:
        """
        Receive a task from coordinator
        
        Returns:
            dict: {"task_id": str, "task_type": str, "data": bytes, "params": dict}
        
        YOU IMPLEMENT: Message parsing, deserialization
        """
        pass
    
    def execute_task(self, task: dict) -> dict:
        """
        Execute the task using local resources
        
        Args:
            task: Task dictionary from receive_task()
        
        Returns:
            dict: {"task_id": str, "result": bytes, "success": bool, "error": str}
        
        YOU IMPLEMENT: Actual computation (upscaling, AI, physics, whatever)
        """
        pass
    
    def send_result(self, result: dict) -> bool:
        """
        Send result back to coordinator
        
        Returns:
            bool: True if sent successfully
        
        YOU IMPLEMENT: Network transmission, retry logic
        """
        pass
    
    def heartbeat(self) -> None:
        """
        Send periodic heartbeat to coordinator
        
        YOU IMPLEMENT: Keep-alive mechanism, health reporting
        """
        pass
```

---

### 2. Coordinator Contract

```python
"""
CONTRACT: Coordinator
PURPOSE: Distribute tasks to peers, collect results
YOU IMPLEMENT: Load balancing, failover, task scheduling
"""

class Coordinator:
    def __init__(self, listen_port: int):
        """
        Args:
            listen_port: Port to listen for peer/gamer connections
        
        YOU IMPLEMENT: Server setup, connection handling
        """
        pass
    
    def register_peer(self, peer_id: str, capabilities: dict) -> bool:
        """
        Register a new peer that wants to contribute compute
        
        Returns:
            bool: True if registered successfully
        
        YOU IMPLEMENT: Peer pool management, capability tracking
        """
        pass
    
    def submit_task(self, task: dict, requester_id: str) -> str:
        """
        Gamer submits a task that needs processing
        
        Args:
            task: {"task_type": str, "data": bytes, "params": dict, "priority": int}
            requester_id: ID of the gamer requesting work
        
        Returns:
            str: task_id for tracking
        
        YOU IMPLEMENT: Task queuing, priority handling
        """
        pass
    
    def assign_task_to_peer(self, task_id: str) -> str:
        """
        Choose a peer and assign them a task
        
        Returns:
            str: peer_id that was assigned the task
        
        YOU IMPLEMENT: Load balancing algorithm, peer selection
        """
        pass
    
    def collect_result(self, task_id: str, timeout: float = 5.0) -> dict:
        """
        Wait for task result from peer
        
        Returns:
            dict: {"task_id": str, "result": bytes, "success": bool}
        
        YOU IMPLEMENT: Result collection, timeout handling, retry logic
        """
        pass
    
    def handle_peer_failure(self, peer_id: str, task_id: str) -> None:
        """
        Called when a peer fails or times out
        
        YOU IMPLEMENT: Failover logic, task reassignment
        """
        pass
    
    def get_system_stats(self) -> dict:
        """
        Get current system statistics
        
        Returns:
            dict: {
                "active_peers": int,
                "pending_tasks": int,
                "completed_tasks": int,
                "failed_tasks": int
            }
        
        YOU IMPLEMENT: Metrics collection, stat tracking
        """
        pass
```

---

### 3. Gamer Client Contract

```python
"""
CONTRACT: GamerClient
PURPOSE: Submit work to the distributed system, get results back
YOU IMPLEMENT: Frame capture, display, input handling
"""

class GamerClient:
    def __init__(self, client_id: str):
        """
        Args:
            client_id: Unique identifier for this gamer
        
        YOU IMPLEMENT: Client initialization
        """
        pass
    
    def connect_to_coordinator(self, coordinator_url: str) -> bool:
        """
        Connect to the coordinator
        
        Returns:
            bool: True if connected
        
        YOU IMPLEMENT: Connection logic
        """
        pass
    
    def capture_frame(self) -> bytes:
        """
        Capture current game frame from screen
        
        Returns:
            bytes: Raw frame data (e.g., JPEG compressed)
        
        YOU IMPLEMENT: Screen capture, compression
        """
        pass
    
    def submit_frame_for_upscaling(self, frame_data: bytes, target_resolution: tuple) -> str:
        """
        Send frame to be upscaled by distributed peers
        
        Args:
            frame_data: Raw frame bytes
            target_resolution: (width, height) tuple
        
        Returns:
            str: task_id for tracking
        
        YOU IMPLEMENT: Task submission protocol
        """
        pass
    
    def get_upscaled_frame(self, task_id: str, timeout: float = 0.016) -> bytes:
        """
        Get the upscaled frame back (within 1 frame @ 60fps)
        
        Returns:
            bytes: Upscaled frame data
        
        YOU IMPLEMENT: Result retrieval, timeout handling
        """
        pass
    
    def display_frame(self, frame_data: bytes) -> None:
        """
        Display the frame to the user
        
        YOU IMPLEMENT: Display logic, rendering
        """
        pass
```

---

## Task Types Contract

### Frame Upscaling Task

```python
"""
CONTRACT: FrameUpscalingTask
INPUT: Low-res frame + target resolution
OUTPUT: High-res frame
YOU IMPLEMENT: Actual upscaling algorithm
"""

TASK_TYPE = "frame_upscale"

INPUT_FORMAT = {
    "task_type": "frame_upscale",
    "data": bytes,  # JPEG/PNG compressed frame
    "params": {
        "input_width": int,
        "input_height": int,
        "output_width": int,
        "output_height": int,
        "quality": str,  # "fast", "balanced", "quality"
    }
}

OUTPUT_FORMAT = {
    "task_id": str,
    "result": bytes,  # Upscaled frame
    "success": bool,
    "processing_time_ms": float,
    "algorithm_used": str
}

# YOU IMPLEMENT: The actual upscaling logic
# Options: OpenCV, Pillow, ML models (ESRGAN), GPU acceleration, etc.
```

---

## Network Protocol Contract

```
MESSAGE FORMAT (JSON over WebSocket or TCP):

1. PEER_REGISTER
{
    "msg_type": "peer_register",
    "peer_id": "peer_xxx",
    "capabilities": {
        "cpu_cores": 8,
        "ram_gb": 16,
        "gpu": true,
        "gpu_vram_gb": 8
    }
}

2. TASK_ASSIGN
{
    "msg_type": "task_assign",
    "task_id": "task_xxx",
    "task_type": "frame_upscale",
    "data_url": "base64://..." or "s3://..." or inline bytes,
    "params": {...}
}

3. TASK_RESULT
{
    "msg_type": "task_result",
    "task_id": "task_xxx",
    "success": true,
    "result_url": "base64://..." or inline bytes,
    "processing_time_ms": 12.5,
    "peer_id": "peer_xxx"
}

4. HEARTBEAT
{
    "msg_type": "heartbeat",
    "peer_id": "peer_xxx",
    "timestamp": 1234567890,
    "load": 0.45  # 0.0 to 1.0
}

YOU IMPLEMENT: Serialization, deserialization, error handling
```

---

## Data Flow Contract

```
NORMAL FLOW:
1. Gamer captures frame → sends to Coordinator
2. Coordinator queues task → assigns to Peer
3. Peer processes frame → sends result to Coordinator
4. Coordinator sends result → back to Gamer
5. Gamer displays frame

ERROR FLOW:
1. Peer fails or times out
2. Coordinator detects failure (heartbeat or timeout)
3. Coordinator reassigns task to different Peer
4. Maximum 3 retry attempts before giving up

YOU IMPLEMENT: All timing, retry logic, error handling
```

---

## Performance Requirements Contract

```
TARGET METRICS:
- Frame capture: 30-60 FPS (16-33ms per frame)
- Network latency: <10ms coordinator ↔ peer
- Processing time: <50ms per frame (total)
- End-to-end latency: <100ms (capture → process → display)
- Success rate: >95%
- Peer failover time: <50ms

YOU MEASURE AND OPTIMIZE to meet these targets
```

---

## Security Contract

```python
"""
SECURITY REQUIREMENTS:
YOU IMPLEMENT: All authentication, encryption, validation
"""

# 1. Peer Authentication
# - Peers must authenticate before receiving tasks
# - Use API keys, JWT tokens, or similar
# YOU IMPLEMENT

# 2. Data Encryption
# - All network traffic should be encrypted (TLS/SSL)
# - Consider encrypting frame data if sensitive
# YOU IMPLEMENT

# 3. Rate Limiting
# - Prevent DoS attacks
# - Limit tasks per gamer per second
# YOU IMPLEMENT

# 4. Input Validation
# - Validate all incoming messages
# - Reject malformed or malicious data
# YOU IMPLEMENT
```

---

## Deployment Contract

```yaml
# coordinator_config.yml
# YOU CREATE AND MANAGE

coordinator:
  listen_port: 8765
  max_peers: 100
  task_timeout_ms: 5000
  heartbeat_interval_ms: 1000
  log_level: "INFO"
  
database:  # Optional
  type: "redis" or "postgres" or "memory"
  connection_string: "..."
  
monitoring:  # Optional
  enable: true
  prometheus_port: 9090
```

```yaml
# peer_config.yml
# YOU CREATE AND MANAGE

peer:
  peer_id: "auto" or "custom_id"
  coordinator_url: "ws://localhost:8765"
  reconnect_attempts: 5
  task_types: ["frame_upscale"]
  
resources:
  use_gpu: true
  max_concurrent_tasks: 4
  
logging:
  level: "INFO"
  file: "/var/log/peer.log"
```

---

## Testing Contract

```python
"""
TESTS YOU SHOULD WRITE:
"""

# 1. Unit Tests
def test_peer_connects_to_coordinator():
    # Test peer can establish connection
    pass

def test_task_serialization():
    # Test task can be serialized/deserialized
    pass

# 2. Integration Tests
def test_end_to_end_frame_processing():
    # Test: gamer → coordinator → peer → coordinator → gamer
    pass

# 3. Load Tests
def test_100_peers_simultaneous():
    # Test system with 100 peers
    pass

# 4. Failure Tests
def test_peer_failure_and_reassignment():
    # Test coordinator handles peer failures
    pass

# YOU IMPLEMENT ALL TESTS
```

---

## Implementation Priority

**YOU DECIDE THE ORDER, but suggested:**

1. **Phase 1: Basic Infrastructure**
   - Coordinator: Simple server that accepts connections
   - Peer: Simple client that connects to coordinator
   - Message passing: Basic JSON over WebSocket

2. **Phase 2: Task Execution**
   - Implement actual frame upscaling on peer
   - Test with static images first

3. **Phase 3: Gamer Integration**
   - Screen capture
   - Submit → Process → Receive flow

4. **Phase 4: Production Hardening**
   - Error handling
   - Retry logic
   - Monitoring
   - Security

5. **Phase 5: Optimization**
   - GPU acceleration
   - Load balancing
   - Caching

---

## What I'm NOT Telling You

- Which libraries to use (OpenCV? Pillow? ML models?)
- How to implement load balancing (round-robin? weighted? predictive?)
- Which transport (WebSocket? gRPC? raw TCP?)
- How to handle serialization (JSON? Protocol Buffers? MessagePack?)
- Database choice (Redis? PostgreSQL? In-memory?)
- Deployment platform (Docker? Kubernetes? Bare metal?)

**YOU MAKE THESE DECISIONS BASED ON YOUR REQUIREMENTS**

---

## Summary

This is a **CONTRACT**, not an implementation.

**I define:**
- Interfaces (what methods exist)
- Data structures (what data flows where)
- Requirements (what the system must do)

**YOU implement:**
- The actual code
- The algorithms
- The network protocols
- The deployment
- The testing
- The optimization

**This gives you:**
- Clear boundaries
- Freedom to choose technologies
- Flexibility to change implementation
- Testable interfaces

**Good luck. Build it your way.**
