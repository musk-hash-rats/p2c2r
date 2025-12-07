"""
Demo: ML-Enhanced Coordinator with Task Splitting

Demonstrates:
1. ML learning from task execution history
2. Intelligent task splitting across peers
3. Performance improvements over time
"""

import asyncio
import random
import time
from typing import List

from src.p2c2g.models import Task
from src.p2c2g.peer import PeerAgent
from src.p2c2g.ml_coordinator import MLCoordinator
from src.p2c2g.task_splitter import SpatialSplitter, FunctionalSplitter, HybridSplitter


async def demo_ml_learning():
    """
    Demonstrate ML coordinator learning over time.
    
    We'll run 100 tasks and watch the coordinator improve.
    """
    
    print("=" * 70)
    print("DEMO 1: ML Learning Over Time")
    print("=" * 70)
    print()
    
    # Create ML coordinator
    coordinator = MLCoordinator()
    
    # Create diverse peer pool
    peers = [
        PeerAgent(peer_id="GPU_Beast", latency_ms=20, reliability=0.98, gpu_score=95),
        PeerAgent(peer_id="Balanced_1", latency_ms=30, reliability=0.95, gpu_score=70),
        PeerAgent(peer_id="Budget_PC", latency_ms=50, reliability=0.90, gpu_score=50),
        PeerAgent(peer_id="Unstable", latency_ms=25, reliability=0.75, gpu_score=85),  # Fast but unreliable
        PeerAgent(peer_id="Slow_Reliable", latency_ms=80, reliability=0.99, gpu_score=60),
    ]
    
    for peer in peers:
        coordinator.register_peer(peer)
    
    print("Registered 5 peers:")
    for peer in peers:
        print(f"  - {peer.peer_id}: latency={peer.latency_ms}ms, "
              f"reliability={peer.reliability:.0%}, gpu={peer.gpu_score}")
    print()
    
    # Phase 1: Initial learning (first 20 tasks)
    print("📚 Phase 1: Initial Learning (20 tasks)")
    print("-" * 70)
    
    phase1_start = time.time()
    phase1_failures = 0
    
    for i in range(20):
        task = Task(
            job_id="training",
            task_id=f"task_{i}",
            payload=b"ray_tracing_data",
            deadline_ms=100,
            constraints={'type': 'ray_tracing', 'requires_rtx': True}
        )
        
        result = await coordinator.schedule_task_ml(task)
        if result.status == 'failure':
            phase1_failures += 1
        
        if (i + 1) % 5 == 0:
            print(f"  Completed {i + 1}/20 tasks...")
    
    phase1_time = time.time() - phase1_start
    
    print(f"\n✓ Phase 1 complete: {phase1_time:.2f}s, {phase1_failures} failures")
    print("\nML Performance Stats (after 20 tasks):")
    stats = coordinator.get_performance_stats()
    for peer_id, stat in stats.items():
        trained = "✓ Trained" if stat['trained'] else "✗ Not enough data"
        print(f"  {peer_id}: {stat['total_tasks']} tasks, "
              f"{stat['success_rate']:.0%} success, "
              f"avg {stat['avg_time_ms']:.1f}ms - {trained}")
    print()
    
    # Phase 2: Continued learning (next 30 tasks)
    print("🧠 Phase 2: ML Optimization (30 tasks)")
    print("-" * 70)
    
    phase2_start = time.time()
    phase2_failures = 0
    
    for i in range(20, 50):
        task = Task(
            job_id="optimized",
            task_id=f"task_{i}",
            payload=b"ray_tracing_data",
            deadline_ms=100,
            constraints={'type': 'ray_tracing', 'requires_rtx': True}
        )
        
        result = await coordinator.schedule_task_ml(task)
        if result.status == 'failure':
            phase2_failures += 1
        
        if (i + 1) % 10 == 0:
            print(f"  Completed {i + 1}/50 tasks...")
    
    phase2_time = time.time() - phase2_start
    
    print(f"\n✓ Phase 2 complete: {phase2_time:.2f}s, {phase2_failures} failures")
    print("\nML Performance Stats (after 50 tasks):")
    stats = coordinator.get_performance_stats()
    for peer_id, stat in stats.items():
        trained = "✓ Trained" if stat['trained'] else "✗ Not enough data"
        print(f"  {peer_id}: {stat['total_tasks']} tasks, "
              f"{stat['success_rate']:.0%} success, "
              f"avg {stat['avg_time_ms']:.1f}ms - {trained}")
    print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY:")
    print(f"  Phase 1 (learning):    {phase1_time:.2f}s, {phase1_failures}/20 failures ({phase1_failures/20:.0%})")
    print(f"  Phase 2 (optimized):   {phase2_time:.2f}s, {phase2_failures}/30 failures ({phase2_failures/30:.0%})")
    improvement = ((phase1_time / 20) - (phase2_time / 30)) / (phase1_time / 20) * 100
    print(f"  Speed improvement:     {improvement:+.1f}%")
    print("=" * 70)
    print()


