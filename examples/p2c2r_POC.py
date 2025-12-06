#!/usr/bin/env python3
"""
Custom P2C2G Simulation Example
-------------------------------
Demonstrates how to customize the P2C2G simulation with different
peer configurations and workload characteristics.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from p2c2g.models import Task
from p2c2g.peer import PeerAgent
from p2c2g.coordinator import Coordinator
from p2c2g.renter import RenterClient


async def custom_simulation():
    """
    Run a custom simulation with specific peer profiles.
    """
    print("=== Custom P2C2G Simulation ===\n")
    
    # Initialize coordinator with custom retry limit
    coordinator = Coordinator(max_attempts=5)
    
    # Create diverse peer profiles
    peers = [
        # High-performance, reliable peer (data center)
        PeerAgent(
            peer_id="datacenter_01",
            base_latency_ms=10,
            reliability=0.98,
            max_throughput=5
        ),
        # Medium-performance peers (edge servers)
        PeerAgent(
            peer_id="edge_01",
            base_latency_ms=25,
            reliability=0.90,
            max_throughput=3
        ),
        PeerAgent(
            peer_id="edge_02",
            base_latency_ms=30,
            reliability=0.88,
            max_throughput=3
        ),
        # Consumer-grade peers (home computers)
        PeerAgent(
            peer_id="consumer_01",
            base_latency_ms=45,
            reliability=0.75,
            max_throughput=2
        ),
        PeerAgent(
            peer_id="consumer_02",
            base_latency_ms=50,
            reliability=0.70,
            max_throughput=1
        ),
    ]
    
    # Register all peers
    for peer in peers:
        coordinator.register_peer(peer)
        print(f"Registered {peer.peer_id}: "
              f"latency={peer.base_latency_ms}ms, "
              f"reliability={peer.reliability:.0%}, "
              f"throughput={peer.max_throughput}")
    
    # Create renter
    renter = RenterClient("gamer_001")
    
    # Generate workload - simulate video frames
    print(f"\n=== Generating Workload ===")
    job_id = "gaming_session_001"
    num_frames = 60  # 2 seconds at 30 FPS
    tasks = []
    
    for frame_num in range(num_frames):
        # Simulate frame data (larger payload than default)
        frame_data = f"FRAME_{frame_num:04d}_" + "X" * 100
        payload = frame_data.encode("utf-8")
        
        task_id = f"{job_id}_frame_{frame_num:04d}"
        
        # Vary deadline based on frame importance
        # I-frames get longer deadlines, P-frames shorter
        if frame_num % 10 == 0:  # I-frame
            deadline_ms = 200
        else:  # P-frame
            deadline_ms = 100
        
        constraints = {
            "gpu_pct": 15,
            "cpu_pct": 10,
            "memory_mb": 256
        }
        
        task = Task(job_id, task_id, payload, deadline_ms, constraints)
        tasks.append(task)
    
    print(f"Generated {len(tasks)} frame tasks")
    
    # Schedule all tasks with controlled concurrency
    print(f"\n=== Scheduling Tasks ===")
    semaphore = asyncio.Semaphore(10)  # Max 10 concurrent
    
    async def schedule_with_limit(t: Task):
        async with semaphore:
            await coordinator.schedule_task(t)
    
    start_time = asyncio.get_event_loop().time()
    await asyncio.gather(*[schedule_with_limit(t) for t in tasks])
    end_time = asyncio.get_event_loop().time()
    
    # Calculate statistics
    total_time = end_time - start_time
    completed = len(coordinator.completed)
    failed = len(tasks) - completed
    success_rate = (completed / len(tasks)) * 100
    
    print(f"\n=== Results ===")
    print(f"Total tasks: {len(tasks)}")
    print(f"Completed: {completed}")
    print(f"Failed: {failed}")
    print(f"Success rate: {success_rate:.1f}%")
    print(f"Total time: {total_time:.2f}s")
    print(f"Throughput: {len(tasks) / total_time:.1f} tasks/sec")
    
    # Show peer statistics
    print(f"\n=== Peer Statistics ===")
    peer_task_counts = {}
    peer_durations = {}
    
    for result in coordinator.completed.values():
        peer_id = result.peer_id
        peer_task_counts[peer_id] = peer_task_counts.get(peer_id, 0) + 1
        if peer_id not in peer_durations:
            peer_durations[peer_id] = []
        peer_durations[peer_id].append(result.duration_ms)
    
    for peer_id in sorted(peer_task_counts.keys()):
        count = peer_task_counts[peer_id]
        avg_duration = sum(peer_durations[peer_id]) / len(peer_durations[peer_id])
        reputation = coordinator.reputation[peer_id]
        print(f"{peer_id:20s}: {count:3d} tasks, "
              f"avg {avg_duration:5.1f}ms, "
              f"reputation {reputation:.2f}")
    
    # Assemble and deliver stream
    print(f"\n=== Assembling Stream ===")
    frame_order = [t.task_id for t in tasks]
    stream = coordinator.assemble_stream(frame_order)
    renter.receive_stream(stream)
    
    print(f"\n=== Simulation Complete ===")


if __name__ == "__main__":
    asyncio.run(custom_simulation())
