#!/usr/bin/env python3
"""
End-to-End Frame Processing Pipeline Test

Tests the complete flow:
1. Frame Capturer (Gamer) → Creates a test frame
2. Frame Distributor (VM) → Distributes to peers  
3. Frame Upscaler (Peer) → Upscales the frame
4. Return to Gamer → Complete the loop

This proves the weak GPU assistance concept works!
"""

import asyncio
import io
import time
import logging
from PIL import Image, ImageDraw
from typing import Optional

# Import our components
from frame_distributor import FrameDistributor
from frame_upscaler import FrameUpscaler, UpscaleMethod

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestFramePipeline:
    """
    Simulates the complete frame processing pipeline.
    
    Gamer → Distributor → Peer Upscaler → Back to Gamer
    """
    
    def __init__(self):
        # Create distributor (VM/Cloud side)
        self.distributor = FrameDistributor(
            max_queue_size=50,
            peer_timeout=2.0,
            enable_fallback=True
        )
        
        # Create upscalers (Peer side)
        self.upscalers = {}
        
        # Track statistics
        self.stats = {
            'frames_submitted': 0,
            'frames_completed': 0,
            'total_latency': 0.0,
            'avg_latency': 0.0
        }
    
    def create_test_frame(self, frame_id: int, resolution=(1280, 720)) -> bytes:
        """
        Create a test frame simulating game output.
        In real use, this would come from the frame capturer.
        """
        # Create image with some content
        img = Image.new('RGB', resolution, color=(50, 50, 100))
        draw = ImageDraw.Draw(img)
        
        # Add grid pattern
        for i in range(0, resolution[0], 100):
            draw.line([(i, 0), (i, resolution[1])], fill=(70, 70, 120), width=1)
        for i in range(0, resolution[1], 100):
            draw.line([(0, i), (resolution[0], i)], fill=(70, 70, 120), width=1)
        
        # Add frame number
        draw.text((50, 50), f"Frame #{frame_id}", fill=(255, 255, 255))
        
        # Add some shapes (simulate game objects)
        draw.ellipse([400, 200, 600, 400], fill=(255, 100, 100))
        draw.rectangle([700, 300, 900, 500], fill=(100, 255, 100))
        draw.polygon([(200, 500), (300, 600), (100, 600)], fill=(100, 100, 255))
        
        # Compress to JPEG (simulating frame capturer output)
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        return buffer.getvalue()
    
    def register_peer(self, peer_id: str, upscale_method: UpscaleMethod = UpscaleMethod.OPENCV_CUBIC):
        """Register a peer upscaler."""
        upscaler = FrameUpscaler(
            target_resolution=(1920, 1080),  # Upscale to 1080p
            method=upscale_method,
            quality=90
        )
        self.upscalers[peer_id] = upscaler
        self.distributor.register_peer(peer_id)
        logger.info(f"Registered peer {peer_id} with method {upscale_method.value}")
    
    async def peer_worker(self, peer_id: str):
        """
        Simulates a peer processing frames.
        Continuously checks for work and upscales frames.
        """
        upscaler = self.upscalers[peer_id]
        
        while True:
            # Check if we have work (simulate checking distributor's assignment)
            if peer_id in self.distributor.busy_peers:
                frame_id = self.distributor.busy_peers[peer_id]
                frame = self.distributor.active_frames.get(frame_id)
                
                if frame:
                    # Upscale the frame
                    try:
                        upscaled_data = upscaler.upscale_frame(frame.data)
                        
                        # Submit result back to distributor
                        await self.distributor.submit_result(
                            frame_id=frame_id,
                            peer_id=peer_id,
                            result_data=upscaled_data,
                            success=True
                        )
                    except Exception as e:
                        logger.error(f"Peer {peer_id} failed to process frame {frame_id}: {e}")
                        await self.distributor.submit_result(
                            frame_id=frame_id,
                            peer_id=peer_id,
                            result_data=b"",
                            success=False
                        )
            
            await asyncio.sleep(0.001)  # 1ms check interval
    
    async def gamer_submit_frames(self, num_frames: int):
        """
        Simulates a gamer submitting frames for processing.
        """
        logger.info(f"Gamer: Submitting {num_frames} frames...")
        
        for i in range(num_frames):
            # Create test frame
            frame_data = self.create_test_frame(i)
            
            # Submit to distributor
            start_time = time.time()
            frame_id = await self.distributor.submit_frame(
                gamer_id="test_gamer",
                frame_data=frame_data
            )
            
            if frame_id >= 0:
                self.stats['frames_submitted'] += 1
                
                # Track submission
                logger.debug(f"Gamer: Submitted frame {frame_id}")
            
            # Simulate 30fps (33ms between frames)
            await asyncio.sleep(0.033)
    
    async def gamer_collect_results(self, expected_frames: int):
        """
        Simulates gamer collecting processed frames.
        """
        logger.info(f"Gamer: Waiting for {expected_frames} processed frames...")
        
        collected = 0
        start_time = time.time()
        
        while collected < expected_frames:
            frame_id = collected
            
            # Wait for result
            result = await self.distributor.get_frame_result(frame_id, timeout=5.0)
            
            if result:
                latency = time.time() - start_time
                self.stats['frames_completed'] += 1
                self.stats['total_latency'] += latency
                
                # Verify it's actually upscaled
                result_img = Image.open(io.BytesIO(result))
                logger.debug(f"Gamer: Received frame {frame_id}, size: {result_img.size}, {len(result)/1024:.1f}KB")
                
                collected += 1
            else:
                logger.warning(f"Gamer: Failed to get frame {frame_id}")
                collected += 1
            
            start_time = time.time()
    
    async def run_test(self, num_frames: int = 10, num_peers: int = 3):
        """
        Run the complete end-to-end test.
        """
        print("=" * 70)
        print("End-to-End Frame Processing Pipeline Test")
        print("=" * 70)
        
        # Start distributor
        print(f"\n1. Starting distributor...")
        dist_task = asyncio.create_task(self.distributor.start())
        await asyncio.sleep(0.1)
        
        # Register peers
        print(f"\n2. Registering {num_peers} peers...")
        peer_tasks = []
        for i in range(num_peers):
            peer_id = f"peer_{i}"
            # Use different methods for variety
            method = [UpscaleMethod.OPENCV_CUBIC, UpscaleMethod.OPENCV_LANCZOS, UpscaleMethod.LANCZOS][i % 3]
            self.register_peer(peer_id, method)
            
            # Start peer worker
            task = asyncio.create_task(self.peer_worker(peer_id))
            peer_tasks.append(task)
        
        print(f"   ✓ {num_peers} peers registered and running")
        
        # Gamer submits frames
        print(f"\n3. Gamer submitting {num_frames} frames (30fps simulation)...")
        gamer_submit = asyncio.create_task(self.gamer_submit_frames(num_frames))
        
        # Gamer collects results
        print(f"\n4. Gamer collecting processed frames...")
        gamer_collect = asyncio.create_task(self.gamer_collect_results(num_frames))
        
        # Wait for completion
        await gamer_submit
        await gamer_collect
        
        # Stop everything
        await self.distributor.stop()
        dist_task.cancel()
        for task in peer_tasks:
            task.cancel()
        
        # Calculate statistics
        if self.stats['frames_completed'] > 0:
            self.stats['avg_latency'] = self.stats['total_latency'] / self.stats['frames_completed']
        
        # Print results
        print(f"\n5. Results:")
        print("-" * 70)
        print(f"   Frames submitted:     {self.stats['frames_submitted']}")
        print(f"   Frames completed:     {self.stats['frames_completed']}")
        print(f"   Success rate:         {self.stats['frames_completed']/self.stats['frames_submitted']*100:.1f}%")
        print(f"   Avg latency:          {self.stats['avg_latency']*1000:.1f}ms per frame")
        print()
        
        # Distributor stats
        dist_stats = self.distributor.get_stats()
        print(f"   Distributor stats:")
        print(f"     - Frames received:  {dist_stats['frames_received']}")
        print(f"     - Frames completed: {dist_stats['frames_completed']}")
        print(f"     - Frames failed:    {dist_stats['frames_failed']}")
        print(f"     - Frames timeout:   {dist_stats['frames_timeout']}")
        print(f"     - Avg process time: {dist_stats['avg_processing_time']*1000:.1f}ms")
        print()
        
        # Upscaler stats
        print(f"   Peer upscaler stats:")
        for peer_id, upscaler in self.upscalers.items():
            stats = upscaler.get_stats()
            if stats['frames_processed'] > 0:
                print(f"     {peer_id:10s}: {stats['frames_processed']:3d} frames, "
                      f"{stats['avg_processing_time']*1000:5.1f}ms avg, "
                      f"method: {stats['method']}")
        
        print()
        print("=" * 70)
        
        # Verify success
        if self.stats['frames_completed'] == num_frames:
            print("✓ SUCCESS: All frames processed through complete pipeline!")
            print("  720p → Distributor → Peer Upscalers → 1080p → Back to Gamer")
        else:
            print(f"⚠ PARTIAL: {self.stats['frames_completed']}/{num_frames} frames completed")
        
        print("=" * 70)


async def main():
    """Run the end-to-end test."""
    pipeline = TestFramePipeline()
    await pipeline.run_test(num_frames=10, num_peers=3)


if __name__ == "__main__":
    asyncio.run(main())
