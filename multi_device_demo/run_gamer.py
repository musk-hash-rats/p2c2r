#!/usr/bin/env python3
"""
Device 3: Gamer Client (Renter)
Connects to cloud, submits tasks, receives results, plays games
"""

import asyncio
import websockets
import json
import argparse
import time
import socket
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'network'))

from network_config import (
    DEFAULT_CLOUD_PORT, GAMER_COST_RATE,
    MAX_RECONNECT_ATTEMPTS, RECONNECT_DELAY, TASK_TIMEOUT
)


class GamerClient:
    def __init__(self, cloud_ip: str, cloud_port: int, gamer_id: str = None):
        self.cloud_url = f"ws://{cloud_ip}:{cloud_port}"
        self.gamer_id = gamer_id or f"gamer_{socket.gethostname()}_{int(time.time())}"
        
        self.ws = None
        self.connected = False
        
        # Track pending tasks
        self.pending_tasks = {}
        
        # Statistics
        self.start_time = time.time()
        self.tasks_submitted = 0
        self.tasks_completed = 0
        self.total_spent = 0.0
        self.total_latency_ms = 0.0
    
    async def connect(self):
        """Connect to cloud coordinator"""
        print(f"🔌 Connecting to cloud at {self.cloud_url}...")
        
        for attempt in range(MAX_RECONNECT_ATTEMPTS):
            try:
                self.ws = await websockets.connect(self.cloud_url)
                
                # Register as gamer
                await self.ws.send(json.dumps({
                    "type": "register_gamer",
                    "gamer_id": self.gamer_id
                }))
                
                response = await self.ws.recv()
                data = json.loads(response)
                
                if data.get("type") == "registered":
                    self.connected = True
                    print(f"✅ Connected! Registered as: {self.gamer_id}")
                    print(f"💰 Cost rate: ${GAMER_COST_RATE}/hour")
                    print()
                    return True
                    
            except Exception as e:
                print(f"❌ Connection attempt {attempt + 1} failed: {e}")
                if attempt < MAX_RECONNECT_ATTEMPTS - 1:
                    print(f"⏳ Retrying in {RECONNECT_DELAY} seconds...")
                    await asyncio.sleep(RECONNECT_DELAY)
        
        print("❌ Could not connect to cloud coordinator")
        return False
    
    async def submit_task(self, task_type: str, task_data: dict, timeout: float = TASK_TIMEOUT):
        """Submit a task and wait for result"""
        if not self.connected:
            raise Exception("Not connected to cloud")
        
        task_id = f"task_{self.gamer_id}_{int(time.time() * 1000)}_{self.tasks_submitted}"
        start_time = time.time()
        
        # Create future for result
        future = asyncio.Future()
        self.pending_tasks[task_id] = future
        
        # Submit task
        await self.ws.send(json.dumps({
            "type": "submit_task",
            "task": {
                "type": task_type,
                "data": task_data
            }
        }))
        
        self.tasks_submitted += 1
        
        # Wait for result with timeout
        try:
            result = await asyncio.wait_for(future, timeout=timeout)
            
            latency_ms = (time.time() - start_time) * 1000
            self.tasks_completed += 1
            self.total_latency_ms += latency_ms
            
            if "cost_usd" in result:
                self.total_spent += result["cost_usd"]
            
            return result, latency_ms
            
        except asyncio.TimeoutError:
            del self.pending_tasks[task_id]
            raise Exception(f"Task timed out after {timeout}s")
    
    async def listen_loop(self):
        """Listen for results from coordinator"""
        try:
            async for message in self.ws:
                data = json.loads(message)
                msg_type = data.get("type")
                
                if msg_type == "task_result":
                    task_id = data.get("task_id")
                    
                    # Find pending task
                    if task_id in self.pending_tasks:
                        future = self.pending_tasks[task_id]
                        
                        if data.get("status") == "completed":
                            future.set_result(data)
                        else:
                            error = data.get("error", "Unknown error")
                            future.set_exception(Exception(error))
                        
                        del self.pending_tasks[task_id]
                        
        except websockets.exceptions.ConnectionClosed:
            print("❌ Connection to cloud lost")
            self.connected = False
        except Exception as e:
            print(f"❌ Error in listen loop: {e}")
            self.connected = False
    
    async def interactive_demo(self):
        """Interactive demo mode for testing"""
        print("🎮 P2C2R GAMER CLIENT - Interactive Demo")
        print("=" * 50)
        print("\nAvailable tasks:")
        print("  1. AI: NPC Dialogue")
        print("  2. AI: Pathfinding")
        print("  3. AI: Procedural Generation")
        print("  4. RT: Reflections")
        print("  5. RT: Shadows")
        print("  6. RT: Global Illumination")
        print("  7. Physics: Rigid Body")
        print("  8. Physics: Fluid")
        print("  9. Physics: Destruction")
        print("  0. Auto Demo (run all)")
        print("  q. Quit")
        print()
        
        tasks = {
            "1": ("ai_npc_dialogue", {"character": "Shopkeeper", "context": "greeting", "personality": "friendly"}),
            "2": ("ai_pathfinding", {"start": [0, 0], "end": [5, 5], "obstacles": [[2, 2]]}),
            "3": ("ai_procedural", {"type": "dungeon", "size": [8, 8], "seed": 42}),
            "4": ("rt_reflections", {"resolution": [1920, 1080], "bounces": 2, "lights": 2}),
            "5": ("rt_shadows", {"quality": "medium", "lights": 3}),
            "6": ("rt_global_illumination", {"bounces": 2, "samples_per_pixel": 100}),
            "7": ("physics_rigid_body", {"num_objects": 20, "simulation_steps": 5}),
            "8": ("physics_fluid", {"grid_size": [32, 32, 32], "iterations": 10}),
            "9": ("physics_destruction", {"complexity": 100, "fracture_depth": 2}),
        }
        
        while self.connected:
            choice = input("Select task (1-9, 0=all, q=quit): ").strip()
            
            if choice == "q":
                break
            
            if choice == "0":
                # Run all tasks
                print("\n🚀 Running all tasks...")
                for key in sorted(tasks.keys()):
                    task_type, task_data = tasks[key]
                    print(f"\n[{key}] Testing: {task_type}")
                    
                    try:
                        result, latency = await self.submit_task(task_type, task_data)
                        proc_time = result.get("processing_time_ms", 0)
                        cost = result.get("cost_usd", 0)
                        cached = result.get("cached", False)
                        
                        print(f"  ✅ Success! Latency: {latency:.1f}ms")
                        print(f"  ⏱️  Processing: {proc_time:.1f}ms")
                        print(f"  💰 Cost: ${cost:.6f}")
                        if cached:
                            print(f"  📦 From cache (free!)")
                    except Exception as e:
                        print(f"  ❌ Failed: {e}")
                
                print(f"\n{'='*50}")
                print(f"✅ Demo complete!")
                print(f"💰 Total spent: ${self.total_spent:.6f}")
                print(f"⏱️  Avg latency: {self.total_latency_ms / self.tasks_completed:.1f}ms")
                
            elif choice in tasks:
                task_type, task_data = tasks[choice]
                print(f"\n🚀 Submitting: {task_type}")
                
                try:
                    result, latency = await self.submit_task(task_type, task_data)
                    
                    print(f"\n📥 Result:")
                    print(json.dumps(result.get("result", {}), indent=2))
                    print(f"\n⏱️  Latency: {latency:.1f}ms")
                    
                    if "processing_time_ms" in result:
                        print(f"⏱️  Processing: {result['processing_time_ms']:.1f}ms")
                    if "cost_usd" in result:
                        print(f"💰 Cost: ${result['cost_usd']:.6f}")
                    if result.get("cached"):
                        print(f"📦 From cache (free!)")
                    
                    print("\n✅ Task completed!")
                    
                except Exception as e:
                    print(f"\n❌ Task failed: {e}")
            else:
                print("❌ Invalid choice!")
    
    async def run_demo(self):
        """Run the interactive demo"""
        if not await self.connect():
            return
        
        # Start listen loop in background
        listen_task = asyncio.create_task(self.listen_loop())
        
        try:
            await self.interactive_demo()
        except KeyboardInterrupt:
            print("\n\n👋 Gamer client shutting down...")
        finally:
            if self.ws:
                await self.ws.close()
            listen_task.cancel()
            
            # Final stats
            uptime_mins = (time.time() - self.start_time) / 60
            print(f"\n📊 Session Summary:")
            print(f"   Session time: {uptime_mins:.1f} minutes")
            print(f"   Tasks completed: {self.tasks_completed}/{self.tasks_submitted}")
            print(f"   Total spent: ${self.total_spent:.6f}")
            print(f"   Avg cost/task: ${self.total_spent/max(self.tasks_completed,1):.6f}")
            
            # Savings comparison
            local_gpu_cost = uptime_mins / 60 * 2.00  # $2/hour local GPU
            savings = local_gpu_cost - self.total_spent
            savings_pct = (savings / local_gpu_cost * 100) if local_gpu_cost > 0 else 0
            
            if savings > 0:
                print(f"\n💰 Savings vs local GPU:")
                print(f"   Local GPU would cost: ${local_gpu_cost:.6f}")
                print(f"   P2C2R cost: ${self.total_spent:.6f}")
                print(f"   You saved: ${savings:.6f} ({savings_pct:.1f}% cheaper!)")


def main():
    parser = argparse.ArgumentParser(description="P2C2R Gamer Client - Device 3 (Renter)")
    parser.add_argument("--cloud-ip", required=True,
                       help="IP address of cloud coordinator (Device 2)")
    parser.add_argument("--cloud-port", type=int, default=DEFAULT_CLOUD_PORT,
                       help=f"Port of cloud coordinator (default: {DEFAULT_CLOUD_PORT})")
    parser.add_argument("--gamer-id",
                       help="Custom gamer ID (default: auto-generated)")
    
    args = parser.parse_args()
    
    gamer = GamerClient(args.cloud_ip, args.cloud_port, args.gamer_id)
    
    try:
        asyncio.run(gamer.run_demo())
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")


if __name__ == "__main__":
    main()
