# Implementation Guidelines: Vibe Coding vs. Precision Engineering

This document clarifies which parts of the P2C2R system can be implemented through "vibe coding" (rapid prototyping with approximate solutions) versus which require precision engineering.

---

## What is "Vibe Coding"?

**Vibe Coding** = Quick implementation focused on getting something working, where:
- Exact algorithms don't matter much
- Performance is "good enough" for now
- You can iterate and optimize later
- The goal is rapid prototyping and validation

**Precision Engineering** = Careful implementation where:
- Correctness is critical
- Performance directly impacts user experience
- Edge cases must be handled properly
- Changes are expensive to make later

---

## ✅ Safe to Vibe Code

### 1. Initial Prototypes and Demos

**What:** First working version to validate the concept

**Why it's safe:**
- You're proving viability, not building production
- Performance isn't critical yet
- You'll rewrite it anyway after learning

**Example:**
```python
# Vibe code is fine for initial demo
class Coordinator:
    def submit_task(self, task):
        # Simple round-robin, no optimization
        peer = self.peers[self.current_index % len(self.peers)]
        self.current_index += 1
        return peer.execute(task)
```

**When to refactor:** After validating the concept works

---

### 2. Configuration and Setup Code

**What:** Installation scripts, configuration parsing, CLI arguments

**Why it's safe:**
- Runs once at startup, not in hot path
- Performance doesn't matter
- Easy to fix if it breaks

**Example:**
```python
# Vibe code is fine for config parsing
def load_config(filename):
    with open(filename) as f:
        # Just get it working, doesn't need to be fast
        return json.load(f)
```

---

### 3. Logging and Debugging Tools

**What:** Print statements, debug logs, monitoring dashboards

**Why it's safe:**
- Not in critical path
- Can be disabled in production
- Clarity > performance

**Example:**
```python
# Vibe code is fine for logging
def execute_task(self, task):
    print(f"Starting task {task.id}")  # Quick and dirty logging
    result = self._do_work(task)
    print(f"Completed task {task.id} in {time.time() - start}s")
    return result
```

---

### 4. Simple Task Executors (Non-Critical)

**What:** Basic implementations of tasks that aren't performance-critical

**Why it's safe:**
- Can optimize later when profiling reveals bottlenecks
- Getting correctness first is more important

**Example:**
```python
# Vibe code is OK for simple pathfinding
def pathfinding(start, goal, obstacles):
    # Simple breadth-first search, not optimized
    queue = [start]
    visited = {start}
    
    while queue:
        current = queue.pop(0)
        if current == goal:
            return reconstruct_path(current)
        
        for neighbor in get_neighbors(current):
            if neighbor not in obstacles and neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    return None
```

**When to optimize:** When profiling shows it's a bottleneck

---

### 5. Error Messages and User-Facing Text

**What:** Error messages, help text, documentation strings

**Why it's safe:**
- Human-readable text doesn't need optimization
- Clarity is more important than perfection

**Example:**
```python
# Vibe code is fine for error messages
if not self.is_connected:
    raise Exception("Not connected to coordinator, try connecting first")
```

---

## ⚠️ Proceed with Caution (Semi-Critical)

### 6. Data Serialization/Deserialization

**What:** Converting between JSON/binary formats

**Why caution needed:**
- Can become bottleneck with large messages
- But easy to swap implementations later

**Vibe code approach:**
```python
# Start with simple JSON (vibe code OK initially)
def serialize(self, data):
    return json.dumps(data).encode()
```

**When to optimize:**
- When profiling shows serialization > 5% of total time
- When message sizes are consistently large (>100KB)

**Optimized approach:**
```python
# Later: Switch to MessagePack for production
import msgpack

def serialize(self, data):
    return msgpack.packb(data)
```

---

### 7. Connection Management

**What:** Establishing and maintaining network connections

**Why caution needed:**
- Connection overhead adds up
- But initial simple approach can work

**Vibe code approach:**
```python
# Start simple (OK for prototype)
def submit_task(self, task):
    conn = self.connect()  # New connection each time
    conn.send(task)
    result = conn.receive()
    conn.close()
    return result
```

**When to optimize:**
- When you have >10 clients submitting tasks
- When latency measurements show connection overhead >20%

