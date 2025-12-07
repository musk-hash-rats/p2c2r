#!/usr/bin/env python3
"""
Frame Capturer - Captures screen frames for distributed processing
Part of P2C2R Phase 2: Game Integration
"""

import time
import io
from typing import Optional, Tuple
from PIL import Image, ImageGrab
import logging

logger = logging.getLogger(__name__)


class FrameCapturer:
    """
    Captures screen frames at specified intervals.
    Used by gamer client to capture game output for distributed rendering.
    """
    
    def __init__(
        self,
        fps: int = 30,
        resolution: Optional[Tuple[int, int]] = None,
        quality: int = 85,
        region: Optional[Tuple[int, int, int, int]] = None
    ):
        """
        Initialize frame capturer.
        
        Args:
            fps: Frames per second to capture (default: 30)
            resolution: Target resolution (width, height). None = native
            quality: JPEG quality 1-100 (default: 85)
            region: Screen region to capture (x, y, width, height). None = full screen
        """
        self.fps = fps
        self.target_resolution = resolution
        self.quality = quality
        self.region = region
        self.frame_interval = 1.0 / fps
        self.is_capturing = False
        self.frame_count = 0
        
        logger.info(f"Frame capturer initialized: {fps}fps, quality={quality}")
        if resolution:
            logger.info(f"Target resolution: {resolution[0]}x{resolution[1]}")
        if region:
            logger.info(f"Capture region: {region}")
    
    def capture_frame(self) -> Optional[bytes]:
        """
        Capture a single frame from screen.
        
        Returns:
            JPEG-compressed frame as bytes, or None if capture failed
        """
        try:
            # Capture screen
            if self.region:
                # Capture specific region (x, y, x+width, y+height)
                x, y, w, h = self.region
                screenshot = ImageGrab.grab(bbox=(x, y, x + w, y + h))
            else:
                # Capture full screen
                screenshot = ImageGrab.grab()
            
            # Resize if target resolution specified
            if self.target_resolution:
                screenshot = screenshot.resize(
                    self.target_resolution,
                    Image.Resampling.LANCZOS
                )
            
            # Compress to JPEG
            buffer = io.BytesIO()
            screenshot.save(buffer, format='JPEG', quality=self.quality)
            frame_data = buffer.getvalue()
            
            self.frame_count += 1
            
            # Log every 100 frames
            if self.frame_count % 100 == 0:
                size_kb = len(frame_data) / 1024
                logger.info(f"Captured frame {self.frame_count} ({size_kb:.1f}KB)")
            
            return frame_data
            
        except Exception as e:
            logger.error(f"Failed to capture frame: {e}")
            return None
    
    def get_frame_info(self, frame_data: bytes) -> dict:
        """
        Get information about a captured frame.
        
        Args:
            frame_data: JPEG frame data
            
        Returns:
            Dictionary with frame metadata
        """
        try:
            img = Image.open(io.BytesIO(frame_data))
            return {
                'width': img.width,
                'height': img.height,
                'format': img.format,
                'size_bytes': len(frame_data),
                'size_kb': len(frame_data) / 1024
            }
        except Exception as e:
            logger.error(f"Failed to get frame info: {e}")
            return {}
    
    def set_capture_region(self, x: int, y: int, width: int, height: int):
        """
        Set specific screen region to capture.
        Useful for capturing just the game window.
        
        Args:
            x, y: Top-left corner position
            width, height: Region dimensions
        """
        self.region = (x, y, width, height)
        logger.info(f"Capture region set to: x={x}, y={y}, w={width}, h={height}")
    
    def clear_capture_region(self):
        """Reset to full screen capture."""
        self.region = None
        logger.info("Capture region cleared (full screen)")
    
    def start_continuous_capture(self, callback):
        """
        Start continuous frame capture (blocking).
        
        Args:
            callback: Function to call with each frame: callback(frame_data)
        """
        self.is_capturing = True
        logger.info(f"Starting continuous capture at {self.fps}fps...")
        
        frame_time = 0
        
        while self.is_capturing:
            start = time.time()
            
            # Capture frame
            frame_data = self.capture_frame()
            if frame_data:
                callback(frame_data)
            
            # Sleep to maintain target FPS
            elapsed = time.time() - start
            sleep_time = max(0, self.frame_interval - elapsed)
            
            if sleep_time > 0:
                time.sleep(sleep_time)
            
            # Track actual FPS
            frame_time = time.time() - start
            actual_fps = 1.0 / frame_time if frame_time > 0 else 0
            
            # Log FPS every 100 frames
            if self.frame_count % 100 == 0:
                logger.info(f"Actual FPS: {actual_fps:.1f} (target: {self.fps})")
    
    def stop_capture(self):
        """Stop continuous frame capture."""
        self.is_capturing = False
        logger.info(f"Frame capture stopped. Total frames: {self.frame_count}")


def test_frame_capturer():
    """Test the frame capturer."""
    print("=" * 60)
    print("Frame Capturer Test")
    print("=" * 60)
    
    # Create capturer (720p, 30fps)
    capturer = FrameCapturer(
        fps=30,
        resolution=(1280, 720),
        quality=85
    )
    
    print(f"\n1. Capturing single frame...")
    frame = capturer.capture_frame()
    
    if frame:
        info = capturer.get_frame_info(frame)
        print(f"   ✓ Frame captured:")
        print(f"     - Size: {info['width']}x{info['height']}")
        print(f"     - Format: {info['format']}")
        print(f"     - Data size: {info['size_kb']:.1f}KB")
    else:
        print("   ✗ Failed to capture frame")
    
    print(f"\n2. Capturing 5 frames at 30fps...")
    frames_captured = []
    
    def save_frame(frame_data):
        frames_captured.append(frame_data)
        if len(frames_captured) >= 5:
            capturer.stop_capture()
    
    import threading
    capture_thread = threading.Thread(
        target=capturer.start_continuous_capture,
        args=(save_frame,)
    )
    capture_thread.start()
    capture_thread.join()
    
    print(f"   ✓ Captured {len(frames_captured)} frames")
    total_size = sum(len(f) for f in frames_captured) / 1024
    print(f"   - Total size: {total_size:.1f}KB")
    print(f"   - Average: {total_size/len(frames_captured):.1f}KB per frame")
    
    print(f"\n3. Estimated bandwidth:")
    kb_per_second = (total_size / len(frames_captured)) * 30  # 30fps
    mb_per_second = kb_per_second / 1024
    print(f"   - At 30fps: {kb_per_second:.1f}KB/s ({mb_per_second:.2f}MB/s)")
    
    print("\n" + "=" * 60)
    print("✓ Frame Capturer Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_frame_capturer()
