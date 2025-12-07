#!/usr/bin/env python3
"""
Single-Machine Test for Multi-Device Demo
Tests all 3 components on one machine (for development/testing)
"""

import subprocess
import time
import sys
import socket

def get_local_ip():
    """Get local IP address"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def main():
    print("🧪 P2C2R Multi-Device Demo - Single Machine Test")
    print("=" * 60)
    print("\nThis will simulate 3 devices on one machine:")
    print("  Device 1 (Peer): Will provide compute")
    print("  Device 2 (Cloud): Will coordinate and store")
    print("  Device 3 (Gamer): Will submit tasks\n")
    
    local_ip = get_local_ip()
    print(f"💻 Local IP: {local_ip}")
    print(f"🌐 Cloud will run on: {local_ip}:8765\n")
    
    input("Press Enter to start all 3 components...")
    
    processes = []
    
    try:
        # Start cloud coordinator
        print("\n1️⃣  Starting Cloud Coordinator (Device 2)...")
        cloud_proc = subprocess.Popen(
            [sys.executable, "run_cloud.py"],
            cwd="/Users/robertgreenwood/P2c2gPOC/multi_device_demo"
        )
        processes.append(("Cloud", cloud_proc))
        time.sleep(2)  # Let cloud start
        
        # Start peer
        print("\n2️⃣  Starting Peer Node (Device 1)...")
        peer_proc = subprocess.Popen(
            [sys.executable, "run_peer.py", "--cloud-ip", local_ip],
            cwd="/Users/robertgreenwood/P2c2gPOC/multi_device_demo"
        )
        processes.append(("Peer", peer_proc))
        time.sleep(2)  # Let peer connect
        
        # Start gamer (interactive)
        print("\n3️⃣  Starting Gamer Client (Device 3)...")
        print("\n" + "=" * 60)
        print("🎮 You can now interact with the gamer client!")
        print("=" * 60 + "\n")
        
        gamer_proc = subprocess.Popen(
            [sys.executable, "run_gamer.py", "--cloud-ip", local_ip],
            cwd="/Users/robertgreenwood/P2c2gPOC/multi_device_demo"
        )
        processes.append(("Gamer", gamer_proc))
        
        # Wait for gamer to finish
        gamer_proc.wait()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    finally:
        print("\n\n🛑 Shutting down all components...")
        for name, proc in processes:
            if proc.poll() is None:  # Still running
                print(f"   Stopping {name}...")
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print(f"   Force killing {name}...")
                    proc.kill()
        
        print("✅ All components stopped\n")

if __name__ == "__main__":
    main()