---

### 8. Caching Strategies

**What:** Storing computed results for reuse

**Why caution needed:**
- Wrong cache can hurt more than help (stale data)
- But can start without caching and add later

**Vibe code approach:**
```python
# Start without caching (vibe code OK)
def get_result(self, task_id):
    return self._compute_result(task_id)
```

**When to add:**
- When profiling shows repeated identical computations
- When cache hit rate would be >30%

---

## ❌ DO NOT Vibe Code (Precision Required)

### 9. Core Event Loop / Message Dispatcher

**What:** Main async loop that routes all messages

**Why precision needed:**
- Performance-critical path
- Affects all operations
- Hard to fix bugs later

**DON'T do this:**
```python
# BAD: Blocking synchronous loop
def run(self):
    while True:
        message = self.receive_message()  # BLOCKS entire system
        self.handle_message(message)      # BLOCKS other messages
```

**DO this:**
```python
# GOOD: Async non-blocking loop
async def run(self):
    while True:
        message = await self.receive_message()  # Non-blocking
        asyncio.create_task(self.handle_message(message))  # Parallel
```

**Why this matters:**
- One slow message blocks entire system in sync version
- Can't achieve >10 tasks/sec without async
- Very hard to retrofit async later

---

### 10. Task Queue Implementation

**What:** Data structure holding pending tasks

**Why precision needed:**
- Wrong data structure = O(n²) instead of O(log n)
- Performance degrades badly at scale
- Hard to swap later without downtime

**DON'T do this:**
```python
# BAD: List with linear search O(n)
class Coordinator:
    def __init__(self):
        self.tasks = []  # Bad for priority queue
    
    def submit_task(self, task):
        self.tasks.append(task)
    
    def get_next_task(self):
        # O(n) to find highest priority - BAD!
        return max(self.tasks, key=lambda t: t.priority)
```

**DO this:**
```python
# GOOD: Priority queue with O(log n) operations
import heapq

class Coordinator:
    def __init__(self):
        self.tasks = []  # heapq
        self.task_index = 0
    
    def submit_task(self, task):
        heapq.heappush(self.tasks, (task.priority, self.task_index, task))
        self.task_index += 1
    
    def get_next_task(self):
        return heapq.heappop(self.tasks)[2] if self.tasks else None
```

**Why this matters:**
- 100 tasks: 10x slower with wrong structure
- 1000 tasks: 100x slower
- 10000 tasks: System becomes unusable

---

### 11. Peer Selection Algorithm

**What:** Choosing which peer handles a task

**Why precision needed:**
- Directly impacts task completion time
- Bad selection = 10x slower tasks
- Affects entire system throughput

**DON'T do this:**
```python
# BAD: Random selection
def select_peer(self, task):
    return random.choice(self.peers)  # Might pick wrong peer!
```

**Why this is bad:**
- Assigns GPU task to CPU-only peer → 100x slower
- Assigns task to overloaded peer → queueing delay
- Assigns task to high-latency peer → poor UX

**DO this:**
```python
# GOOD: Intelligent selection
def select_peer(self, task):
    # 1. Filter by capabilities
    capable = [p for p in self.peers if p.can_handle(task)]
    if not capable:
        raise NoCapablePeerError()
    
    # 2. Score by load, performance, latency
    def score(peer):
        return (
            peer.success_rate * 0.4 +
            (1 - peer.current_load) * 0.3 +
            (1 / (peer.avg_latency_ms + 1)) * 0.3
        )
    
    # 3. Return best peer
    return max(capable, key=score)
```

---

### 12. Timeout Handling

**What:** Deciding when to give up on a task

**Why precision needed:**
- Too short: Tasks fail unnecessarily
- Too long: System hangs on dead peers
- Directly affects reliability

**DON'T do this:**
```python
# BAD: Fixed timeout for all tasks
TIMEOUT = 5.0  # Same for everything - BAD!

def get_result(self, task_id):
    return self.wait_for_result(task_id, timeout=TIMEOUT)
```

**Why this is bad:**
- Simple tasks (50ms) wait unnecessarily for 5s
- Complex tasks (10s) timeout prematurely
- No adaptation to network conditions

