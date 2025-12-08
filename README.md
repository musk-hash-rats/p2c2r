# P2C2R - Peer-to-Cloud-to-Renter

**Community-Powered Gaming: Gamers Helping Gamers** ❤️

> *"A way for the community to help out less fortunate gamers."*

Play AAA games on a potato laptop. Your community shares their idle GPU/CPU cycles so you can game. No expensive hardware needed.

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│ 👥 COMMUNITY    │         │ 💻 CLOUD VM     │         │ 👤 GAMER        │
│ (Helpers)       │────────▶│ (Orchestrator)  │◀────────│ (Player)        │
│                 │         │                 │         │                 │
│ • Share idle PC │ INTERNET│ • Game server   │ INTERNET│ • Potato laptop │
│ • Run micro-tasks│        │ • Validates all │         │ • Plays AAA games│
│ • Help others   │         │ • Ensures fair  │         │ • Pays $0.01/hr │
│ • Earn $0.15/h  │         │ • Port 8765     │         │ • 98% savings!  │
└─────────────────┘         └─────────────────┘         └─────────────────┘
```

## 💡 The Vision

**The Problem**: Gaming PCs cost $2000+. Cloud gaming costs $20/month. Many gamers can't afford either.

**The Solution**: Community members share their idle compute. A 16-year-old plays Cyberpunk 2077 on a 2015 laptop, powered by helpers' idle GPUs around the world.

**How It Works**:
1. **Gamer** starts a cloud VM that hosts the game session (authoritative server)
2. **VM** breaks work into micro-tasks: physics, AI, rendering, compression
3. **Community helpers** run sandboxed tasks (they never see the full game)
4. **VM** validates all results and assembles the final game state
5. **Gamer** sees smooth gameplay on cheap hardware

**Read the full vision**: [docs/THE_VISION.md](docs/THE_VISION.md) ❤️

## 🚀 Quick Start

### Single Machine Testing
```bash
# Terminal 1: Start the network
./run_network.sh

# Terminal 2: Test it
python3 tools/testing/test_quick.py
```

### Internet Deployment
See [`multi_device_demo/README.md`](multi_device_demo/README.md) for:
- Testing with ngrok (5 minutes, free)
- Deploying to AWS/DigitalOcean (production)
- Full distributed network setup

## 📚 Documentation

- **[The Vision](docs/THE_VISION.md)** ❤️ - Why we're building this (read this first!)
- **[Quick Start Guide](docs/guides/QUICKSTART.md)** - Get running in 5 minutes
- **[Multi-Device Setup](multi_device_demo/README.md)** - Internet deployment
- **[Internet Deployment](multi_device_demo/INTERNET_DEPLOYMENT.md)** - Production guide
- **[Project Structure](docs/PROJECT_STRUCTURE.md)** - How files are organized
- **[Legal Compliance](docs/LEGAL_COMPLIANCE.md)** - Open source policy

## 🏗️ Project Structure

```
P2c2gPOC/
├── network/               # Core networking code
│   ├── peer.py           # Contributor node
│   ├── cloud.py          # Coordinator
│   ├── renter.py         # Gamer client
│   └── task_executors.py # 9 real task algorithms
├── multi_device_demo/     # Internet deployment
│   ├── run_cloud.py      # Start cloud server
│   ├── run_peer.py       # Start contributor
│   └── run_gamer.py      # Start gamer
├── tools/                 # Utilities
│   ├── testing/          # Test scripts
│   └── monitoring/       # Status checkers
└── docs/                  # Documentation
```

## ✅ Current Status

**Phase 1: Proof of Concept** ✓ (Complete!)
- ✅ Real task execution (9 algorithms: AI, ray tracing, physics)
- ✅ WebSocket-based networking (internet-ready)
- ✅ SQLite storage for tasks/results
- ✅ Failover & retry logic
- ✅ Web monitoring dashboard
- ✅ Distributed computing model
- ✅ 100% open source (MIT/BSD/Apache 2.0)

**Phase 2: Game Integration** 🚧 (Next!)
- [ ] Sandboxed task execution (security)
- [ ] Result validation (prevent cheating)
- [ ] Simple game demo (Minecraft-like)
- [ ] VM orchestration (authoritative server)

**Phase 3: Community Platform** 🔮 (Future)
- [ ] Peer discovery & reputation
- [ ] Payment integration (Stripe, crypto)
- [ ] Dashboard for gamers & helpers
- [ ] SDK for game developers

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Quick functionality test
python3 tools/testing/test_quick.py

# Check system status
python3 tools/monitoring/check_status.py
```

## 📖 Real-World Example

**Meet Alex** (16, can't afford gaming PC):
- Launches Cyberpunk 2077 on P2C2R
- Cloud VM hosts the game session ($0.01/hour)
- Community helpers run physics, AI, rendering tasks
- Alex's 2018 laptop just handles display
- **Plays smooth 60fps on a potato!** 🎉

**Meet Sarah** (28, software engineer):
- Has gaming PC with RTX 4080
- At work 9-5, PC sits idle
- Donates compute to P2C2R community
- Helps 10-20 gamers while she's at work
- Earns $1.20/day OR donates to help kids game ❤️

**The Impact**:
- Alex saves $1980 (no gaming PC needed)
- Sarah's idle hardware helps others
- Community wins together 🎉

## 🔐 Legal

All dependencies are open source (MIT, BSD, Apache 2.0).  
See [LEGAL_COMPLIANCE.md](docs/LEGAL_COMPLIANCE.md) for details.

## 📝 License

MIT License - see [LICENSE](LICENSE) file

---

**Status**: Working prototype ✓  
**Next**: Deploy to internet with ngrok or AWS