async def demo_task_splitting():
    """
    Demonstrate task splitting strategies.
    
    Shows how a large task can be split across multiple peers.
    """
    
    print("=" * 70)
    print("DEMO 2: Task Splitting Strategies")
    print("=" * 70)
    print()
    
    # Create different splitters
    spatial_splitter = SpatialSplitter()
    functional_splitter = FunctionalSplitter()
    hybrid_splitter = HybridSplitter()
    
    # Test 1: Spatial splitting for ray tracing
    print("🎯 Test 1: Spatial Splitting (Ray Tracing)")
    print("-" * 70)
    
    ray_tracing_task = Task(
        job_id="frame_42",
        task_id="ray_trace",
        payload=b"scene_data",
        deadline_ms=100,
        constraints={
            'type': 'ray_tracing',
            'resolution': (1920, 1080),
            'requires_rtx': True
        }
    )
    
    num_peers = 4
    subtasks = spatial_splitter.split(ray_tracing_task, num_peers)
    
    print(f"Original task split into {len(subtasks)} tiles:")
    for i, subtask in enumerate(subtasks):
        bounds = subtask.payload['tile_bounds']
        complexity = subtask.constraints['estimated_complexity']
        print(f"  Tile {i}: ({bounds['x']}, {bounds['y']}) "
              f"{bounds['width']}x{bounds['height']} - "
              f"complexity: {complexity:.0f}")
    print()
    
    # Test 2: Functional splitting for game frame
    print("🎮 Test 2: Functional Splitting (Game Frame)")
    print("-" * 70)
    
    game_frame_task = Task(
        job_id="game_session_1",
        task_id="frame_0",
        payload=b"game_state",
        deadline_ms=16,  # 60 FPS
        constraints={'type': 'game_frame'}
    )
    
    subtasks = functional_splitter.split(game_frame_task, num_peers=5)
    
    print(f"Game frame split into {len(subtasks)} subsystems:")
    for i, subtask in enumerate(subtasks):
        subsystem = subtask.payload['subsystem']
        deadline = subtask.deadline_ms
        print(f"  {subsystem}: deadline {deadline}ms")
    print()
    
    # Test 3: Hybrid splitting (intelligent)
    print("🚀 Test 3: Hybrid Splitting (Intelligent)")
    print("-" * 70)
    
    tasks_to_test = [
        ("Ray Tracing", Task(
            job_id="test", task_id="rt", payload=b"data", deadline_ms=100,
            constraints={'type': 'ray_tracing', 'resolution': (1920, 1080)}
        )),
        ("Game Frame", Task(
            job_id="test", task_id="gf", payload=b"data", deadline_ms=16,
            constraints={'type': 'game_frame'}
        )),
        ("Rendering", Task(
            job_id="test", task_id="render", payload=b"data", deadline_ms=16,
            constraints={'type': 'rendering'}
        ))
    ]
    
    for name, task in tasks_to_test:
        subtasks = hybrid_splitter.split(task, num_peers=4)
        print(f"  {name}: split into {len(subtasks)} subtasks using "
              f"{'spatial' if len(subtasks) > 1 and 'tile' in subtasks[0].task_id else 'functional' if 'subsystem' in subtasks[0].payload else 'pipeline'} strategy")
    
    print()
    print("=" * 70)
    print()


