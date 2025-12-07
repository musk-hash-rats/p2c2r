# P2C2R Space Shooter Demo

A simple space shooter that demonstrates P2C2R's "Uber for Compute" model.

## What This Demonstrates

This game shows how P2C2R works like **Uber for GPU compute**:

- 🎮 **Player** = Rider (needs compute)
- 🌐 **P2C2R Network** = Uber platform (connects supply/demand)
- 💻 **Peers** = Drivers (provides compute from idle GPUs)

## The "Uber" Model in Action

```
┌──────────────────┐
│  Game Needs AI   │ "I need enemy AI computed!"
│  (Your Game)     │ 
└────────┬─────────┘
         │
         │ Request via P2C2R
         ▼
┌──────────────────────────┐
│   P2C2R Coordinator      │ "Let me find you a peer..."
│   (Like Uber dispatch)   │ Routes task to best peer
└────────┬─────────────────┘
         │
         │ Assigns task
         ▼
┌──────────────────┐
│  Idle GPU Peer   │ "I'll compute that for you!"
│  (Like Uber car) │ Returns AI decisions
└────────┬─────────┘
         │
         │ Result
         ▼
┌──────────────────┐
│  Game Gets AI    │ Enemies move intelligently
│  (Fast & Cheap)  │ $7.50/mo instead of $1200 GPU
└──────────────────┘
```

## How It Works

### With P2C2R (Uber Mode) ✅
```csharp
// Game requests AI from peer network
var result = await P2C2RClient.Instance.SubmitAITask(
    "enemy_behavior",
    gameState
);

// Peer computes AI and returns result
// You pay only for what you use (like Uber)
```

### Without P2C2R (Own GPU) ⚠️
```csharp
// Game computes AI locally
ComputeEnemyAI(); // Requires RTX 4080 ($1200)

// You own the hardware (like owning a car)
```

## Cost Comparison

| Approach | Upfront Cost | Monthly Cost | 2 Year Total |
|----------|--------------|--------------|--------------|
| **Local GPU** | $1,200 | $50 (electricity) | $2,400 |
| **P2C2R Network** | $0 | $7.50 | $180 |
| **Savings** | $1,200 | $42.50 | $2,220 (92%) |

Just like Uber vs owning a car! 🚗→🚕

## Setup

1. **Start P2C2R Network:**
```bash
cd /path/to/P2c2gPOC
./run_network.sh
```

2. **Open in Unity:**
```bash
# Open this folder in Unity Hub
# Unity 2020.3 or later required
```

3. **Add P2C2R Plugin:**
```
Window > Package Manager > + > Add from disk
Select: P2c2gPOC/unity-plugin/package.json
```

4. **Run the Demo:**
- Open scene (or create new scene)
- Add `SpaceShooter.cs` to an empty GameObject
- Add `P2C2RDemo.cs` to another GameObject
- Press Play!

## What to Look For

### Performance Stats (Top Left)
```
Score: 150
Enemies: 7/10
Killed: 5
P2C2R Latency: 0.045s
AI: Peer Network (Uber Mode) ✓
```

### P2C2R Status Box
```
P2C2R Status
━━━━━━━━━━━━━━━━
Status: ✓ Connected
Tasks Sent: 23
Tasks Completed: 23
Avg Latency: 0.048s
Pending: 0
```

### The "Uber" Advantage Box
```
The "Uber" Advantage
━━━━━━━━━━━━━━━━━━━━
Local GPU: $1200 + $50/mo
P2C2R Network: $7.50/mo
━━━━━━━━━━━━━━━━
Savings: $1,250 (94% cheaper!)
```

## Toggle P2C2R On/Off

In the Inspector for `SpaceShooter`:
- ✅ **Use P2C2R** = Uber mode (peer network)
- ❌ **Use P2C2R** = Own GPU mode (local compute)

Watch the latency and cost difference!

## Key Files

- `Assets/Scripts/SpaceShooter.cs` - Main game with P2C2R AI
- `Assets/Scripts/P2C2RDemo.cs` - Stats and comparison UI
- `Packages/com.p2c2r.compute/` - P2C2R plugin (symlink)

## The Business Model

### Three-Sided Marketplace

1. **Gamers (Demand)**
   - Pay $7.50/month for compute access
   - Save 90%+ vs buying GPU
   - Get AAA features on mid-tier hardware

2. **GPU Owners (Supply)**
   - Earn $8-16/month from idle GPU
   - Passive income while not gaming
   - Free gaming with compute credits

3. **P2C2R (Platform)**
   - Takes 25% transaction fee
   - Handles routing, billing, trust
   - Scales automatically

### Why It Works

Just like Uber:
- ✅ **Network effects** - More users = better service
- ✅ **Asset utilization** - Use idle resources (80% of GPUs idle)
- ✅ **Lower costs** - No infrastructure, use peer network
- ✅ **Win-win-win** - All parties benefit

## Scalable & Secure Infrastructure

See [INFRASTRUCTURE.md](../docs/INFRASTRUCTURE.md) for cloud architecture.

**Spoiler:** WebSocket over TLS, not QUIC. Battle-tested protocols. ✅

---

**Questions?**

Open an issue: https://github.com/musk-hash-rats/p2c2r/issues
