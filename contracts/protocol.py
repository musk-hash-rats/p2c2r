"""
NETWORK PROTOCOL CONTRACT

You implement these message formats however you want.
This is just a suggested structure.

PERFORMANCE CONSIDERATIONS:

MESSAGE FORMAT EFFICIENCY:
1. JSON: Easy to debug, human-readable, but larger size and slower parsing
   - Size: ~500 bytes for typical message
   - Parse time: ~0.5-1ms
   - Best for: Development, debugging, small-scale deployments

2. MessagePack: Binary JSON, faster and smaller
   - Size: ~300 bytes (40% smaller than JSON)
   - Parse time: ~0.1-0.2ms (5x faster than JSON)
   - Best for: Production with moderate scale

3. Protocol Buffers: Strongly typed, very efficient
   - Size: ~150 bytes (70% smaller than JSON)
   - Parse time: ~0.05-0.1ms (10x faster than JSON)
   - Best for: High-performance production systems
   - Requires: .proto schema files and code generation

4. Cap'n Proto / FlatBuffers: Zero-copy serialization
   - Size: Similar to Protobuf
   - Parse time: Near zero (no deserialization needed)
   - Best for: Extreme performance requirements
   - More complex to implement

5. Custom Binary: Maximum control
   - Size: Minimal (only essential data)
   - Parse time: Fastest (direct memory access)
   - Best for: When you need absolute maximum performance
   - Most work to implement and maintain

COMPRESSION:
For large binary data (frames, models), consider compression:
- zlib: Good balance (20-50% size reduction, moderate CPU)
- lz4: Very fast, decent compression (useful for real-time)
- zstd: Excellent compression, still fast (best for most cases)
- brotli: Best compression, slower (good for static data)

BATCHING:
Send multiple messages in one packet to reduce overhead:
- Reduces TCP/WebSocket framing overhead
- Better utilization of network bandwidth
- Trade-off: Increased latency for batched messages

CONNECTION OPTIMIZATION:
- Keep WebSocket connections alive (avoid reconnection overhead)
- Use TCP_NODELAY to disable Nagle's algorithm for low latency
- Consider HTTP/2 or HTTP/3 for multiplexing
- Use connection pooling for multiple coordinators
"""

# MESSAGE FORMAT SUGGESTIONS (you choose JSON, Protobuf, custom binary, etc.)

# 1. PEER REGISTRATION
PEER_REGISTER = {
    "msg_type": "peer_register",
    "peer_id": "peer_laptop_001",
    "capabilities": {
        "cpu_cores": 8,
        "ram_gb": 16.0,
        "gpu": True,
        "gpu_vram_gb": 8.0
    }
}

# 2. PEER REGISTRATION RESPONSE
PEER_REGISTER_RESPONSE = {
    "msg_type": "peer_register_response",
    "success": True,
    "peer_id": "peer_laptop_001"
}

# 3. GAMER REGISTRATION
GAMER_REGISTER = {
    "msg_type": "gamer_register",
    "client_id": "gamer_pc_001"
}

# 4. TASK SUBMISSION (from gamer to coordinator)
# PERFORMANCE NOTE: This is the most frequent message type in the system.
# Optimize for size and serialization speed.
#
# SIZE OPTIMIZATION:
# - Use base64 encoding for binary data (33% overhead but text-safe)
# - Or send binary data separately via binary WebSocket frames (no overhead)
# - Or use shared memory/cache for large data (send reference instead)
#
# For 1920x1080 frame:
# - Raw RGB: 6.2 MB
# - JPEG (quality 85): ~200-500 KB
# - WebP (quality 85): ~150-300 KB (better compression)
# - Reference to cached data: ~32 bytes (hash/ID)
#
TASK_SUBMIT = {
    "msg_type": "task_submit",
    "task_id": "task_12345",
    "task_type": "upscale",  # or "ai", "physics", etc.
    "data": "<base64_encoded_or_url>",  # You choose how to send binary data
    "params": {
        "input_res": [1280, 720],
        "output_res": [1920, 1080],
        "quality": "balanced"
    },
    "requester_id": "gamer_pc_001"
}

# 5. TASK ASSIGNMENT (from coordinator to peer)
TASK_ASSIGN = {
    "msg_type": "task_assign",
    "task_id": "task_12345",
    "task_type": "upscale",
    "data": "<base64_encoded_or_url>",
    "params": {
        "input_res": [1280, 720],
        "output_res": [1920, 1080],
        "quality": "balanced"
    }
}

# 6. TASK RESULT (from peer to coordinator)
TASK_RESULT = {
    "msg_type": "task_result",
    "task_id": "task_12345",
    "peer_id": "peer_laptop_001",
    "success": True,
    "result": "<base64_encoded_or_url>",
    "processing_time_ms": 12.5,
    "error": None  # or error message if success=False
}

# 7. RESULT DELIVERY (from coordinator to gamer)
RESULT_DELIVERY = {
    "msg_type": "result_delivery",
    "task_id": "task_12345",
    "success": True,
    "result": "<base64_encoded_or_url>",
    "processing_time_ms": 12.5,
    "network_latency_ms": 3.2,
    "error": None
}

# 8. HEARTBEAT (from peer to coordinator)
# PERFORMANCE NOTE: Heartbeats should be lightweight and infrequent enough
# to not create network overhead, but frequent enough to detect failures quickly.
#
# HEARTBEAT STRATEGY:
# - Interval: 5-10 seconds (balance between responsiveness and overhead)
# - Use TCP keepalive instead if supported (OS-level, more efficient)
# - Only send when peer is idle (avoid interfering with task execution)
# - Consider adaptive intervals based on network conditions
#
# OVERHEAD CALCULATION:
# - Message size: ~100 bytes
# - Frequency: every 5 seconds
# - Bandwidth per peer: 20 bytes/sec (negligible)
# - 1000 peers: 20 KB/sec (still negligible)
#
HEARTBEAT = {
    "msg_type": "heartbeat",
    "peer_id": "peer_laptop_001",
    "timestamp": 1234567890,
    "load": 0.45,  # 0.0 to 1.0
    "tasks_completed": 157,
    "tasks_failed": 2
}

# 9. TASK TIMEOUT (from coordinator to gamer)
TASK_TIMEOUT = {
    "msg_type": "task_timeout",
    "task_id": "task_12345",
    "error": "Task exceeded 5s timeout"
}

# 10. PEER DISCONNECT (internal coordinator event)
PEER_DISCONNECT = {
    "msg_type": "peer_disconnect",
    "peer_id": "peer_laptop_001",
    "reason": "connection_lost"
}


"""
TRANSPORT OPTIONS (you choose):

Option 1: WebSocket + JSON
- Easy to implement
- Human-readable messages
- Good browser support
- Library: websockets (Python), ws (Node.js)

Option 2: WebSocket + Protocol Buffers
- More efficient (smaller messages)
- Type-safe
- Requires .proto file definitions
- Library: protobuf

Option 3: gRPC
- Built-in request/response patterns
- Streaming support
- More complex setup
- Library: grpcio

Option 4: Raw TCP + Custom Binary
- Maximum control
- Most efficient
- Most work to implement
- Library: socket (Python)

YOU CHOOSE WHAT WORKS BEST FOR YOUR USE CASE
"""
