#!/usr/bin/env python3
"""
Device 1: Peer Node (Contributor)
Connects to cloud, receives tasks, executes them, earns money
"""

import asyncio
import websockets
import json
import argparse
import time
import socket
import sys
import os

# Add parent directory to path to import task executors
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'network'))

from task_executors import execute_task
from network_config import (
    DEFAULT_CLOUD_PORT, PEER_EARNING_RATE,
    MAX_RECONNECT_ATTEMPTS, RECONNECT_DELAY
)


class PeerNode:
    def __init__(self, cloud_ip: str, cloud_port: int, peer_id: str = None):
        self.cloud_url = f"ws://{cloud_ip}:{cloud_port}"
        self.peer_id = peer_id or f"peer_{socket.gethostname()}_{int(time.time())}"
        
        self.ws = None
        self.connected = False
        
        # Statistics
        self.start_time = time.time()
        self.tasks_completed = 0
        self.total_earned = 0.0
        self.total_processing_time_ms = 0.0
    
    async def connect(self):
        """Connect to cloud coordinator"""
        print(f"🔌 Connecting to cloud at {self.cloud_url}...")
        
        for attempt in range(MAX_RECONNECT_ATTEMPTS):
            try:
                self.ws = await websockets.connect(self.cloud_url)
                
                # Register as peer
                await self.ws.send(json.dumps({
                    "type": "register_peer",
                    "peer_id": self.peer_id
                }))
                
                response = await self.ws.recv()
                data = json.loads(response)
                
                if data.get("type") == "registered":
                    self.connected = True
                    print(f"✅ Connected! Registered as: {self.peer_id}")
                    print(f"💰 Earning rate: ${PEER_EARNING_RATE}/hour")
                    print()
                    return True
                    
            except Exception as e:
                print(f"❌ Connection attempt {attempt + 1} failed: {e}")
                if attempt < MAX_RECONNECT_ATTEMPTS - 1:
                    print(f"⏳ Retrying in {RECONNECT_DELAY} seconds...")
                    await asyncio.sleep(RECONNECT_DELAY)
        
        print("❌ Could not connect to cloud coordinator")
        return False
    
    async def handle_task(self, task_id: str, task_type: str, task_data: dict):
        """Execute a task and return result"""
        start_time = time.time()
        
        print(f"⚡ Received task: {task_type}")
        print(f"   Processing...")
        
        try:
            # Execute the task using real implementations
            result = await execute_task(task_type, task_data)
            
            processing_time_ms = (time.time() - start_time) * 1000
            
            # Calculate earnings
            hours_worked = processing_time_ms / 1000 / 3600
            earned = hours_worked * PEER_EARNING_RATE
            
            # Update stats
            self.tasks_completed += 1
            self.total_earned += earned
            self.total_processing_time_ms += processing_time_ms
            
            # Send result back
            await self.ws.send(json.dumps({
                "type": "task_result",
                "task_id": task_id,
                "result": result,
                "processing_time_ms": processing_time_ms
            }))
            
            print(f"   ✅ Completed in {processing_time_ms:.1f}ms")
            print(f"   💰 Earned: ${earned:.6f}")
            print()
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            # Send error result
            await self.ws.send(json.dumps({
                "type": "task_result",
                "task_id": task_id,
                "error": str(e)
            }))
    
    async def listen_loop(self):
        """Listen for tasks from coordinator"""
        try:
            async for message in self.ws:
                data = json.loads(message)
                msg_type = data.get("type")
                
                if msg_type == "execute_task":
                    task_id = data.get("task_id")
                    task_type = data.get("task_type")
                    task_data = data.get("task_data", {})
                    
                    # Execute task (non-blocking)
                    asyncio.create_task(self.handle_task(task_id, task_type, task_data))
                    
        except websockets.exceptions.ConnectionClosed:
            print("❌ Connection to cloud lost")
            self.connected = False
        except Exception as e:
            print(f"❌ Error in listen loop: {e}")
            self.connected = False
    
    async def stats_loop(self):
        """Display periodic statistics"""
        while self.connected:
            await asyncio.sleep(60)  # Every minute
            
            if self.connected:
                uptime_mins = (time.time() - self.start_time) / 60
                avg_task_time = (self.total_processing_time_ms / self.tasks_completed 
                               if self.tasks_completed > 0 else 0)
                
                print(f"\n📊 Peer Statistics:")
                print(f"   Uptime: {uptime_mins:.1f} minutes")
                print(f"   Tasks completed: {self.tasks_completed}")
                print(f"   Total earned: ${self.total_earned:.6f}")
                print(f"   Avg task time: {avg_task_time:.1f}ms")
                print(f"   Hourly rate: ${(self.total_earned / uptime_mins * 60):.6f}/hr")
                print()
    
    async def run(self):
        """Main peer node loop"""
        print("💻 P2C2R PEER NODE")
        print("=" * 50)
        
        if not await self.connect():
            return
        
        # Run listener and stats in parallel
        try:
            await asyncio.gather(
                self.listen_loop(),
                self.stats_loop()
            )
        except KeyboardInterrupt:
            print("\n\n👋 Peer node shutting down...")
            if self.ws:
                await self.ws.close()


def main():
    parser = argparse.ArgumentParser(description="P2C2R Peer Node - Device 1 (Contributor)")
    parser.add_argument("--cloud-ip", required=True,
                       help="IP address of cloud coordinator (Device 2)")
    parser.add_argument("--cloud-port", type=int, default=DEFAULT_CLOUD_PORT,
                       help=f"Port of cloud coordinator (default: {DEFAULT_CLOUD_PORT})")
    parser.add_argument("--peer-id", 
                       help="Custom peer ID (default: auto-generated)")
    
    args = parser.parse_args()
    
    peer = PeerNode(args.cloud_ip, args.cloud_port, args.peer_id)
    
    try:
        asyncio.run(peer.run())
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")


if __name__ == "__main__":
    main()
