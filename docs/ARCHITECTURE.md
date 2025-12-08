# P2C2R Technical Architecture

## System Design Based on The Vision

This document explains how P2C2R implements the community gaming vision technically.

---

## Core Principle: VM is Authoritative

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLOUD VM (THE BOSS)                          │
│                                                                 │
│  • Hosts the official game session                             │
│  • Keeps authoritative game state                              │
│  • Handles persistence (save games)                            │
│  • Validates all results from peers                            │
│  • Ensures fairness & prevents cheating                        │
│  • Falls back to cloud compute if peers fail                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
         ▲                           ▲                          ▲
         │                           │                          │
         │                           │                          │
    ┌────┴────┐                 ┌───┴────┐              ┌──────┴──────┐
    │ GAMER   │                 │ PEER 1 │              │   PEER N    │
    │ (Player)│                 │(Helper)│              │  (Helper)   │
    └─────────┘                 └────────┘              └─────────────┘
```

**Key Points:**
- VM is the single source of truth
- Peers are helpers, not authorities
- Gamer's client is lightweight (rendering + input only)
- All game logic lives in VM for security

---

## Task Flow: How Work Gets Done

### 1. Gamer Starts Session

```python
# Gamer's machine
gamer_client.connect(vm_address="p2c2r.example.com:8765")
gamer_client.start_game("cyberpunk_2077")

# VM spins up
vm.load_game_state("save_file_123.json")
vm.initialize_world()
vm.status = "AUTHORITATIVE_SERVER_RUNNING"
```

### 2. VM Breaks Work Into Micro-Tasks

```python
# Every frame (60fps), VM creates tasks
frame = vm.current_frame

tasks = [
    # Physics (can be distributed)
    {
        "type": "physics_step",
        "data": serialize(world.physics_objects),
        "context_free": True  # No game secrets
    },
    
    # AI pathfinding (can be distributed)
    {
        "type": "ai_pathfinding",
        "data": {"start": (100, 50), "end": (200, 150), "grid": grid_data},
        "context_free": True
    },
    
    # Rendering (if gamer has weak GPU)
    {
        "type": "render_frame",
        "data": {"scene": scene_description, "camera": camera_pos},
        "can_fallback_to_peer": True
    },
    
    # Game logic (VM ONLY - never distributed)
    {
        "type": "apply_player_input",
        "handler": vm.internal_only,
        "data": player_inputs
    }
]

vm.distribute_tasks(tasks)
```

### 3. Sandboxed Execution on Peers

**Critical: Peers never see the full game!**

```python
# Peer receives ONLY the micro-task
task = peer.receive_task()  # e.g., physics_step

# Peer doesn't know:
# - What game this is
# - Where in the world these objects are
# - What the player is doing
# - Any game logic or secrets

# Peer just computes
result = peer.execute_sandboxed(task)
# Example: "These 100 spheres moved to these new positions"

peer.send_result(result)
```

**Sandboxing Methods:**
1. **Data Minimization**: Only send what's needed for computation
2. **No Context**: Task has no game world context
3. **Validation Later**: VM checks if result makes sense
4. **Containerization**: Future - run in Docker/WebAssembly sandbox

### 4. VM Validates Results

```python
# VM receives results from peers
for task_id, result in completed_tasks:
    if vm.validate(result, task_id):
        # Sanity checks:
        # - Physics: Do velocities/positions make sense?
        # - AI: Is path actually valid?
        # - Rendering: Is frame not corrupted?
        
        if result.seems_reasonable():
            vm.apply_to_game_state(result)
        else:
            # Peer might be malicious or buggy
            vm.recompute_locally(task_id)
            peer_reputation[result.peer_id] -= 10
    else:
        # Validation failed
        vm.fallback_to_cloud_compute(task_id)
```

**Validation Examples:**

```python
def validate_physics_result(result, expected):
    """Ensure physics result is plausible"""
    for obj in result.objects:
        # Check velocities aren't impossibly high
        if obj.velocity > MAX_REASONABLE_VELOCITY:
            return False
        
        # Check positions haven't teleported
        if distance(obj.pos, expected.last_pos) > MAX_FRAME_MOVEMENT:
            return False
    
    return True

def validate_ai_pathfinding(result, task):
    """Ensure AI path is actually valid"""
    path = result.path
    
    # Check path is continuous
    for i in range(len(path) - 1):
        if not is_adjacent(path[i], path[i+1]):
            return False
    
    # Check path doesn't go through walls
    if any(grid[pos] == WALL for pos in path):
        return False
    
    return True
```

### 5. VM Assembles Final State

```python
# VM combines all validated results
frame_state = {
    "physics": validated_physics_results,
    "ai": validated_ai_results,
    "game_logic": vm_internal_logic_result,  # Never distributed
    "player_state": vm.authoritative_player_state
}

# Send to gamer's client
gamer_client.render(frame_state)
```

### 6. Gamer Sees Magic

```python
# Gamer's lightweight client
def render_frame(frame_state):
    # Just display what VM says is true
    draw_world(frame_state.physics)
    draw_npcs(frame_state.ai)
    draw_player(frame_state.player_state)
    
    # Client doesn't validate or compute
    # It trusts the authoritative VM
```

---

## Security Model

### What Peers CAN'T Do

❌ **See the full game world**
- They only get isolated tasks
- No context about where objects are in the game

❌ **Cheat or modify game state**
- VM validates everything
- Malicious results are rejected

❌ **Access player's data**
- Save files stay on VM
- Player credentials never leave VM

❌ **See other players (in multiplayer)**
- Only get tasks for NPCs/physics
- Player positions handled by VM

### What VM MUST Do

✅ **Validate every result**
```python
if not validate(peer_result):
    fallback_to_cloud_compute()