async def demo_ml_with_splitting():
    """
    Demonstrate ML coordinator with task splitting.
    
    This is the full system working together!
    """
    
    print("=" * 70)
    print("DEMO 3: ML Coordinator + Task Splitting (Full System)")
    print("=" * 70)
    print()
    
    # Create ML coordinator
    coordinator = MLCoordinator()
    
    # Create peer pool
    peers = [
        PeerAgent(peer_id="GPU_1", latency_ms=20, reliability=0.95, gpu_score=90),
        PeerAgent(peer_id="GPU_2", latency_ms=25, reliability=0.93, gpu_score=85),
        PeerAgent(peer_id="GPU_3", latency_ms=30, reliability=0.90, gpu_score=75),
        PeerAgent(peer_id="GPU_4", latency_ms=35, reliability=0.88, gpu_score=70),
    ]
    
    for peer in peers:
        coordinator.register_peer(peer)
    
    print(f"Registered {len(peers)} peers")
    print()
    
    # Create task splitter
    splitter = HybridSplitter()
    
    # Simulate rendering 10 frames with ray tracing
    print("🎬 Rendering 10 frames with ray tracing...")
    print("-" * 70)
    
    total_start = time.time()
    frame_times = []
    
    for frame_id in range(10):
        frame_start = time.time()
        
        # Create ray tracing task
        task = Task(
            job_id=f"frame_{frame_id}",
            task_id="ray_trace",
            payload=b"scene_data",
            deadline_ms=100,
            constraints={
                'type': 'ray_tracing',
                'resolution': (1920, 1080),
                'requires_rtx': True
            }
        )
        
        # Split task across peers
        subtasks = splitter.split(task, num_peers=len(peers))
        
        # Schedule all subtasks in parallel
        results = await asyncio.gather(*[
            coordinator.schedule_task_ml(subtask)
            for subtask in subtasks
        ])
        
        # Check if all succeeded
        successes = sum(1 for r in results if r.status == 'success')
        frame_time = (time.time() - frame_start) * 1000
        frame_times.append(frame_time)
        
        print(f"  Frame {frame_id}: {frame_time:.1f}ms "
              f"({successes}/{len(subtasks)} tiles succeeded)")
    
    total_time = time.time() - total_start
    avg_frame_time = sum(frame_times) / len(frame_times)
    fps = 1000 / avg_frame_time
    
    print()
    print("=" * 70)
    print("RENDERING COMPLETE:")
    print(f"  Total time:        {total_time:.2f}s")
    print(f"  Average frame:     {avg_frame_time:.1f}ms")
    print(f"  Effective FPS:     {fps:.1f}")
    print(f"  Min frame time:    {min(frame_times):.1f}ms")
    print(f"  Max frame time:    {max(frame_times):.1f}ms")
    print("=" * 70)
    print()
    
    # Show final ML stats
    print("Final ML Performance Stats:")
    stats = coordinator.get_performance_stats()
    for peer_id, stat in stats.items():
        print(f"  {peer_id}: {stat['total_tasks']} tasks, "
              f"{stat['success_rate']:.0%} success, "
              f"avg {stat['avg_time_ms']:.1f}ms")
    print()


async def main():
    """Run all demos."""
    
    print()
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                                                                    ║")
    print("║       P2C2G: ML OPTIMIZATION & TASK SPLITTING DEMO                ║")
    print("║                                                                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print()
    
    # Run demos sequentially
    await demo_ml_learning()
    await demo_task_splitting()
    await demo_ml_with_splitting()
    
    print()
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                                                                    ║")
    print("║                      ALL DEMOS COMPLETE!                           ║")
    print("║                                                                    ║")
    print("║  The ML coordinator learns to:                                     ║")
    print("║    ✓ Predict peer performance                                      ║")
    print("║    ✓ Avoid unreliable peers                                        ║")
    print("║    ✓ Balance load intelligently                                    ║")
    print("║    ✓ Adapt to network conditions                                   ║")
    print("║                                                                    ║")
    print("║  Task splitting enables:                                           ║")
    print("║    ✓ Parallel execution across multiple peers                      ║")
    print("║    ✓ Better resource utilization                                   ║")
    print("║    ✓ Adaptive tiling based on complexity                           ║")
    print("║    ✓ Functional decomposition for game frames                      ║")
    print("║                                                                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print()


if __name__ == '__main__':
    asyncio.run(main())
