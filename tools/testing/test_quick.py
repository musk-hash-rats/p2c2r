#!/usr/bin/env python3
"""
Quick test runner for P2C2R functionality
Provides a simple menu to test individual features
"""

import asyncio
import websockets
import json
import time
from typing import Dict, Any

class QuickTester:
    def __init__(self):
        self.ws = None
        self.coordinator_url = "ws://localhost:8765"
        
    async def connect(self):
        """Connect to the cloud coordinator"""
        print("🔌 Connecting to coordinator...")
        try:
            self.ws = await websockets.connect(self.coordinator_url)
            # Register as user
            await self.ws.send(json.dumps({
                "type": "register_user",
                "user_id": "test_user"
            }))
            response = await self.ws.recv()
            print(f"✅ Connected: {response}\n")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print("Make sure ./run_network.sh is running!")
            return False
    
    async def test_task(self, task_type: str, task_data: Dict[str, Any]):
        """Test a single task"""
        start_time = time.time()
        
        # Submit task
        await self.ws.send(json.dumps({
            "type": "submit_task",
            "task": {
                "type": task_type,
                "data": task_data
            }
        }))
        
        # Wait for result
        response = await self.ws.recv()
        end_time = time.time()
        
        result = json.loads(response)
        latency_ms = (end_time - start_time) * 1000
        
        return result, latency_ms
    
    async def run_menu(self):
        """Interactive menu for testing"""
        if not await self.connect():
            return
        
        tasks = {
            "1": ("AI: NPC Dialogue", "ai_npc_dialogue", {
                "character": "Merchant",
                "context": "player wants to trade",
                "personality": "friendly"
            }),
            "2": ("AI: Pathfinding", "ai_pathfinding", {
                "start": [0, 0],
                "end": [5, 5],
                "obstacles": [[2, 2]]
            }),
            "3": ("AI: Procedural", "ai_procedural", {
                "type": "dungeon",
                "size": [10, 10],
                "seed": 42
            }),
            "4": ("RT: Reflections", "rt_reflections", {
                "resolution": [1920, 1080],
                "bounces": 2,
                "lights": 2
            }),
            "5": ("RT: Shadows", "rt_shadows", {
                "quality": "medium",
                "lights": 3
            }),
            "6": ("RT: Global Illumination", "rt_global_illumination", {
                "bounces": 2,
                "samples_per_pixel": 100
            }),
            "7": ("Physics: Rigid Body", "physics_rigid_body", {
                "num_objects": 20,
                "simulation_steps": 5
            }),
            "8": ("Physics: Fluid", "physics_fluid", {
                "grid_size": [32, 32, 32],
                "iterations": 10
            }),
            "9": ("Physics: Destruction", "physics_destruction", {
                "complexity": 100,
                "fracture_depth": 2
            }),
            "0": ("Run All Tests", "all", {}),
            "q": ("Quit", "quit", {})
        }
        
        while True:
            print("\n" + "="*50)
            print("🎮 P2C2R Quick Tester")
            print("="*50)
            print("\nSelect a task to test:")
            print()
            for key, (name, _, _) in tasks.items():
                print(f"  [{key}] {name}")
            print()
            
            choice = input("Enter choice: ").strip().lower()
            
            if choice not in tasks:
                print("❌ Invalid choice!")
                continue
            
            name, task_type, task_data = tasks[choice]
            
            if task_type == "quit":
                print("👋 Goodbye!")
                break
            
            if task_type == "all":
                print("\n🚀 Running all tests...")
                total_time = 0
                successes = 0
                
                for key in sorted(tasks.keys()):
                    if key in ["0", "q"]:
                        continue
                    
                    test_name, test_type, test_data = tasks[key]
                    print(f"\n[{key}] Testing: {test_name}")
                    
                    try:
                        result, latency = await self.test_task(test_type, test_data)
                        total_time += latency
                        successes += 1
                        
                        print(f"  ✅ Success! Latency: {latency:.1f}ms")
                        if "processing_time_ms" in result.get("result", {}):
                            print(f"  ⏱️  Processing: {result['result']['processing_time_ms']:.1f}ms")
                    except Exception as e:
                        print(f"  ❌ Failed: {e}")
                
                print(f"\n{'='*50}")
                print(f"✅ Completed {successes}/9 tests")
                print(f"⏱️  Total time: {total_time/1000:.2f}s")
                print(f"📊 Average latency: {total_time/successes:.1f}ms")
                
            else:
                print(f"\n🚀 Testing: {name}")
                print(f"📤 Input: {json.dumps(task_data, indent=2)}")
                
                try:
                    result, latency = await self.test_task(task_type, task_data)
                    
                    print(f"\n📥 Result:")
                    print(json.dumps(result, indent=2))
                    print(f"\n⏱️  Latency: {latency:.1f}ms")
                    
                    if "processing_time_ms" in result.get("result", {}):
                        proc_time = result["result"]["processing_time_ms"]
                        network_time = latency - proc_time
                        print(f"⏱️  Processing: {proc_time:.1f}ms")
                        print(f"🌐 Network: {network_time:.1f}ms")
                    
                    print("\n✅ Test passed!")
                    
                except Exception as e:
                    print(f"\n❌ Test failed: {e}")
        
        if self.ws:
            await self.ws.close()

async def main():
    tester = QuickTester()
    await tester.run_menu()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