```

✅ **Rate limit peers**
```python
if peer.failed_validations > 3:
    peer.reputation = "UNTRUSTED"
    peer.banned_until = now + 1_hour
```

✅ **Keep authoritative state**
```python
# VM is source of truth
game_state = vm.state  # Official
peer_results = suggestions  # Just suggestions
```

✅ **Handle failures gracefully**
```python
if peer.timeout() or peer.malicious():
    vm.compute_locally()  # Always have fallback
```

### Example Attack Scenarios

**Attack 1: Malicious Peer Sends Wrong Physics**
```python
# Peer tries to cheat
malicious_result = {
    "player_pos": (999999, 999999),  # Teleport player
    "player_health": 9999             # God mode
}

# VM validation catches it
if not validate_physics(malicious_result):
    log("Peer {} sent invalid physics", peer.id)
    peer.reputation -= 50
    vm.recompute_physics_locally()  # Safe fallback
```

**Attack 2: Peer Tries to Read Game Secrets**
```python
# Peer requests more data
peer.request("give_me_full_game_state")

# VM refuses
vm.response("DENIED - you only get task data")

# Peer only ever receives:
task = {
    "type": "physics",
    "objects": [obj1, obj2, ...]  # No game context
}
```

**Attack 3: Peer Delays Results (Griefing)**
```python
# Peer takes 10 seconds to respond (frame should be 16ms)
vm.timeout_threshold = 200ms

if peer.response_time > timeout_threshold:
    log("Peer {} too slow, falling back", peer.id)
    vm.compute_locally()
    peer.reputation -= 10
```

---

## Failover Strategy

```python
class VM:
    def execute_task(self, task):
        # Try peer first (cheaper)
        try:
            result = self.assign_to_peer(task, timeout=200ms)
            if self.validate(result):
                return result
        except (Timeout, ValidationError):
            pass
        
        # Fallback to cloud compute (more expensive but reliable)
        return self.compute_on_cloud(task)
```

**Failover Levels:**
1. **Peer execution** (cheapest) - Try first
2. **Different peer** (same cost) - If first peer fails
3. **Cloud compute** (more expensive) - If no peers available
4. **VM local** (last resort) - If cloud is down

---

## Current Implementation Status

### ✅ What Works Now (Phase 1)

```
network/cloud_coordinator.py   → VM coordinator (basic)
network/peer.py                → Peer execution
network/renter.py              → Gamer client
network/task_executors.py      → 9 real task types
multi_device_demo/             → Internet deployment
```

**Features:**
- ✅ WebSocket networking (internet-ready)
- ✅ Task distribution
- ✅ Failover logic
- ✅ SQLite storage
- ✅ Multiple task types (AI, physics, ray tracing)

### 🚧 What's Next (Phase 2)

**Need to Add:**
- [ ] **Sandboxing**: Docker/WASM containers for peers
- [ ] **Validation**: Sophisticated result checking
- [ ] **Game Demo**: Simple game (voxel game-like) to prove it works
- [ ] **VM Authority**: Full game server implementation
- [ ] **Security**: API keys, encryption, rate limiting

**Architecture Changes:**
```python
# Current: Basic task execution
cloud.distribute_task(task)
peer.execute(task)
cloud.receive_result(result)

# Future: Full VM authority model
vm.start_game_session()
vm.distribute_sandboxed_task(task)
peer.execute_in_sandbox(task)
vm.validate_and_apply(result)
```

---

## Performance Model

### Latency Budget (60fps = 16ms per frame)

```
Task breakdown for one frame:
├── VM breaks down work: 1ms
├── Network to peer: 20-50ms (internet)
├── Peer computes: 5-10ms
├── Network back to VM: 20-50ms
├── VM validates: 1ms
└── VM assembles: 1ms

Total: ~50-120ms (3-7 frames behind)
```

**Solution: Pipeline Multiple Frames**
```
Frame 1: VM → Peers (physics)
Frame 2: VM → Peers (AI)      | Frame 1: Peers → VM (results)
Frame 3: VM → Peers (render)  | Frame 2: Peers → VM | Frame 1: Display
```

**Result**: 3-frame latency acceptable (50ms), invisible to player

### Cost Model

**Traditional Cloud Gaming:**
- Geforce Now: $20/month = $0.67/hour
- Full cloud VM: $0.50/hour

**P2C2R Model:**
- Gamer pays: $0.01/hour (98% savings!)
- Peers earn: $0.15/hour
- VM cost: Amortized across many gamers

**How it's cheaper:**
- Peers use **idle** hardware (sunk cost)
- VM only does coordination (not full compute)
- Economy of scale (1 VM, 1000 peers)

---

## Roadmap

### Phase 1: POC ✅ (Done!)
- Basic networking
- Task distribution
- Internet deployment

### Phase 2: Game Integration 🚧 (Next 3-6 months)
- Simple game demo
- Sandboxed execution
- Result validation
- VM authority model

### Phase 3: Community Platform 🔮 (6-12 months)
- Peer discovery
- Reputation system
- Payments (Stripe, crypto)
- Dashboard for gamers/helpers

### Phase 4: Real Games 🌟 (12+ months)
- SDK for game developers
- game engine integration
- Partner with indie devs
- Community marketplace

---

**Last Updated**: December 7, 2025  
**Status**: Phase 1 complete, Phase 2 starting  
**Vision**: Make gaming accessible to everyone ❤️
