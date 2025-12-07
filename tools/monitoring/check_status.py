#!/usr/bin/env python3
"""
P2C2R Status Checker
Quick health check for the network
"""

import socket
import subprocess
import sys

def check_port(port, service_name):
    """Check if a port is listening"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    
    status = "✅ RUNNING" if result == 0 else "❌ NOT RUNNING"
    print(f"  {service_name} (port {port}): {status}")
    return result == 0

def check_process(name):
    """Check if a process is running"""
    try:
        result = subprocess.run(
            ['pgrep', '-f', name],
            capture_output=True,
            text=True
        )
        running = len(result.stdout.strip()) > 0
        status = "✅ RUNNING" if running else "❌ NOT RUNNING"
        print(f"  {name}: {status}")
        return running
    except Exception:
        return False

def main():
    print("🔍 P2C2R System Status")
    print("=" * 50)
    
    print("\n📡 Network Services:")
    coord_running = check_port(8765, "Cloud Coordinator")
    gui_running = check_port(5001, "Web GUI")
    
    print("\n🖥️  Processes:")
    peer_running = check_process("peer_node")
    
    print("\n" + "=" * 50)
    
    if coord_running and peer_running:
        print("✅ System is OPERATIONAL")
        print("\n💡 Ready to test:")
        print("   python3 test_quick.py")
        print("   python3 demo_functionality.py")
        if gui_running:
            print("   http://localhost:5001 (GUI)")
        return 0
    else:
        print("❌ System is NOT READY")
        print("\n💡 To start the system:")
        print("   ./run_network.sh")
        if not gui_running:
            print("   python3 p2c2r_web_gui.py  (optional)")
        return 1

if __name__ == "__main__":
    sys.exit(main())
