# Performance Issues Summary

Quick reference for the main performance issues identified in P2C2R contract definitions.

## 🔴 Critical Issues

### 1. Blocking `submit_and_wait()` in GamerClient
- **Location**: `contracts/gamer_client.py` line 72-82
- **Issue**: Synchronous blocking prevents concurrent task submission
- **Impact**: 10-100x slowdown for batch operations
- **Solution**: Use async/await pattern instead

**Bad:**
```python
result = gamer.submit_and_wait(task_type, data)  # Blocks entire thread
```

**Good:**
```python
task_id = await gamer.submit_task(task_type, data)
result = await gamer.get_result(task_id)
```

**Best:**
```python
# Pipeline multiple tasks
task_ids = [await gamer.submit_task(t, d) for t, d in tasks]
results = await asyncio.gather(*[gamer.get_result(tid) for tid in task_ids])
```

---

## 🟠 High Priority Issues

### 2. Unrealistic 16ms Timeout
- **Location**: `contracts/gamer_client.py` line 56
- **Issue**: Default timeout of 16ms (60fps) too short for network operations
- **Impact**: Most tasks timeout before completion
- **Solution**: Use adaptive timeouts based on task type

**Problem:**
```python
result = gamer.get_result(task_id, timeout=0.016)  # 16ms - too short!
```

**Solution:**
```python
timeouts = {
    "upscale_fast": 0.1,      # 100ms
    "upscale_quality": 1.0,   # 1 second
    "ai_simple": 0.5,         # 500ms
    "ai_complex": 5.0,        # 5 seconds
}
result = gamer.get_result(task_id, timeout=timeouts[task_type])
```

### 3. No Connection Pooling
- **Location**: All client/peer implementations
- **Issue**: Creating new connections for each task adds overhead
- **Impact**: +100-200ms latency per connection (WebSocket + TLS handshake)
- **Solution**: Maintain persistent connections

**Bad:**
```python
def submit_task(self, task):
    conn = connect(coordinator_url)  # 100-200ms overhead
    conn.send(task)
    result = conn.receive()
    conn.close()
    return result
```

**Good:**
```python
class GamerClient:
    def __init__(self):
        self.connection = None  # Persistent connection
    
    async def connect(self):
        self.connection = await websockets.connect(self.coordinator_url)
    
    async def submit_task(self, task):
        await self.connection.send(task)  # Reuse connection (0ms overhead)
```

---

## 🟡 Medium Priority Issues

### 4. Simple Round-Robin Peer Selection
- **Location**: `contracts/coordinator.py` line 53-73
- **Issue**: Doesn't consider peer capabilities, load, or latency
- **Impact**: 2-5x slower task completion times
- **Solution**: Intelligent peer selection based on multiple factors

**Bad:**
```python
# Round-robin - assigns GPU task to CPU peer
next_peer = peers[current_index % len(peers)]
```

**Good:**
```python
def select_best_peer(self, task):
    # Filter by capabilities
    capable = [p for p in peers if p.can_handle(task)]
    
    # Score by load, latency, performance
    scores = []
    for peer in capable:
        score = (
            peer.performance_history * 0.4 +
            (1 - peer.current_load) * 0.3 +
            (1 / (peer.latency_ms + 1)) * 0.2 +
            peer.task_affinity[task.type] * 0.1
        )
        scores.append((score, peer))
    
    return max(scores, key=lambda x: x[0])[1]
```

### 5. No Result Caching
- **Location**: `contracts/coordinator.py` line 75-91
- **Issue**: Identical tasks recomputed every time
- **Impact**: Wasted compute cycles, higher latency
- **Solution**: Cache results with LRU eviction

**Implementation:**
```python
from functools import lru_cache
import hashlib

class Coordinator:
    def __init__(self):
        self.result_cache = {}
        self.cache_max_size = 1000
    
    def submit_task(self, task):
        # Compute cache key
        cache_key = hashlib.sha256(
            json.dumps({
                "type": task["task_type"],
                "data_hash": hashlib.sha256(task["data"]).hexdigest(),
                "params": task["params"]
            }).encode()
        ).hexdigest()
        
        # Check cache
        if cache_key in self.result_cache:
            return self.result_cache[cache_key]  # Near-zero latency
        
        # Execute and cache
        result = self._execute_task(task)
        self.result_cache[cache_key] = result
        return result
```

### 6. Busy-Wait in get_result()
- **Location**: `contracts/coordinator.py` line 75
- **Issue**: Blocking with busy-wait loop wastes CPU
- **Impact**: High CPU usage, poor scalability
- **Solution**: Use asyncio.Event or futures

**Bad:**
```python
def get_result(self, task_id, timeout):
    start = time.time()
    while time.time() - start < timeout:
        if task_id in self.results:
            return self.results[task_id]
        time.sleep(0.001)  # Busy-wait
    raise TimeoutError()
```

**Good:**
```python
async def get_result(self, task_id, timeout):
    # Use event for efficient waiting
    event = asyncio.Event()
    self.result_events[task_id] = event
    
    try:
        await asyncio.wait_for(event.wait(), timeout)
        return self.results[task_id]
    except asyncio.TimeoutError:
        raise TimeoutError()
```

