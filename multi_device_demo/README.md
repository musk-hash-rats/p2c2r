# 🌐 Multi-Device P2C2R Demo - Community Gaming

## 💡 The Vision

> *"A way for the community to help out less fortunate gamers."*

This demonstrates **community-powered gaming**: helpers share their idle GPUs so kids can play AAA games on cheap laptops.

**Read the full vision**: [../docs/THE_VISION.md](../docs/THE_VISION.md) ❤️

## The Three Components

This is a **distributed network** across the internet:

1. **COMMUNITY HELPERS (Peers)**: Anyone, anywhere with idle GPU/CPU to share
2. **CLOUD VM (Coordinator)**: Game server on public internet - the "authoritative boss"
3. **GAMERS (Players)**: Kids/people anywhere who want to play games on cheap hardware

## How It Works (Simple)

```
🎮 Gamer starts game → 💻 Cloud VM hosts session → 👥 Community runs micro-tasks
                                   ↓
                        VM validates results & ensures fairness
                                   ↓
                        🎮 Gamer sees smooth gameplay on potato laptop!
```

**The Magic:**
- **VM is authoritative**: It's the official game server, handles persistence, prevents cheating
- **Helpers run sandboxed tasks**: Physics, AI, rendering - but never see full game
- **VM validates everything**: Results checked before merging into game state
- **Failover built-in**: If helpers drop, VM falls back to cloud compute

**Why This Matters:**
- 16-year-old plays Cyberpunk 2077 on 2015 laptop
- Community helper's idle GPU makes it possible
- 98% cheaper than buying gaming PC ($0.01/hr vs $2000 upfront)
- Gamers helping gamers ❤️

## Prerequisites

### All Devices Need:
- Python 3.8+
- `websockets` package: `pip3 install websockets`
- Internet connection

### Device 2 (Cloud Server) Needs:
- **Public IP or domain name** (e.g., AWS, DigitalOcean, your own server)
- **Port 8765 open to internet** (firewall/router configured)
- OR use **ngrok** for testing without public IP (see below)

## Quick Setup

### Option A: You Have a Public Server (AWS, DigitalOcean, etc.)

**1. Get your server's public IP or domain:**
```bash
# On your cloud server
curl ifconfig.me
# Output example: 203.0.113.42

# Or use domain: p2c2r.example.com
```

**2. Open port 8765:**
```bash
# AWS: Configure security group to allow TCP 8765
# DigitalOcean: Configure firewall
# Your server: sudo ufw allow 8765
```

### Option B: Testing Without Public Server (Use ngrok)

**If you don't have a public server yet, use ngrok for testing:**

```bash
# 1. Install ngrok (free): https://ngrok.com/download

# 2. On Device 2, start the cloud:
python3 run_cloud.py

# 3. In another terminal on Device 2, expose it:
ngrok tcp 8765

# Output will show:
# Forwarding: tcp://0.tcp.ngrok.io:12345 -> localhost:8765

# 4. Use the ngrok address on other devices:
# python3 run_peer.py --cloud-ip 0.tcp.ngrok.io --cloud-port 12345
```

### 2. Start on Each Device

**Device 2 (Cloud - Your Server):**
```bash
cd multi_device_demo
python3 run_cloud.py
# Server now listening on 0.0.0.0:8765
```

**Device 1 (Peer - Anywhere in the World):**
```bash
cd multi_device_demo
python3 run_peer.py --cloud-ip p2c2r.example.com
# Or: python3 run_peer.py --cloud-ip 203.0.113.42
# Or with ngrok: python3 run_peer.py --cloud-ip 0.tcp.ngrok.io --cloud-port 12345
```

**Device 3 (Gamer - Anywhere in the World):**
```bash
cd multi_device_demo
python3 run_gamer.py --cloud-ip p2c2r.example.com
# Or: python3 run_gamer.py --cloud-ip 203.0.113.42
# Or with ngrok: python3 run_gamer.py --cloud-ip 0.tcp.ngrok.io --cloud-port 12345
```

## What You'll See

### Device 1 (Peer) Output:
```
💻 P2C2R PEER NODE
==================
🔌 Connecting to cloud at 192.168.1.100:8765...
✅ Connected! Ready to contribute compute.
💰 Earning rate: $0.15/hour

⚡ Received task: rt_reflections
   Processing... 
   ✅ Completed in 156ms
   💰 Earned: $0.000065

⚡ Received task: ai_pathfinding
   Processing...
   ✅ Completed in 42ms
   💰 Earned: $0.000018

Total earned: $0.083 (33 minutes uptime)
```

### Device 2 (Cloud) Output:
```
☁️  P2C2R CLOUD COORDINATOR
===========================
🌐 Server started on 0.0.0.0:8765
💾 Database: results.db (storing all computations)

📡 Peer connected: peer_laptop_001 (192.168.1.150)
🎮 Gamer connected: gamer_pc_001 (192.168.1.175)

📥 Task received: rt_reflections from gamer_pc_001
   → Routing to peer_laptop_001
   💾 Stored in database
   
📤 Result ready: rt_reflections (156ms)
   → Sent to gamer_pc_001
   💾 Result stored

Network: 1 peer, 1 gamer, 47 tasks completed
Revenue: $0.50 (coordinator fee: $0.05)
```

