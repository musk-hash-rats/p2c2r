# P2C2R Project Structure

## 📁 Clean Organization

```
P2c2gPOC/
├── 📄 README.md                    # Main project readme
├── 📄 LICENSE                      # MIT License
├── 📄 start.sh                     # Quick start launcher
├── 📄 requirements.txt             # Python dependencies
├── 📄 pyproject.toml               # Python project config
│
├── 📁 network/                     # ⭐ CORE NETWORKING CODE
│   ├── cloud_coordinator.py       # Cloud server coordinator
│   ├── peer.py                    # Contributor/peer node
│   ├── renter.py                  # Gamer/renter client
│   └── task_executors.py         # 9 real task implementations
│
├── 📁 multi_device_demo/          # ⭐ INTERNET DEPLOYMENT
│   ├── README.md                  # Multi-device setup guide
│   ├── BOINC_DEPLOYMENT.md        # Production deployment guide
│   ├── run_cloud.py               # Start cloud server
│   ├── run_peer.py                # Start contributor
│   ├── run_gamer.py               # Start gamer
│   ├── cloud_storage.py           # SQLite storage layer
│   └── p2c2r-cloud.service        # Systemd service file
│
├── 📁 tools/                      # ⭐ UTILITIES
│   ├── testing/                   # Test scripts
│   │   ├── test_quick.py          # Interactive testing menu
│   │   ├── demo_functionality.py  # Automated test suite
│   │   └── test_network.py        # Network tests
│   └── monitoring/                # Monitoring tools
│       ├── check_status.py        # Health checker
│       ├── p2c2r_gui.py          # Tkinter GUI monitor
│       ├── p2c2r_web_gui.py      # Flask web dashboard
│       └── templates/             # Web UI templates
│           └── index.html
│
├── 📁 scripts/                    # Shell scripts
│   ├── run_network.sh            # Network launcher
│   ├── setup.sh                  # Environment setup
│   └── setup_demo.sh             # Demo setup
│
├── 📁 tests/                      # Pytest unit tests
│   ├── test_coordinator.py
│   ├── test_peer.py
│   └── test_renter.py
│
├── 📁 docs/                       # Documentation
│   ├── LEGAL_COMPLIANCE.md       # Open source policy
│   ├── guides/                   # User guides
│   │   ├── QUICKSTART.md
│   │   └── QUICKSTART_DEMO.md
│   └── archive/                  # Old/reference files
│       ├── examples/             # Old example code
│       ├── unity-plugin/         # Unity integration (old)
│       ├── src/                  # Old p2c2g package
│       └── *.md                  # Old documentation
│
└── 📁 .github/                    # GitHub configuration
    └── copilot-instructions.md

```

## 🎯 Key Directories

### `network/` - Core System
The heart of P2C2R. All networking logic, task execution, and coordination.

**Files:**
- `cloud_coordinator.py` - Central coordinator (runs on server)
- `peer.py` - Contributor node (runs on contributor's machine)
- `renter.py` - Gamer client (runs on gamer's machine)
- `task_executors.py` - 9 real algorithms (AI, ray tracing, physics, etc.)

### `multi_device_demo/` - Production Ready
Everything needed to deploy P2C2R over the internet (BOINC-style).

**Files:**
- `README.md` - Complete setup guide
- `BOINC_DEPLOYMENT.md` - AWS/DigitalOcean deployment
- `run_*.py` - Launcher scripts for each component
- `cloud_storage.py` - SQLite database layer

### `tools/` - Development Tools
Testing and monitoring utilities.

**testing/**
- `test_quick.py` - Interactive test menu (quickest way to test)
- `demo_functionality.py` - Automated test suite
- `test_network.py` - Network-specific tests

**monitoring/**
- `check_status.py` - CLI status checker
- `p2c2r_gui.py` - Desktop GUI (Tkinter)
- `p2c2r_web_gui.py` - Web dashboard (Flask)

### `docs/archive/` - Historical Reference
Old code and documentation kept for reference but not actively used.

## 🚀 Quick Access

### To Start the System
```bash
./start.sh
```

### To Test
```bash
python3 tools/testing/test_quick.py
```

### To Monitor
```bash
python3 tools/monitoring/check_status.py
# OR
python3 tools/monitoring/p2c2r_web_gui.py  # Web dashboard
```

### To Deploy
```bash
cd multi_device_demo
# Read BOINC_DEPLOYMENT.md for instructions
```

## 📝 File Count Summary

**Active Files:**
- Core network code: 4 files
- Multi-device deployment: 7 files
- Testing tools: 3 files
- Monitoring tools: 4 files
- Scripts: 3 files
- Documentation: 4 active docs

**Total Active**: ~25 files (clean and focused!)

**Archived**: Everything else moved to `docs/archive/`

## 🗑️ What Was Archived

- Old `src/p2c2g/` package (replaced by `network/`)
- Old `p2c2g_poc.py` (replaced by multi_device_demo)
- Old `examples/` (pygame demos, outdated)
- Old `unity-plugin/` (future work, not current focus)
- Old documentation (10+ markdown files → archived)

## 📊 Before vs After

### Before (Cluttered)
```
Root directory: 12 .md files, 10 .py files, 3 .sh files
Total: 25+ files in root
```

### After (Organized)
```
Root directory: 1 README, 1 start script, config files
Everything else: Organized in subdirectories
Total in root: 6 files
```

**Result**: 75% reduction in root clutter! 🎉

---

**Last Updated**: December 7, 2025
**Status**: Cleaned and organized ✓
