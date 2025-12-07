# P2C2G Documentation

## Table of Contents
- [Architecture Overview](#architecture-overview)
- [Core Components](#core-components)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Deployment](#deployment)

## Architecture Overview

P2C2G (Peer-to-Cloud-to-Gamer) is a distributed computing system that enables multiple peers to contribute compute resources for cloud gaming sessions.

### System Components

```
┌──────────┐         ┌──────────────┐         ┌──────────┐
│  Renter  │◄────────┤ Coordinator  │────────►│  Peer 1  │
│ (Gamer)  │         │   (Broker)   │         │          │
└──────────┘         └──────────────┘         └──────────┘
                            │
                            ├────────►┌──────────┐
                            │         │  Peer 2  │
                            │         └──────────┘
                            │
                            └────────►┌──────────┐
                                      │  Peer N  │
                                      └──────────┘
```

### Data Flow

1. **Renter** initiates a gaming session request
2. **Coordinator** breaks down the workload into tasks
3. **Peers** process assigned tasks with resource constraints
4. **Coordinator** handles failovers and reassignments
5. **Renter** receives assembled output stream

## Core Components

### Peer Agent
Contributor nodes that execute tasks with:
- Configurable latency profiles
- Reliability scores
- Resource constraints (GPU/CPU utilization)
- Thermal throttling simulation

### Coordinator
Central orchestrator that:
- Schedules tasks across available peers
- Monitors peer health via telemetry
- Handles task failovers automatically
- Assembles outputs in correct order
- Maintains peer reputation scores

### Renter Client
End-user interface that:
- Submits workload requests
- Receives processed output streams
- Monitors session quality

## API Reference

### Task Object
```python
Task(
    job_id: str,
    task_id: str,
    payload: bytes,
    deadline_ms: int,
    constraints: Dict[str, int]
)
```

### Result Object
```python
Result(
    job_id: str,
    task_id: str,
    status: str,  # 'success' or 'failure'
    output: bytes,
    duration_ms: int,
    peer_id: str,
    error: Optional[str]
)
```

### Telemetry Object
```python
Telemetry(
    peer_id: str,
    gpu_load: float,
    cpu_load: float,
    latency_ms: int,
    thermal_status: str,
    reliability_score: float
)
```

## Configuration

### Peer Configuration
```python
PeerAgent(
    peer_id="peer_001",
    base_latency_ms=25,       # Network latency to coordinator
    reliability=0.85,          # Success rate (0.0 - 1.0)
    max_throughput=2           # Concurrent task limit
)
```

### Coordinator Configuration
```python
Coordinator(
    max_attempts=3             # Task retry limit
)
```

## Running the PoC

### Basic Usage
```bash
python -m p2c2g
```

### Custom Configuration
```python
from p2c2g import demo_p2c2g
import asyncio

asyncio.run(demo_p2c2g(
    num_peers=10,
    num_frames=50
))
```

## Performance Tuning

### Peer Selection Algorithm
The coordinator scores peers based on:
- Network latency (lower is better)
- Current workload (fewer in-flight tasks is better)
- Reputation score (higher is better)

### Failover Strategy
- Automatic retry on task failure
- Reputation-based peer penalization
- Exponential backoff for repeated failures
- Maximum retry limit enforcement

## Future Enhancements

- Real GPU/CPU resource management
- WebRTC streaming integration
- Distributed ledger for peer incentives
- Advanced scheduling algorithms
- Network partition handling
- Peer discovery mechanisms

## Troubleshooting

### Common Issues

**High failure rate:**
- Adjust peer reliability scores
- Increase max_attempts in Coordinator
- Check network latency settings

**Slow performance:**
- Reduce num_frames or increase num_peers
- Optimize peer throughput settings
- Review task complexity

**Missing frames in output:**
- Check coordinator logs for permanent failures
- Verify task deadlines are realistic
- Review peer capacity settings
