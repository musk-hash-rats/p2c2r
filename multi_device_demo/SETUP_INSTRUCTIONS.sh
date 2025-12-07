#!/bin/bash
# Quick 3-Device Demo Test
# Run each component in a separate terminal for real multi-device simulation

echo "🌐 P2C2R Multi-Device Demo Setup"
echo "=================================="
echo ""
echo "This demo requires 3 PHYSICAL DEVICES (or 3 terminals):"
echo ""
echo "📋 SETUP INSTRUCTIONS:"
echo ""
echo "1. Find your Cloud device IP:"
echo "   On Device 2, run: ifconfig | grep 'inet ' | grep -v 127.0.0.1"
echo "   Example output: inet 192.168.1.100"
echo ""
echo "2. On Device 2 (Cloud/Coordinator):"
echo "   cd /path/to/P2c2gPOC/multi_device_demo"
echo "   python3 run_cloud.py"
echo ""
echo "3. On Device 1 (Peer/Contributor):"
echo "   cd /path/to/P2c2gPOC/multi_device_demo"
echo "   python3 run_peer.py --cloud-ip 192.168.1.100"
echo ""
echo "4. On Device 3 (Gamer/Renter):"
echo "   cd /path/to/P2c2gPOC/multi_device_demo"
echo "   python3 run_gamer.py --cloud-ip 192.168.1.100"
echo ""
echo "=================================="
echo ""
echo "💡 SINGLE MACHINE TEST:"
echo "To test on ONE machine with 3 terminals:"
echo ""

# Get local IP
LOCAL_IP=$(ifconfig | grep 'inet ' | grep -v 127.0.0.1 | awk '{print $2}' | head -1)

echo "Your local IP: $LOCAL_IP"
echo ""
echo "Terminal 1: python3 run_cloud.py"
echo "Terminal 2: python3 run_peer.py --cloud-ip $LOCAL_IP"
echo "Terminal 3: python3 run_gamer.py --cloud-ip $LOCAL_IP"
echo ""
echo "=================================="
