#!/usr/bin/env python3
"""
Basic P2C2G Example
------------------
Minimal example showing basic usage of P2C2G components.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from p2c2g.models import Task
from p2c2g.peer import PeerAgent
from p2c2g.coordinator import Coordinator
from p2c2g.renter import RenterClient


async def basic_example():
    """Simple P2C2G workflow with 3 peers and 10 tasks."""
    
    # Step 1: Create coordinator
    coordinator = Coordinator(max_attempts=3)
    
    # Step 2: Create and register peers
    peer1 = PeerAgent("peer_1", base_latency_ms=20, reliability=0.90)
    peer2 = PeerAgent("peer_2", base_latency_ms=30, reliability=0.85)
    peer3 = PeerAgent("peer_3", base_latency_ms=40, reliability=0.80)
    
    coordinator.register_peer(peer1)
    coordinator.register_peer(peer2)
    coordinator.register_peer(peer3)
    
    # Step 3: Create renter
    renter = RenterClient("user_001")
    
    # Step 4: Create tasks
    tasks = []
    for i in range(10):
        task = Task(
            job_id="job_001",
            task_id=f"task_{i:03d}",
            payload=f"data_{i}".encode(),
            deadline_ms=100,
            constraints={"gpu_pct": 10, "cpu_pct": 10}
        )
        tasks.append(task)
    
    # Step 5: Schedule all tasks
    await asyncio.gather(*[coordinator.schedule_task(t) for t in tasks])
    
    # Step 6: Assemble and receive stream
    task_ids = [t.task_id for t in tasks]
    stream = coordinator.assemble_stream(task_ids)
    renter.receive_stream(stream)
    
    print(f"✓ Completed {len(coordinator.completed)}/{len(tasks)} tasks")


if __name__ == "__main__":
    asyncio.run(basic_example())
