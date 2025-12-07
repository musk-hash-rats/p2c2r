#!/usr/bin/env python3
"""
Frame Distributor - VM/Cloud component that distributes frames to peers
Part of P2C2R Phase 2: Game Integration
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class FrameStatus(Enum):
    """Status of a frame in the processing pipeline."""
    PENDING = "pending"           # Waiting to be distributed
    PROCESSING = "processing"     # Assigned to peer, being processed
    COMPLETED = "completed"       # Successfully processed
    FAILED = "failed"            # Processing failed
    TIMEOUT = "timeout"          # Peer took too long


@dataclass
class Frame:
    """Represents a captured frame from the gamer."""
    frame_id: int
    gamer_id: str
    data: bytes
    timestamp: float
    status: FrameStatus = FrameStatus.PENDING
    assigned_peer: Optional[str] = None
    result_data: Optional[bytes] = None
    processing_start: Optional[float] = None
    processing_end: Optional[float] = None
    
    def processing_time(self) -> Optional[float]:
        """Calculate how long this frame took to process."""
        if self.processing_start and self.processing_end:
            return self.processing_end - self.processing_start
        return None


class FrameDistributor:
    """
    Distributes frames from gamers to peers for processing.
    
    This is the VM/Cloud component that:
    1. Receives frames from gamers
    2. Distributes them to available peers
    3. Collects processed results
    4. Sends results back to gamers
    5. Handles timeouts and failures
    """
    
    def __init__(
        self,
        max_queue_size: int = 100,
        peer_timeout: float = 2.0,  # 2 seconds max processing time
        enable_fallback: bool = True
    ):
        """
        Initialize frame distributor.
        
        Args:
            max_queue_size: Maximum frames to queue before dropping
            peer_timeout: Max seconds to wait for peer to process frame
            enable_fallback: Use local fallback if peers fail
        """
        self.max_queue_size = max_queue_size
        self.peer_timeout = peer_timeout
        self.enable_fallback = enable_fallback
        
        # Frame management
        self.pending_frames: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self.active_frames: Dict[int, Frame] = {}  # frame_id -> Frame
        self.completed_frames: Dict[int, Frame] = {}  # frame_id -> Frame
        
        # Peer management
        self.available_peers: List[str] = []
        self.busy_peers: Dict[str, int] = {}  # peer_id -> frame_id
        
        # Statistics
        self.stats = {
            'frames_received': 0,
            'frames_completed': 0,
            'frames_failed': 0,
            'frames_timeout': 0,
            'fallback_used': 0,
            'avg_processing_time': 0.0
        }
        
        self.is_running = False
        logger.info(f"Frame distributor initialized: queue_size={max_queue_size}, timeout={peer_timeout}s")
    
    async def submit_frame(self, gamer_id: str, frame_data: bytes) -> int:
        """
        Submit a frame for processing.
        
        Args:
            gamer_id: ID of the gamer who sent this frame
            frame_data: Raw frame data (JPEG compressed)
            
        Returns:
            Frame ID for tracking
        """
        frame_id = self.stats['frames_received']
        frame = Frame(
            frame_id=frame_id,
            gamer_id=gamer_id,
            data=frame_data,
            timestamp=time.time()
        )
        
        try:
            await self.pending_frames.put(frame)
            self.stats['frames_received'] += 1
            logger.debug(f"Frame {frame_id} queued from gamer {gamer_id}")
            return frame_id
        except asyncio.QueueFull:
            logger.warning(f"Frame queue full! Dropping frame from {gamer_id}")
            return -1
    
    async def get_frame_result(self, frame_id: int, timeout: float = 5.0) -> Optional[bytes]:
        """
        Get the processed result for a frame.
        
        Args:
            frame_id: Frame to get result for
            timeout: Max seconds to wait
            
        Returns:
            Processed frame data, or None if not ready/failed
        """
        start = time.time()
        while time.time() - start < timeout:
            if frame_id in self.completed_frames:
                frame = self.completed_frames[frame_id]
                if frame.status == FrameStatus.COMPLETED:
                    return frame.result_data
                else:
                    logger.warning(f"Frame {frame_id} failed: {frame.status}")
                    return None
            await asyncio.sleep(0.001)  # 1ms polling (10x faster)
        
        logger.warning(f"Timeout waiting for frame {frame_id} result")
        return None
    
    def register_peer(self, peer_id: str):
        """Register a peer as available for work."""
        if peer_id not in self.available_peers:
            self.available_peers.append(peer_id)
            logger.info(f"Peer {peer_id} registered. Total available: {len(self.available_peers)}")
    
    async def unregister_peer(self, peer_id: str):
        """Remove a peer from available pool."""
        if peer_id in self.available_peers:
            self.available_peers.remove(peer_id)
            logger.info(f"Peer {peer_id} unregistered. Total available: {len(self.available_peers)}")
        
        # Handle if peer was processing a frame
        if peer_id in self.busy_peers:
            frame_id = self.busy_peers[peer_id]
            if frame_id in self.active_frames:
                frame = self.active_frames[frame_id]
                logger.warning(f"Peer {peer_id} disconnected while processing frame {frame_id}")
                # Re-queue the frame
                await self.pending_frames.put(frame)
                del self.active_frames[frame_id]
            del self.busy_peers[peer_id]
    
    async def distribute_frames(self):
        """
        Main distribution loop.
        Continuously distributes pending frames to available peers.
        """
        logger.info("Frame distribution started")
        
        while self.is_running:
            # Check for available peer and pending frame
            if not self.available_peers or self.pending_frames.empty():
                await asyncio.sleep(0.001)  # 1ms (10x faster)
                continue
            
            # Get next frame and peer
            frame = await self.pending_frames.get()
            peer_id = self.available_peers.pop(0)
            
            # Assign frame to peer
            frame.status = FrameStatus.PROCESSING
            frame.assigned_peer = peer_id
            frame.processing_start = time.time()
            
            self.active_frames[frame.frame_id] = frame
            self.busy_peers[peer_id] = frame.frame_id
            
            logger.debug(f"Frame {frame.frame_id} assigned to peer {peer_id}")
            
            # Start timeout monitor for this frame
            asyncio.create_task(self._monitor_frame_timeout(frame.frame_id))
    
    async def _monitor_frame_timeout(self, frame_id: int):
        """
        Monitor a frame for timeout.
        If peer takes too long, mark as timeout and optionally use fallback.
        """
        await asyncio.sleep(self.peer_timeout)
        
        # Check if frame is still processing
        if frame_id in self.active_frames:
            frame = self.active_frames[frame_id]
            if frame.status == FrameStatus.PROCESSING:
                logger.warning(f"Frame {frame_id} timed out (peer: {frame.assigned_peer})")
                frame.status = FrameStatus.TIMEOUT
                self.stats['frames_timeout'] += 1
                
                # Free up the peer
                if frame.assigned_peer in self.busy_peers:
                    del self.busy_peers[frame.assigned_peer]
                    self.available_peers.append(frame.assigned_peer)
                
                # Use fallback if enabled
                if self.enable_fallback:
                    logger.info(f"Using fallback for frame {frame_id}")
                    result = await self._fallback_process(frame.data)
                    await self.submit_result(frame_id, frame.assigned_peer, result, success=True)
                    self.stats['fallback_used'] += 1
                else:
                    # Move to completed with failure status
                    self.completed_frames[frame_id] = frame
                    del self.active_frames[frame_id]
    
    async def _fallback_process(self, frame_data: bytes) -> bytes:
        """
        Fallback processing when peers fail/timeout.
        For now, just returns original frame. In real impl, would do local upscaling.
        """
        logger.debug("Fallback: returning original frame (no processing)")
        # No artificial delay - return immediately for speed
        return frame_data
    
    async def submit_result(
        self,
        frame_id: int,
        peer_id: str,
        result_data: bytes,
        success: bool = True
    ):
        """
        Peer submits a processed frame result.
        
        Args:
            frame_id: Frame that was processed
            peer_id: Peer that processed it
            result_data: Processed frame data
            success: Whether processing succeeded
        """
        if frame_id not in self.active_frames:
            logger.warning(f"Received result for unknown frame {frame_id}")
            return
        
        frame = self.active_frames[frame_id]
        frame.processing_end = time.time()
        frame.result_data = result_data
        
        if success:
            frame.status = FrameStatus.COMPLETED
            self.stats['frames_completed'] += 1
            
            # Update avg processing time
            if frame.processing_time():
                old_avg = self.stats['avg_processing_time']
                count = self.stats['frames_completed']
                new_avg = (old_avg * (count - 1) + frame.processing_time()) / count
                self.stats['avg_processing_time'] = new_avg
            
            logger.debug(f"Frame {frame_id} completed by {peer_id} in {frame.processing_time():.3f}s")
        else:
            frame.status = FrameStatus.FAILED
            self.stats['frames_failed'] += 1
            logger.warning(f"Frame {frame_id} failed processing by {peer_id}")
        
        # Move to completed and free peer
        self.completed_frames[frame_id] = frame
        del self.active_frames[frame_id]
        
        if peer_id in self.busy_peers:
            del self.busy_peers[peer_id]
            self.available_peers.append(peer_id)
    
    async def start(self):
        """Start the frame distributor."""
        self.is_running = True
        await self.distribute_frames()
    
    async def stop(self):
        """Stop the frame distributor."""
        self.is_running = False
        logger.info("Frame distributor stopped")
        logger.info(f"Final stats: {self.stats}")
    
    def get_stats(self) -> dict:
        """Get current statistics."""
        return {
            **self.stats,
            'pending_frames': self.pending_frames.qsize(),
            'active_frames': len(self.active_frames),
            'available_peers': len(self.available_peers),
            'busy_peers': len(self.busy_peers)
        }


async def test_frame_distributor():
    """Test the frame distributor."""
    print("=" * 60)
    print("Frame Distributor Performance Test")
    print("=" * 60)
    
    # Create distributor with faster timeout
    distributor = FrameDistributor(
        max_queue_size=100,
        peer_timeout=0.5,  # Faster timeout
        enable_fallback=True
    )
    
    # Start distributor
    dist_task = asyncio.create_task(distributor.start())
    
    # Register more peers for parallel processing
    print("\n1. Registering peers...")
    for i in range(10):
        distributor.register_peer(f"peer_{i}")
    print(f"   ✓ {len(distributor.available_peers)} peers registered")
    
    # Submit more frames to test throughput
    print("\n2. Submitting frames...")
    start_time = time.time()
    frame_ids = []
    for i in range(50):
        frame_id = await distributor.submit_frame(
            gamer_id="test_gamer",
            frame_data=f"frame_{i}_data".encode()
        )
        frame_ids.append(frame_id)
    submit_time = time.time() - start_time
    print(f"   ✓ {len(frame_ids)} frames submitted in {submit_time:.3f}s")
    print(f"   ✓ Submission rate: {len(frame_ids)/submit_time:.1f} frames/sec")
    
    # Simulate fast peer processing
    print("\n3. Simulating peer processing...")
    process_start = time.time()
    await asyncio.sleep(0.05)  # Let distributor assign frames
    
    # Process assigned frames rapidly
    processed = 0
    while distributor.active_frames:
        for frame_id, frame in list(distributor.active_frames.items()):
            # Simulate very fast processing
            result = f"processed_{frame_id}".encode()
            await distributor.submit_result(
                frame_id=frame_id,
                peer_id=frame.assigned_peer,
                result_data=result,
                success=True
            )
            processed += 1
        await asyncio.sleep(0.001)  # 1ms between batches
    
    process_time = time.time() - process_start
    print(f"   ✓ {processed} frames processed in {process_time:.3f}s")
    print(f"   ✓ Processing rate: {processed/process_time:.1f} frames/sec")
    
    # Wait a bit for completion
    await asyncio.sleep(0.1)
    
    # Get stats
    print("\n4. Performance Statistics:")
    stats = distributor.get_stats()
    
    total_time = time.time() - start_time
    throughput = stats['frames_completed'] / total_time
    
    print(f"   frames_received: {stats['frames_received']}")
    print(f"   frames_completed: {stats['frames_completed']}")
    print(f"   frames_failed: {stats['frames_failed']}")
    print(f"   frames_timeout: {stats['frames_timeout']}")
    print(f"   fallback_used: {stats['fallback_used']}")
    print(f"   avg_processing_time: {stats['avg_processing_time']:.3f}s")
    print(f"   available_peers: {stats['available_peers']}")
    print(f"   ")
    print(f"   📊 OVERALL THROUGHPUT: {throughput:.1f} frames/sec")
    print(f"   📊 TOTAL TIME: {total_time:.3f}s")
    
    # Calculate frames per second capability
    if stats['avg_processing_time'] > 0:
        theoretical_fps = len(distributor.available_peers) / stats['avg_processing_time']
        print(f"   📊 THEORETICAL MAX: {theoretical_fps:.1f} fps with {len(distributor.available_peers)} peers")
    
    # Stop distributor
    await distributor.stop()
    dist_task.cancel()
    
    print("\n" + "=" * 60)
    print("✓ Frame Distributor Performance Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_frame_distributor())