### Device 3 (Gamer) Output:
```
🎮 P2C2R GAMER CLIENT
=====================
🔌 Connecting to cloud at 192.168.1.100:8765...
✅ Connected! Ready to offload compute.
💰 Cost rate: $0.01/hour

🎯 Game Demo: Space Shooter with P2C2R
=======================================

[Frame 1] Rendering...
  → Offloading ray tracing (reflections)
  ⏱️  Cloud latency: 168ms
  ✅ Received traced frame
  💰 Cost: $0.000047

[Frame 2] Enemy AI decision...
  → Offloading pathfinding for 5 enemies
  ⏱️  Cloud latency: 55ms
  ✅ Received 5 paths
  💰 Cost: $0.000015

Total cost: $0.023 (2.5 hours gameplay)
Savings vs local GPU: $4.98 (99.5% cheaper!)
```

## The Three Components

### 1. Peer (Contributor) - Device 1

**Purpose:** Provide compute power and earn money

**What it does:**
- Connects to cloud coordinator
- Receives tasks (AI, ray tracing, physics)
- Executes using real algorithms
- Returns results
- Tracks earnings

**Hardware:** Any laptop/desktop with spare CPU/GPU

**Code:** `run_peer.py`

### 2. Cloud (Coordinator + Storage) - Device 2

**Purpose:** Route tasks and store all computations

**What it does:**
- Runs WebSocket server
- Maintains SQLite database of all tasks/results
- Routes incoming tasks to available peers
- Handles failover if peers disconnect
- Stores results for 24 hours (caching)
- Tracks billing for gamers and payments for peers

**Hardware:** Server or desktop with good uptime

**Code:** `run_cloud.py` + `cloud_storage.py`

### 3. Gamer (Renter) - Device 3

**Purpose:** Play games using distributed compute

**What it does:**
- Connects to cloud coordinator
- Submits compute-heavy tasks
- Receives results
- Uses results in game
- Tracks costs

**Hardware:** Gaming PC/laptop

**Code:** `run_gamer.py` + `game_demo.py`

## Advanced: Game Integration Demo

Device 3 includes a **real game demo** that shows P2C2R in action:

```bash
cd multi_device_demo
python3 game_demo.py --cloud-ip 192.168.1.100
```

This runs a Pygame space shooter that:
- Uses P2C2R for enemy AI (pathfinding)
- Offloads ray tracing for weapon effects
- Calculates physics on peer nodes
- Shows real-time cost and latency on screen

## Testing Failover

1. Start all 3 devices
2. On Device 3, submit tasks
3. **Disconnect Device 1** (Ctrl+C)
4. Watch Device 2 re-route tasks to backup peer or queue them
5. **Reconnect Device 1**
6. Watch Device 2 send queued tasks

This proves the network is resilient!

## Cost Comparison (Real World)

**Traditional (Device 3 alone):**
- RTX 4070 GPU: $600 upfront + $50/month electricity
- Runs hot, loud, wears out in 3 years
- Total cost: $2,400 over 3 years

**P2C2R Network:**
- Device 3: No GPU needed ($0 upfront)
- Pay $0.01/hour when gaming (10 hrs/week = $5.20/year)
- Total cost: $15.60 over 3 years

**Savings: $2,384 (99.3% cheaper!)**

## Network Requirements

- **Latency**: < 200ms acceptable (internet latency)
- **Bandwidth**: ~1 Mbps per peer (minimal)
- **Reliability**: Any stable internet connection works
- **Peers can be anywhere**: US, Europe, Asia - doesn't matter!
- **Gamers can be anywhere**: Connect from any country

## Troubleshooting

**Peer/Gamer can't connect to cloud?**
```bash
# 1. Check cloud is accessible from internet
curl http://YOUR_IP:8765
# Should see connection attempt in cloud logs

# 2. Check firewall on cloud server
sudo ufw status  # Linux
sudo ufw allow 8765

# 3. Check router/AWS security group allows port 8765

# 4. Test with ngrok if you don't have public IP yet
```

**High latency over internet?**
- 100-200ms is normal for internet
- Contributors closer to cloud = lower latency
- Consider multiple cloud servers (US, EU, Asia)

**Tasks timing out?**
- Verify peer is actually running
- Check cloud logs for routing errors
- Internet connection stable?
- Try simpler tasks first (ai_npc_dialogue)

**Using ngrok for testing:**
```bash
# Free ngrok account allows testing without public server
# Limitation: Random URL changes each restart
# Production: Get real server with static IP/domain
```

## Files Included

```
multi_device_demo/
├── README.md              (this file)
├── run_peer.py           (Device 1 - contributor)
├── run_cloud.py          (Device 2 - coordinator)
├── run_gamer.py          (Device 3 - renter)
├── cloud_storage.py      (SQLite database for Device 2)
├── game_demo.py          (Real Pygame demo for Device 3)
├── network_config.py     (Shared config)
└── test_network.py       (Validate 3-device setup)
```

## Next Steps

1. **Set up 3 devices** following Quick Setup above
2. **Run basic test** to verify connectivity
3. **Try game demo** to see real-world usage
4. **Check Device 2 database** to see stored computations
5. **Experiment with failover** by disconnecting peers

---

**This is the real "Uber of Game Compute"** - 3 separate physical devices working together to provide distributed gaming compute! 🚀
