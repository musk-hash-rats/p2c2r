#!/usr/bin/env python3
"""
Network Frame Processing Demo

Demonstrates frame processing over WebSocket network.
Run this to see gamer → coordinator → peers → back to gamer flow!
"""

import asyncio
import io
import time
from PIL import Image, ImageDraw
from frame_network import FrameCoordinator, NetworkFramePeer, NetworkFrameGamer
from frame_upscaler import UpscaleMethod


def create_test_frame(frame_num: int) -> bytes:
    """Create a test frame."""
    img = Image.new('RGB', (1280, 720), color=(30, 30, 60))
    draw = ImageDraw.Draw(img)
    
    # Grid
    for i in range(0, 1280, 80):
        draw.line([(i, 0), (i, 720)], fill=(50, 50, 80), width=1)
    for i in range(0, 720, 80):
        draw.line([(0, i), (1280, i)], fill=(50, 50, 80), width=1)
    
    # Frame number
    draw.text((50, 50), f"Frame #{frame_num}", fill=(255, 255, 255))
    
    # Moving circle (simulates animation)
    x = (frame_num * 50) % 1200
    draw.ellipse([x, 300, x+80, 380], fill=(255, 100, 100))
    
    # Compress
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    return buffer.getvalue()


async def run_coordinator():
    """Run the coordinator server."""
    print("🌐 Starting Frame Coordinator...")
    coordinator = FrameCoordinator(host="0.0.0.0", port=8765)
    await coordinator.start()


async def run_peer(peer_id: str, method: UpscaleMethod):
    """Run a peer worker."""
    print(f"🔧 Starting Peer {peer_id} with {method.value}...")
    peer = NetworkFramePeer(
        peer_id=peer_id,
        coordinator_uri="ws://localhost:8765",
        upscale_method=method
    )
    await peer.connect_and_run()


async def run_gamer_demo():
    """Run a gamer demo that submits frames."""
    print("🎮 Starting Gamer Demo...")
    await asyncio.sleep(2)  # Wait for coordinator and peers
    
    gamer = NetworkFrameGamer(
        gamer_id="demo_gamer",
        coordinator_uri="ws://localhost:8765"
    )
    
    await gamer.connect()
    print("✓ Gamer connected")
    
    # Submit 5 frames
    print("\nSubmitting 5 frames for processing...")
    frame_ids = []
    
    for i in range(5):
        frame_data = create_test_frame(i)
        frame_id = await gamer.submit_frame(frame_data)
        frame_ids.append(frame_id)
        print(f"  ✓ Submitted frame {frame_id} ({len(frame_data)/1024:.1f}KB)")
        await asyncio.sleep(0.033)  # 30fps
    
    # Collect results
    print("\nCollecting processed frames...")
    for frame_id in frame_ids:
        start = time.time()
        result = await gamer.get_frame_result(frame_id)
        latency = time.time() - start
        
        if result:
            img = Image.open(io.BytesIO(result))
            print(f"  ✓ Frame {frame_id}: {img.size}, {len(result)/1024:.1f}KB, {latency*1000:.1f}ms latency")
        else:
            print(f"  ✗ Frame {frame_id}: Failed")
    
    await gamer.disconnect()
    print("\n✅ Demo complete!")


async def run_all_demo():
    """Run coordinator, peers, and gamer in one process for demo."""
    print("=" * 70)
    print("Frame Processing Network Demo")
    print("=" * 70)
    print("\nStarting all components...")
    print()
    
    # Start coordinator
    coord_task = asyncio.create_task(run_coordinator())
    await asyncio.sleep(1)
    
    # Start 3 peers with different methods
    peer_tasks = [
        asyncio.create_task(run_peer("peer_fast", UpscaleMethod.OPENCV_CUBIC)),
        asyncio.create_task(run_peer("peer_quality", UpscaleMethod.OPENCV_LANCZOS)),
        asyncio.create_task(run_peer("peer_pil", UpscaleMethod.LANCZOS)),
    ]
    await asyncio.sleep(1)
    
    # Run gamer demo
    try:
        await run_gamer_demo()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        # Cleanup
        coord_task.cancel()
        for task in peer_tasks:
            task.cancel()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "coordinator":
            asyncio.run(run_coordinator())
        elif cmd == "peer" and len(sys.argv) > 2:
            peer_id = sys.argv[2]
            method_str = sys.argv[3] if len(sys.argv) > 3 else "opencv_cubic"
            method = UpscaleMethod(method_str)
            asyncio.run(run_peer(peer_id, method))
        elif cmd == "gamer":
            asyncio.run(run_gamer_demo())
        else:
            print("Usage:")
            print("  python demo_frame_network.py coordinator")
            print("  python demo_frame_network.py peer <peer_id> [method]")
            print("  python demo_frame_network.py gamer")
            print("\nOr run all-in-one demo:")
            print("  python demo_frame_network.py")
    else:
        # Run all-in-one demo
        asyncio.run(run_all_demo())