**DO this:**
```python
# GOOD: Adaptive timeouts
class Coordinator:
    def __init__(self):
        self.task_timeouts = {
            "upscale_fast": 0.2,
            "upscale_quality": 2.0,
            "ai_simple": 0.5,
            "ai_complex": 10.0,
            "physics": 0.1,
        }
        self.peer_latencies = {}  # Track per-peer latency
    
    def get_timeout(self, task, peer):
        base_timeout = self.task_timeouts.get(task.type, 5.0)
        peer_factor = self.peer_latencies.get(peer.id, 1.0)
        return base_timeout * peer_factor
```

---

### 13. Resource Cleanup

**What:** Closing connections, freeing memory, releasing locks

**Why precision needed:**
- Resource leaks accumulate over time
- Crashes system after hours/days of operation
- Very hard to debug in production

**DON'T do this:**
```python
# BAD: No cleanup
def execute_task(self, task):
    model = load_model(task.type)  # Never freed!
    return model.process(task.data)
```

**DO this:**
```python
# GOOD: Proper cleanup
def execute_task(self, task):
    model = None
    try:
        model = load_model(task.type)
        return model.process(task.data)
    finally:
        if model:
            model.cleanup()  # Always cleanup
```

**Or use context managers:**
```python
# BETTER: Context manager ensures cleanup
def execute_task(self, task):
    with load_model(task.type) as model:
        return model.process(task.data)
```

---

### 14. Cryptographic/Security Code

**What:** Authentication, encryption, signature verification

**Why precision needed:**
- Security bugs are catastrophic
- Can't be "approximately right"
- Must use established libraries

**DON'T do this:**
```python
# BAD: Rolling your own crypto
def encrypt(self, data, key):
    # Custom encryption - DON'T DO THIS!
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])
```

**DO this:**
```python
# GOOD: Use established libraries
from cryptography.fernet import Fernet

def encrypt(self, data, key):
    f = Fernet(key)
    return f.encrypt(data)
```

---

### 15. Concurrency Primitives

**What:** Locks, semaphores, atomic operations

**Why precision needed:**
- Race conditions cause rare, hard-to-debug crashes
- Wrong synchronization = data corruption
- Nearly impossible to test exhaustively

**DON'T do this:**
```python
# BAD: No synchronization
class Coordinator:
    def __init__(self):
        self.active_tasks = 0
    
    def submit_task(self, task):
        self.active_tasks += 1  # RACE CONDITION!
        # ... assign task ...
    
    def complete_task(self, task):
        self.active_tasks -= 1  # RACE CONDITION!
```

**DO this:**
```python
# GOOD: Proper synchronization
import asyncio

class Coordinator:
    def __init__(self):
        self.active_tasks = 0
        self.lock = asyncio.Lock()
    
    async def submit_task(self, task):
        async with self.lock:
            self.active_tasks += 1
        # ... assign task ...
    
    async def complete_task(self, task):
        async with self.lock:
            self.active_tasks -= 1
```

---

## Code Style and Formatting Rules

### Use PEP 8 for Clarity and Readability

**PEP 8 is NOT optional** - it ensures code is readable by everyone.

#### Key PEP 8 Rules:

**1. Indentation: 4 spaces (not tabs)**
```python
# GOOD
def my_function():
    if condition:
        do_something()
    
# BAD
def my_function():
  if condition:  # 2 spaces - wrong
      do_something()  # mixing - VERY bad
```

**2. Line length: Max 88 characters (Black formatter standard)**
```python
# GOOD
result = coordinator.submit_task(
    task_type="upscale",
    data=frame_data,
    params={"quality": "high"}
)

# BAD (too long)
result = coordinator.submit_task(task_type="upscale", data=frame_data, params={"quality": "high", "resolution": [1920, 1080]})
```

**3. Imports: Standard library, then third-party, then local**
```python
# GOOD
import asyncio
import json
from typing import Dict, List

import websockets
from PIL import Image

from p2c2r.coordinator import Coordinator
from p2c2r.peer import Peer

# BAD (mixed order)
from p2c2r.coordinator import Coordinator
import json
import websockets
```