---

## 🟢 Optimization Opportunities

### 7. No Model/Resource Caching in Peers
- **Location**: `contracts/peer_node.py` line 51-75
- **Issue**: Loading models/resources for each task
- **Impact**: +100-1000ms overhead per task
- **Solution**: Preload and cache resources

**Bad:**
```python
def execute_task(self, task):
    model = load_model(task.type)  # 100-1000ms overhead
    result = model.process(task.data)
    return result
```

**Good:**
```python
class PeerNode:
    def __init__(self):
        # Preload models once
        self.models = {
            "upscale": load_upscale_model(),
            "ai": load_ai_model(),
        }
    
    def execute_task(self, task):
        model = self.models[task.type]  # 0ms overhead
        return model.process(task.data)
```

### 8. Inefficient JSON Protocol
- **Location**: `contracts/protocol.py`
- **Issue**: JSON is verbose and slow to parse
- **Impact**: Larger messages, slower serialization
- **Solution**: Use MessagePack or Protocol Buffers for production

**Comparison:**

| Protocol | Message Size | Parse Time | Complexity |
|----------|--------------|------------|------------|
| JSON | 500 bytes | 0.5-1ms | Low |
| MessagePack | 300 bytes (40% smaller) | 0.1-0.2ms (5x faster) | Low |
| Protobuf | 150 bytes (70% smaller) | 0.05-0.1ms (10x faster) | Medium |

**Recommendation:** Start with JSON for development, migrate to MessagePack for production.

### 9. No Request Batching
- **Location**: `contracts/gamer_client.py` line 39-54
- **Issue**: Sending tasks one-by-one increases overhead
- **Impact**: High latency for many small tasks
- **Solution**: Batch multiple tasks into one message

**Bad:**
```python
# 10 round-trips
for i in range(10):
    await client.submit_task(f"task_{i}", data[i])
```

**Good:**
```python
# 1 round-trip
await client.submit_tasks_batch([
    {"type": "upscale", "data": data[i]} for i in range(10)
])
```

**Performance Impact:** 5-10x improvement for small tasks

### 10. No GPU Acceleration
- **Location**: `contracts/task_types.py` all executors
- **Issue**: CPU-only implementations miss massive speedup
- **Impact**: 10-100x slower than GPU for ML/graphics tasks
- **Solution**: Use GPU when available

**Example:**
```python
import torch

class FrameUpscaler:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = load_model().to(self.device)
    
    def upscale(self, frame):
        with torch.no_grad():
            frame_tensor = torch.from_numpy(frame).to(self.device)
            result = self.model(frame_tensor)
            return result.cpu().numpy()
```

---

## Quick Wins (Implement First)

1. **Add async/await everywhere** - Biggest impact, relatively easy
2. **Use persistent connections** - Eliminates 100-200ms overhead
3. **Implement result caching** - Near-zero latency for repeated tasks
4. **Add adaptive timeouts** - Prevents false failures
5. **Cache models/resources** - Eliminates 100-1000ms per task

## Performance Testing

Run this load test to measure improvements:

```python
import asyncio
import time

async def load_test():
    client = GamerClient("test_client")
    await client.connect()
    
    # Submit 100 tasks
    start = time.time()
    task_ids = [await client.submit_task("upscale", b"data") for _ in range(100)]
    results = await asyncio.gather(*[client.get_result(tid) for tid in task_ids])
    elapsed = time.time() - start
    
    print(f"100 tasks in {elapsed:.2f}s = {100/elapsed:.2f} tasks/sec")

asyncio.run(load_test())
```

**Baseline (without optimizations):** ~10 tasks/sec  
**Target (with optimizations):** >100 tasks/sec

---

## See Also

- [Complete Performance Optimization Guide](PERFORMANCE_OPTIMIZATION_GUIDE.md) - Comprehensive 500+ line guide
- Contract files with detailed performance comments:
  - `contracts/gamer_client.py`
  - `contracts/coordinator.py`
  - `contracts/peer_node.py`
  - `contracts/task_types.py`
  - `contracts/protocol.py`

---

## Summary Table

| Issue | Priority | Impact | Effort | Location |
|-------|----------|--------|--------|----------|
| Blocking submit_and_wait | 🔴 Critical | 10-100x slower | Low | gamer_client.py |
| 16ms timeout | 🟠 High | Most tasks fail | Low | gamer_client.py |
| No connection pooling | 🟠 High | +100-200ms | Medium | All files |
| Simple peer selection | 🟡 Medium | 2-5x slower | Medium | coordinator.py |
| No result caching | 🟡 Medium | Repeated work | Medium | coordinator.py |
| Busy-wait loops | 🟡 Medium | High CPU | Low | coordinator.py |
| No model caching | 🟢 Low | +100-1000ms | Low | peer_node.py |
| JSON protocol | 🟢 Low | Larger/slower | High | protocol.py |
| No batching | 🟢 Low | 5-10x slower | Medium | gamer_client.py |
| No GPU acceleration | 🟢 Low | 10-100x slower | High | task_types.py |

---

**Last Updated:** 2025-12-08  
**Status:** Documented in contracts, ready for implementation
