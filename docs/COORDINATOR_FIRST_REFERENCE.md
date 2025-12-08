# Cloud Coordinator First - Quick Reference Card

## 🎯 Question: Should I Start with the Cloud?
**Answer: YES! 100% YES!**

---

## Why Coordinator First?

| Approach | Result |
|----------|--------|
| **Start with Coordinator** ✅ | Can test immediately, defines protocol, everything connects to it |
| Start with Peer ❌ | No coordinator to connect to, need to mock it, protocol undefined |
| Start with Gamer ❌ | Same problems, no backend to submit to |

---

## The 5-Phase Plan

### Phase 1: Basic Server (Days 1-2)
```python
# network/cloud_coordinator.py
- WebSocket server on port 8765
- Accept connections
- Register peers and gamers
- Route messages
```
**Test**: Can you connect with a WebSocket client?

---

### Phase 2: Task Queue (Days 3-4)
```python
# Add to coordinator
- Queue incoming tasks
- Assign to available peers
- Forward results to gamers
```
**Test**: Submit task → assigned to peer → result returned?

---

### Phase 3: Heartbeats (Day 5)
```python
# Add monitoring
- Peers send heartbeat every 5s
- Coordinator checks health every 10s
- Remove dead peers, reassign tasks
```
**Test**: Kill a peer → tasks reassigned?

---

### Phase 4: Test Clients (Week 2)
```python
# test_peer.py - Minimal peer that registers and executes tasks
# test_gamer.py - Minimal gamer that submits tasks
```
**Test**: Full end-to-end flow?

---

### Phase 5: Real Implementation (Weeks 3-4)
```python
# network/peer_node.py - Real peer with task execution
# network/gamer_client.py - Real gamer client API
```
**Test**: Real workload?

---

## Message Protocol (JSON over WebSocket)

### Peer → Coordinator
```json
{"msg_type": "register_peer", "peer_id": "peer_1", "capabilities": {...}}
{"msg_type": "heartbeat", "peer_id": "peer_1"}
{"msg_type": "task_result", "task_id": "123", "result": {...}}
```

### Gamer → Coordinator
```json
{"msg_type": "register_gamer", "gamer_id": "gamer_1"}
{"msg_type": "task_request", "task_id": "123", "task_type": "physics", "data": {...}}
```

### Coordinator → Peer
```json
{"msg_type": "registration_ack", "status": "registered"}
{"msg_type": "task_assignment", "task_id": "123", "task_data": {...}}
```

### Coordinator → Gamer
```json
{"msg_type": "registration_ack", "status": "registered"}
{"msg_type": "task_result", "task_id": "123", "result": {...}}
```

---

## Quick Start Commands

```bash
# 1. Install dependencies
pip install websockets psutil

# 2. Start coordinator
python network/cloud_coordinator.py

# 3. Test connection (in another terminal)
python -c "
import asyncio
import websockets
async def test():
    async with websockets.connect('ws://localhost:8765') as ws:
        print('Connected!')
asyncio.run(test())
"

# 4. Start test peer
python test_peer.py

# 5. Start test gamer
python test_gamer.py
```

---

## Architecture Reminder

```
         ┌─────────────┐
         │   Gamer     │
         └──────┬──────┘
                │ submit task
                ▼
    ┌───────────────────────┐
    │   COORDINATOR         │
    │   (Start Here!)       │
    │                       │
    │  • Registers peers    │
    │  • Queues tasks       │
    │  • Monitors health    │
    │  • Routes results     │
    └───────┬───────┬───────┘
            │       │
      assign task   │
            │       │
            ▼       ▼
    ┌────────┐  ┌────────┐
    │ Peer 1 │  │ Peer 2 │
    │ (GPU)  │  │ (CPU)  │
    └────────┘  └────────┘
```

---

## Key Files to Create

1. **`network/cloud_coordinator.py`** - START HERE!
2. **`test_peer.py`** - Simple test peer
3. **`test_gamer.py`** - Simple test gamer
4. **`network/peer_node.py`** - Real peer implementation
5. **`network/gamer_client.py`** - Real gamer client

---

## Testing Checklist

- [ ] Coordinator starts and listens on port 8765
- [ ] Peer can connect and register
- [ ] Gamer can connect and register
- [ ] Gamer submits task → queued by coordinator
- [ ] Coordinator assigns task to peer
- [ ] Peer executes task and returns result
- [ ] Coordinator forwards result to gamer
- [ ] Gamer receives result
- [ ] Peer sends heartbeats
- [ ] Coordinator detects dead peer
- [ ] Coordinator reassigns task when peer dies

---

## Common Pitfalls to Avoid

❌ **Starting with peer** - You'll have nothing to connect to  
❌ **Overthinking** - Start simple, add features incrementally  
❌ **No testing** - Test each phase before moving on  
❌ **Skipping heartbeats** - You need health monitoring from day 1  
❌ **Forgetting error handling** - Handle disconnects gracefully

---

## Success Metrics

### Week 1 (Coordinator)
✓ Coordinator running  
✓ Accepts connections  
✓ Routes messages  
✓ Queues tasks  
✓ Monitors health

### Week 2 (Testing)
✓ Test peer connects  
✓ Test gamer connects  
✓ End-to-end task flow works  
✓ Failover works

### Week 3-4 (Full System)
✓ Real peer implementation  
✓ Real gamer client  
✓ Multiple task types  
✓ Demo application  

---

## Resources

- **Full Guide**: See `STARTING_GUIDE.md` for complete code templates
- **Contracts**: See `contracts/coordinator.py` for interface definition
- **Architecture**: See `docs/ARCHITECTURE.md` for system design
- **Network Details**: See `network/README.md` for protocol details

---

## Final Checklist

Before you start coding:
- [ ] Read this reference card
- [ ] Skim `STARTING_GUIDE.md` for code templates
- [ ] Review `contracts/coordinator.py` for interface
- [ ] Understand the message protocol above

Then:
- [ ] Create `network/cloud_coordinator.py`
- [ ] Start with minimal WebSocket server
- [ ] Test connection with simple client
- [ ] Add features incrementally
- [ ] Test after each feature

---

## Need Help?

1. Check `STARTING_GUIDE.md` for detailed code
2. Look at `contracts/` for interface definitions
3. Read `docs/ARCHITECTURE.md` for design
4. Ask questions if stuck!

**Remember: Start simple. The coordinator is just a message router. You can make it fancy later.**

**Good luck! 🚀**
