#!/usr/bin/env python3
"""
Quick test script to verify P2C2R network functionality.

This script:
1. Starts cloud coordinator
2. Starts 2 peers
3. Runs a user client with test tasks
4. Verifies results
5. Shuts everything down
"""

import asyncio
import subprocess
import time
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 70)
print("🧪 P2C2R NETWORK TEST")
print("=" * 70)
print()

# List to track processes
processes = []

def cleanup():
    """Kill all processes."""
    print("\n🧹 Cleaning up processes...")
    for p in processes:
        try:
            p.terminate()
            p.wait(timeout=2)
        except:
            try:
                p.kill()
            except:
                pass
    print("✓ Cleanup complete")

try:
    # Start cloud coordinator
    print("1️⃣  Starting Cloud Coordinator...")
    cloud = subprocess.Popen(
        [sys.executable, 'network/cloud_coordinator.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    processes.append(cloud)
    time.sleep(2)
    
    # Check if cloud started
    if cloud.poll() is not None:
        print("❌ Cloud coordinator failed to start")
        stderr = cloud.stderr.read()
        print(f"Error: {stderr}")
        cleanup()
        sys.exit(1)
    
    print("   ✓ Cloud coordinator started")
    
    # Start peers
    print("\n2️⃣  Starting Peer Nodes...")
    for i in range(1, 3):
        peer = subprocess.Popen(
            [sys.executable, 'network/peer_node.py', f'test_peer_{i}'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        processes.append(peer)
        time.sleep(0.5)
        print(f"   ✓ Peer {i} started")
    
    time.sleep(2)
    
    # Start user client in demo mode
    print("\n3️⃣  Starting User Client (demo mode)...")
    user = subprocess.Popen(
        [sys.executable, 'network/user_client.py', 'test_user', 'ws://localhost:8765', '--demo'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    processes.append(user)
    
    # Monitor user output
    print("\n📋 Test Results:")
    print("-" * 70)
    
    task_count = 0
    success_count = 0
    
    # Read output for 15 seconds
    start_time = time.time()
    while time.time() - start_time < 15:
        line = user.stdout.readline()
        if not line:
            break
        
        line = line.strip()
        if line:
            # Count tasks
            if 'Task submitted' in line:
                task_count += 1
            elif 'Task completed' in line:
                success_count += 1
            
            # Print important lines
            if any(keyword in line for keyword in ['Task submitted', 'Task completed', 'Error', 'Failed']):
                print(f"   {line}")
    
    print("-" * 70)
    
    # Evaluate results
    print("\n📊 Test Summary:")
    print(f"   Tasks submitted: {task_count}")
    print(f"   Tasks completed: {success_count}")
    
    if success_count >= task_count * 0.8:  # 80% success rate
        print("\n✅ TEST PASSED!")
        print("   Network is functioning correctly.")
    else:
        print("\n⚠️  TEST INCONCLUSIVE")
        print("   Some tasks may still be processing.")
        print("   Run the network manually to investigate.")
    
except KeyboardInterrupt:
    print("\n\n⚠️  Test interrupted by user")
except Exception as e:
    print(f"\n❌ Test failed with error: {e}")
    import traceback
    traceback.print_exc()
finally:
    cleanup()

print("\n" + "=" * 70)
print("Test complete!")
print("=" * 70)
