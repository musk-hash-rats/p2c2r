#!/usr/bin/env python3
"""
P2C2G Proof of Concept (PoC)
---------------------------
A minimal, self-contained simulation of a Peer-to-Cloud-to-Gamer pipeline.

Goal:
    - Simulate multiple peers each contributing a slice of compute.
    - Coordinator schedules micro-tasks to peers, handles failover, assembles outputs.
    - Renter receives an assembled "stream" (bytes) representing processed frames.

Notes:
    - This PoC uses asyncio to model latency, processing time, and failover.
    - The workload is simplified to "frames" (bytes) processed by peers with artificial delays.
    - Resource constraints are simulated; no real GPU/CPU capping is performed.

Run:
    python p2c2g_poc.py

Expected:
    - Printouts showing task scheduling, processing, failovers, and renter receiving streams.
"""

import asyncio
import random
from typing import List

from p2c2g import Coordinator, PeerAgent, RenterClient, Task


async def demo_p2c2g(num_peers: int = 5, num_frames: int = 30) -> None:
    """
    Run the P2C2G demo:
        - Create peers with varied latency and reliability.
        - Generate a job with N frame-tasks.
        - Schedule tasks to peers with failover.
        - Assemble stream and deliver to renter.

    Args:
        num_peers (int): Number of simulated peers.
        num_frames (int): Number of frame tasks to process.
    """
    # Initialize coordinator and renter
    coordinator = Coordinator(max_attempts=3)
    renter = RenterClient("renter_01")

    # Create peers (diverse latencies and reliabilities)
    peers = [
        PeerAgent(
            peer_id=f"peer_{i+1}",
            base_latency_ms=random.choice([15, 25, 35, 45]),
            reliability=random.choice([0.78, 0.85, 0.9, 0.95]),
            max_throughput=random.choice([1, 2, 3]),
        )
        for i in range(num_peers)
    ]
    for p in peers:
        coordinator.register_peer(p)

    # Build tasks (frames) for a single job
    job_id = "job_001"
    tasks: List[Task] = []
    frame_order: List[str] = []
    for i in range(num_frames):
        # Simulate a frame payload as bytes
        payload = f"frame_{i:03d}".encode("utf-8")
        task_id = f"{job_id}_frame_{i:03d}"
        deadline_ms = random.choice([120, 150, 180])
        constraints = {"gpu_pct": 10, "cpu_pct": 10}
        tasks.append(Task(job_id, task_id, payload, deadline_ms, constraints))
        frame_order.append(task_id)

    # Dispatch tasks concurrently with bounded parallelism
    semaphore = asyncio.Semaphore(8)  # limit simultaneous schedules

    async def schedule_with_semaphore(t: Task):
        async with semaphore:
            await coordinator.schedule_task(t)

    print("\n=== Dispatching tasks ===")
    await asyncio.gather(*(schedule_with_semaphore(t) for t in tasks))

    print("\n=== Assembling stream ===")
    stream = coordinator.assemble_stream(frame_order)

    print("\n=== Delivering to renter ===")
    renter.receive_stream(stream)

    print("\n=== Summary ===")
    print(f"Total tasks: {len(tasks)}")
    print(f"Completed: {len(coordinator.completed)}")
    print(f"Failed permanently: {len(tasks) - len(coordinator.completed)}")
    print(f"Peer reputations: {coordinator.reputation}")


if __name__ == "__main__":
    print("P2C2G Proof of Concept")
    print("=" * 50)
    asyncio.run(demo_p2c2g(num_peers=5, num_frames=30))
    print("\nPoC complete!")
