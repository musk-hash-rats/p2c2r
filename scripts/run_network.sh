#!/bin/bash

# P2C2R Distributed System Launcher
# Starts cloud coordinator, peers, and user clients

echo "====================================================================="
echo "🚀 P2C2R DISTRIBUTED SYSTEM LAUNCHER"
echo "====================================================================="
echo ""

# Change to project root (parent of scripts directory)
cd "$(dirname "$0")/.."

# Check if running from correct directory
if [ ! -d "network" ]; then
    echo "❌ Error: Must run from P2c2gPOC root directory"
    echo "   Current directory: $(pwd)"
    exit 1
fi

# Check if websockets is installed
python3 -c "import websockets" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Warning: websockets not installed"
    echo "   Installing dependencies..."
    pip3 install websockets psutil
    echo ""
fi

# Function to kill all processes on exit
cleanup() {
    echo ""
    echo "====================================================================="
    echo "🛑 Shutting down P2C2R network..."
    echo "====================================================================="
    kill $(jobs -p) 2>/dev/null
    wait
    echo "✓ All processes stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start cloud coordinator
echo "1️⃣  Starting Cloud Coordinator..."
python3 network/cloud_coordinator.py &
CLOUD_PID=$!
sleep 2

# Start peers (default: 3 peers)
NUM_PEERS=${1:-3}
echo ""
echo "2️⃣  Starting $NUM_PEERS Peer Nodes..."
for i in $(seq 1 $NUM_PEERS); do
    echo "   Starting Peer $i..."
    python3 network/peer_node.py "peer_$i" ws://localhost:8765 &
    sleep 0.5
done
sleep 2

# Start user client in demo mode
echo ""
echo "3️⃣  Starting User Client (demo mode)..."
python3 network/user_client.py "demo_user" ws://localhost:8765 --demo &
USER_PID=$!

echo ""
echo "====================================================================="
echo "✓ P2C2R NETWORK RUNNING"
echo "====================================================================="
echo ""
echo "Processes:"
echo "  • Cloud Coordinator: localhost:8765"
echo "  • Peer Nodes: $NUM_PEERS"
echo "  • User Client: demo_user (demo mode)"
echo ""
echo "Press Ctrl+C to stop all processes"
echo "====================================================================="
echo ""

# Wait for all background processes
wait
