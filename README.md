# P2C2G - Peer-to-Cloud-to-Gamer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A distributed computing proof of concept that simulates multiple peers contributing compute resources for cloud gaming sessions.

## 🎮 Overview

P2C2G (Peer-to-Cloud-to-Gamer) demonstrates a distributed computing framework where:

- **Peers**: Contributor nodes execute tasks with varied latency and reliability
- **Coordinator**: Orchestrates task scheduling, handles failovers, and assembles outputs
- **Renter**: End-user (gamer) consuming the distributed cloud session

This PoC uses asyncio to model latency, processing time, and failover scenarios with simulated resource constraints.

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/mushhaskrat/p2c2g.git
cd p2c2g

# Install in development mode
pip install -e .

# Or install from requirements
pip install -r requirements.txt
```

### Running the Demo

```bash
# Run the main proof of concept
python p2c2g_poc.py

# Or use the installed package
python -m p2c2g
```

Expected output will show:
- Task scheduling and peer assignments
- Processing with simulated latencies
- Failover handling when peers fail
- Stream assembly and delivery to renter

## 📁 Project Structure

```
P2c2gPOC/
├── src/
│   └── p2c2g/
│       ├── __init__.py       # Package initialization
│       ├── models.py         # Data models (Task, Result, Telemetry)
│       ├── peer.py           # Peer agent implementation
│       ├── coordinator.py    # Coordinator implementation
│       └── renter.py         # Renter client implementation
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_peer.py
│   ├── test_coordinator.py
│   └── test_renter.py
├── docs/
│   ├── architecture.md       # System architecture
│   ├── api.md               # API documentation
│   └── examples.md          # Usage examples
├── examples/
│   └── custom_demo.py       # Custom demo scripts
├── p2c2g_poc.py             # Main PoC script
├── setup.py                 # Package setup
├── requirements.txt         # Dependencies
├── README.md               # This file
└── LICENSE                 # MIT License
```

## 🔧 Architecture

### Components

1. **PeerAgent**: Simulates a contributor node
   - Processes tasks asynchronously
   - Reports telemetry (CPU, GPU, latency)
   - Has configurable reliability and throughput

2. **Coordinator**: Manages distributed execution
   - Schedules tasks based on peer metrics
   - Handles failover when peers fail
   - Tracks peer reputation
   - Assembles results into final stream

3. **RenterClient**: Represents the end-user
   - Receives processed streams
   - Can send input (placeholder for future)

### Data Flow

```
Renter Input → Coordinator → Task Queue → Peers
                    ↓                        ↓
              Failover Logic          Processing
                    ↓                        ↓
              Result Assembly ← Completed Tasks
                    ↓
              Renter Output
```

## 📚 Usage Examples

### Basic Usage

```python
import asyncio
from p2c2g import Coordinator, PeerAgent, RenterClient, Task

async def main():
    # Create coordinator and renter
    coordinator = Coordinator(max_attempts=3)
    renter = RenterClient("player_1")
    
    # Register peers
    peer1 = PeerAgent("peer_1", base_latency_ms=20, reliability=0.9)
    peer2 = PeerAgent("peer_2", base_latency_ms=30, reliability=0.85)
    coordinator.register_peer(peer1)
    coordinator.register_peer(peer2)
    
    # Create and schedule tasks
    task = Task("job_1", "task_1", b"frame_data", 150, {"gpu_pct": 10})
    await coordinator.schedule_task(task)
    
    # Assemble and deliver
    stream = coordinator.assemble_stream(["task_1"])
    renter.receive_stream(stream)

asyncio.run(main())
```

### Custom Configuration

```python
# Create peer with custom settings
peer = PeerAgent(
    peer_id="high_perf_peer",
    base_latency_ms=10,      # Low latency
    reliability=0.98,         # High reliability
    max_throughput=5          # Can handle 5 parallel tasks
)

# Create coordinator with more retry attempts
coordinator = Coordinator(max_attempts=5)
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=p2c2g tests/

# Run specific test file
pytest tests/test_coordinator.py

# Run with verbose output
pytest -v tests/
```

## 📊 Performance Characteristics

- **Latency**: Simulated 15-45ms base latency per peer
- **Reliability**: Configurable 78-95% success rate
- **Throughput**: 1-3 parallel tasks per peer
- **Failover**: Automatic retry up to 3 attempts (configurable)

## 🛠️ Development

### Code Style

This project follows:
- PEP 8 guidelines
- Type hints for all function signatures
- Docstrings for all classes and public methods
- Functions kept under 50 lines where possible

### Running Linters

```bash
# Check code style
flake8 src/p2c2g tests/

# Type checking
mypy src/p2c2g

# Format code
black src/p2c2g tests/
```

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🗺️ Roadmap

- [ ] Real GPU/CPU resource monitoring
- [ ] Network protocol implementation (gRPC/WebSocket)
- [ ] Actual video frame processing
- [ ] Peer discovery and registration
- [ ] Cryptographic verification
- [ ] Load balancing improvements
- [ ] Monitoring dashboard
- [ ] Docker containerization

## 📧 Contact

**Author**: musk-hash-rats

**Repository**: https://github.com/musk-hash-rats/p2c2r

## 🙏 Acknowledgments

- Inspired by distributed computing frameworks
- Built for educational purposes and proof of concept validation

---

Made with ❤️ for the distributed computing community
