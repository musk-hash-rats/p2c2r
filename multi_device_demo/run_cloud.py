#!/usr/bin/env python3
"""
Device 2: Cloud Coordinator + Storage
Runs the WebSocket server, routes tasks, stores all computations
"""

import asyncio
import websockets
import json
import argparse
import time
import sys
import os
from typing import Dict, Set, Any

# Add parent directory to path to import task executors
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'network'))

from cloud_storage import CloudStorage
from network_config import (
    DEFAULT_CLOUD_HOST, DEFAULT_CLOUD_PORT,
    PEER_EARNING_RATE, GAMER_COST_RATE, COORDINATOR_FEE,
    HEARTBEAT_INTERVAL
)


class CloudCoordinator:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.storage = CloudStorage()
        
        # Active connections
        self.peers: Dict[str, Any] = {}  # peer_id -> {ws, info}
        self.gamers: Dict[str, Any] = {}  # gamer_id -> {ws, info}
        
        # Task queue
        self.pending_tasks: Dict[str, Any] = {}  # task_id -> task_info
        
        # Statistics
        self.start_time = time.time()
        self.tasks_routed = 0
        self.total_revenue = 0.0
        
    async def handle_client(self, websocket, path):
        """Handle incoming WebSocket connections"""
        client_id = None
        client_type = None
        remote_ip = websocket.remote_address[0]
        
        try:
            async for message in websocket:
                data = json.loads(message)
                msg_type = data.get("type")
                
                # Registration
                if msg_type == "register_peer":
                    client_id = data.get("peer_id")
                    client_type = "peer"
                    self.peers[client_id] = {
                        "ws": websocket,
                        "ip": remote_ip,
                        "registered_at": time.time()
                    }
                    self.storage.register_peer(client_id, remote_ip)
                    await websocket.send(json.dumps({
                        "type": "registered",
                        "message": f"Registered as peer: {client_id}"
                    }))
                    print(f"📡 Peer connected: {client_id} ({remote_ip})")
                    
                elif msg_type == "register_gamer":
                    client_id = data.get("gamer_id")
                    client_type = "gamer"
                    self.gamers[client_id] = {
                        "ws": websocket,
                        "ip": remote_ip,
                        "registered_at": time.time()
                    }
                    self.storage.register_gamer(client_id, remote_ip)
                    await websocket.send(json.dumps({
                        "type": "registered",
                        "message": f"Registered as gamer: {client_id}"
                    }))
                    print(f"🎮 Gamer connected: {client_id} ({remote_ip})")
                
                # Task submission from gamer
                elif msg_type == "submit_task":
                    if client_type != "gamer":
                        continue
                    
                    task = data.get("task", {})
                    task_id = f"task_{client_id}_{int(time.time() * 1000)}"
                    task_type = task.get("type")
                    task_data = task.get("data", {})
                    
                    # Check cache first
                    cached = self.storage.get_cached_result(task_type, task_data)
                    if cached:
                        print(f"📦 Cache hit: {task_type} (saved compute!)")
                        await websocket.send(json.dumps({
                            "type": "task_result",
                            "task_id": task_id,
                            "status": "completed",
                            "result": cached,
                            "cached": True
                        }))
                        continue
                    
                    # Store task
                    self.storage.store_task(task_id, client_id, task_type, task_data)
                    
                    # Route to available peer
                    if self.peers:
                        peer_id = list(self.peers.keys())[0]  # Simple: pick first
                        peer = self.peers[peer_id]
                        
                        self.storage.assign_task_to_peer(task_id, peer_id)
                        
                        # Send to peer
                        await peer["ws"].send(json.dumps({
                            "type": "execute_task",
                            "task_id": task_id,
                            "task_type": task_type,
                            "task_data": task_data
                        }))
                        
                        # Track for response routing
                        self.pending_tasks[task_id] = {
                            "gamer_id": client_id,
                            "peer_id": peer_id,
                            "submitted_at": time.time()
                        }
                        
                        print(f"📥 Task {task_type} from {client_id} → {peer_id}")
                        self.tasks_routed += 1
                    else:
                        # No peers available
                        await websocket.send(json.dumps({
                            "type": "task_result",
                            "task_id": task_id,
                            "status": "error",
                            "error": "No peers available"
                        }))
                        print(f"❌ No peers available for task {task_type}")
                
                # Task result from peer
                elif msg_type == "task_result":
                    if client_type != "peer":
                        continue
                    
                    task_id = data.get("task_id")
                    result = data.get("result")
                    processing_time = data.get("processing_time_ms", 0)
                    
                    if task_id in self.pending_tasks:
                        task_info = self.pending_tasks[task_id]
                        gamer_id = task_info["gamer_id"]
                        
                        # Calculate costs
                        cost_usd = (processing_time / 1000 / 3600) * GAMER_COST_RATE
                        peer_earning = (processing_time / 1000 / 3600) * PEER_EARNING_RATE
                        coordinator_fee = cost_usd * COORDINATOR_FEE
                        
                        # Update database
                        self.storage.store_result(task_id, result, processing_time, cost_usd)
                        self.storage.update_peer_earnings(client_id, peer_earning)
                        self.storage.update_gamer_spending(gamer_id, cost_usd)
                        
                        self.total_revenue += coordinator_fee
                        
                        # Send to gamer
                        if gamer_id in self.gamers:
                            gamer_ws = self.gamers[gamer_id]["ws"]
                            await gamer_ws.send(json.dumps({
                                "type": "task_result",
                                "task_id": task_id,
                                "status": "completed",
                                "result": result,
                                "processing_time_ms": processing_time,
                                "cost_usd": cost_usd
                            }))
                        
                        print(f"📤 Result {task_id} → {gamer_id} ({processing_time:.1f}ms, ${cost_usd:.6f})")
                        
                        del self.pending_tasks[task_id]
                
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            print(f"❌ Error handling client: {e}")
        finally:
            # Cleanup on disconnect
            if client_id:
                if client_type == "peer" and client_id in self.peers:
                    del self.peers[client_id]
                    print(f"📡 Peer disconnected: {client_id}")
                elif client_type == "gamer" and client_id in self.gamers:
                    del self.gamers[client_id]
                    print(f"🎮 Gamer disconnected: {client_id}")
    
    async def cleanup_loop(self):
        """Periodic cleanup of expired data"""
        while True:
            await asyncio.sleep(3600)  # Every hour
            self.storage.cleanup_expired_results()
    
    async def stats_loop(self):
        """Periodic statistics display"""
        while True:
            await asyncio.sleep(30)  # Every 30 seconds
            uptime_mins = (time.time() - self.start_time) / 60
            stats = self.storage.get_statistics()
            
            print(f"\n📊 Network Stats:")
            print(f"   Uptime: {uptime_mins:.1f} minutes")
            print(f"   Active Peers: {len(self.peers)} | Active Gamers: {len(self.gamers)}")
            print(f"   Tasks Routed: {self.tasks_routed}")
            print(f"   Total Revenue: ${self.total_revenue:.6f} (coordinator fee)")
            print(f"   Database: {stats.get('total_tasks_completed', 0)} tasks stored\n")
    
    async def start(self):
        """Start the cloud coordinator server"""
        print("☁️  P2C2R CLOUD COORDINATOR")
        print("=" * 50)
        print(f"🌐 Starting server on {self.host}:{self.port}")
        print(f"💾 Database: {self.storage.db_path}")
        print(f"💰 Rates: Peer earns ${PEER_EARNING_RATE}/hr, Gamer pays ${GAMER_COST_RATE}/hr")
        print("=" * 50)
        print()
        
        # Start server
        async with websockets.serve(self.handle_client, self.host, self.port):
            # Start background tasks
            await asyncio.gather(
                self.cleanup_loop(),
                self.stats_loop()
            )


def main():
    parser = argparse.ArgumentParser(description="P2C2R Cloud Coordinator (Device 2)")
    parser.add_argument("--host", default=DEFAULT_CLOUD_HOST,
                       help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=DEFAULT_CLOUD_PORT,
                       help=f"Port to bind to (default: {DEFAULT_CLOUD_PORT})")
    
    args = parser.parse_args()
    
    coordinator = CloudCoordinator(args.host, args.port)
    
    try:
        asyncio.run(coordinator.start())
    except KeyboardInterrupt:
        print("\n\n👋 Cloud coordinator shutting down...")
        coordinator.storage.close()


if __name__ == "__main__":
    main()