**4. Naming conventions:**
```python
# Classes: PascalCase
class TaskExecutor:
    pass

# Functions and variables: snake_case
def execute_task(task_data: dict) -> dict:
    result_data = process(task_data)
    return result_data

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 5.0
```

**5. Whitespace:**
```python
# GOOD
result = calculate(a, b)
items = [1, 2, 3]
data = {"key": "value"}

# BAD
result=calculate(a,b)  # No spaces around =, after commas
items = [1,2,3]  # No spaces after commas
data = { "key":"value" }  # Extra spaces in dict
```

**6. Type hints (required for public APIs):**
```python
# GOOD
def submit_task(
    self,
    task_type: str,
    data: bytes,
    params: dict = None
) -> str:
    pass

# BAD (no type hints)
def submit_task(self, task_type, data, params=None):
    pass
```

**7. Docstrings (required for all public functions/classes):**
```python
# GOOD
def execute_task(self, task: dict) -> dict:
    """
    Execute a task using local resources.
    
    Args:
        task: Task data including type, input, and parameters
    
    Returns:
        dict: Result with output and success status
    """
    pass

# BAD (no docstring)
def execute_task(self, task):
    pass
```

### Tools to Enforce PEP 8:

**Black**: Auto-formatter (opinionated, consistent)
```bash
pip install black
black contracts/ src/
```

**Flake8**: Linter (catches violations)
```bash
pip install flake8
flake8 contracts/ src/
```

**mypy**: Type checker
```bash
pip install mypy
mypy contracts/ src/
```

**Pre-commit hook** (recommended):
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.0.0
    hooks:
      - id: black
  
  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

---

## Decision Framework

When implementing a feature, ask:

### 1. Is this in the hot path?
- **Yes** → Precision required
- **No** → Vibe code OK

### 2. How often does it run?
- **Every task (1000x/sec)** → Precision required
- **Once per connection** → Caution
- **Once at startup** → Vibe code OK

### 3. Can I easily replace it later?
- **Yes (modular, well-defined interface)** → Vibe code OK
- **No (deeply integrated)** → Precision required

### 4. Does it affect correctness?
- **Yes (data loss, crashes, corruption)** → Precision required
- **No (just slower/less optimal)** → Vibe code OK

### 5. Does it affect security?
- **Yes** → Precision required, use libraries
- **No** → Can vibe code

---

## Summary Table

| Component | Vibe Code OK? | Why |
|-----------|---------------|-----|
| Initial prototype | ✅ Yes | Learning phase, will rewrite |
| Config/setup | ✅ Yes | Not in hot path |
| Logging | ✅ Yes | Debug tool, not critical |
| Simple tasks | ✅ Yes | Can optimize later |
| Error messages | ✅ Yes | Human readability > performance |
| Serialization | ⚠️ Caution | Easy to swap, but can bottleneck |
| Connections | ⚠️ Caution | Start simple, optimize later |
| Caching | ⚠️ Caution | Add when profiling shows need |
| Event loop | ❌ No | Core infrastructure, must be async |
| Task queue | ❌ No | Wrong choice = O(n²) |
| Peer selection | ❌ No | Directly impacts performance |
| Timeouts | ❌ No | Affects reliability |
| Resource cleanup | ❌ No | Leaks cause crashes |
| Security/crypto | ❌ No | Must be correct, use libraries |
| Concurrency | ❌ No | Race conditions hard to debug |

---

## When to Refactor Vibe Code

Signs it's time to move from vibe code to production code:

1. **Performance profiling** shows it's a bottleneck (>5% of total time)
2. **Scale testing** reveals it doesn't handle load (>100 concurrent operations)
3. **Error rate** is high (>1% failure rate)
4. **Code review** identifies correctness issues
5. **You're shipping to users** - refactor before production

---

## Final Advice

**Start with vibe code for:**
- Proving concepts
- Rapid prototyping
- Non-critical features
- Tools and scripts

**Use precision engineering for:**
- Core event loops
- Data structures in hot path
- Algorithms with performance implications
- Security and concurrency

**Always follow PEP 8:**
- Makes code readable by everyone
- Prevents bugs from formatting issues
- Standard across Python community
- Use Black formatter for automatic compliance

**Remember:** Premature optimization is bad, but premature vibe coding of critical components is worse. Choose wisely!
