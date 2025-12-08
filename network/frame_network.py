#!/usr/bin/env python3
"""
Frame Processing Network Integration

Integrates frame processing pipeline with WebSocket network:
- Cloud Coordinator distributes frames to peers over WebSocket
- Peers receive frames, upscale them, and return results
- Gamers submit frames and get upscaled results back

This makes the weak GPU assistance work over the internet!
"""

import asyncio
import websockets
import json
import base64
import time
import logging
from typing import Dict, Optional, Set
from dataclasses import dataclass
from frame_distributor import FrameDistributor, Frame, FrameStatus
from frame_upscaler import FrameUpscaler, UpscaleMethod

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class FrameMessage:
    """Message format for frame processing over network."""
    msg_type: str  # frame_submit, frame_assign, frame_result, frame_request
    msg_id: str
    frame_id: int
    gamer_id: str
    peer_id: Optional[str] = None
    frame_data: Optional[str] = None  # Base64 encoded
    timestamp: float = 0.0
    
    def to_json(self) -> str:
        return json.dumps({
            'msg_type': self.msg_type,
            'msg_id': self.msg_id,
            'frame_id': self.frame_id,
            'gamer_id': self.gamer_id,
            'peer_id': self.peer_id,
            'frame_data': self.frame_data,
            'timestamp': self.timestamp
        })
    
    @staticmethod
    def from_json(json_str: str) -> 'FrameMessage':
        data = json.loads(json_str)
        return FrameMessage(**data)


class FrameCoordinator:
    """
    Cloud coordinator that distributes frames to peers over WebSocket.
    Integrates FrameDistributor with network layer.
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        self.host = host
        self.port = port
        
        # Frame distributor
        self.distributor = FrameDistributor(
            max_queue_size=100,
            peer_timeout=2.0,
            enable_fallback=True
        )
        
        # Network connections
        self.gamer_connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.peer_connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        
        # Track which frames belong to which gamers
        self.frame_to_gamer: Dict[int, str] = {}
        
        logger.info(f"Frame coordinator initialized on {host}:{port}")
    
    async def handle_connection(self, websocket):
        """Handle incoming WebSocket connections."""
        client_id = None
        client_type = None
        
        try:
            # Wait for registration
            msg_str = await websocket.recv()
            msg = json.loads(msg_str)
            
            if msg['msg_type'] == 'register_gamer':
                client_id = msg['gamer_id']
                client_type = 'gamer'
                self.gamer_connections[client_id] = websocket
                logger.info(f"Gamer {client_id} connected from {websocket.remote_address}")
                
                # Send acknowledgment
                await websocket.send(json.dumps({
                    'msg_type': 'registered',
                    'status': 'success',
                    'client_id': client_id
                }))
                
                # Handle gamer messages
                await self.handle_gamer(client_id, websocket)
                
            elif msg['msg_type'] == 'register_peer':
                client_id = msg['peer_id']
                client_type = 'peer'
                self.peer_connections[client_id] = websocket
                self.distributor.register_peer(client_id)
                logger.info(f"Peer {client_id} connected from {websocket.remote_address}")
                
                # Send acknowledgment
                await websocket.send(json.dumps({
                    'msg_type': 'registered',
                    'status': 'success',
                    'client_id': client_id
                }))
                
                # Handle peer messages
                await self.handle_peer(client_id, websocket)
            
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {client_id} ({client_type}) disconnected")
        except Exception as e:
            logger.error(f"Error handling connection: {e}")
        finally:
            # Cleanup
            if client_id and client_type == 'gamer' and client_id in self.gamer_connections:
                del self.gamer_connections[client_id]
            if client_id and client_type == 'peer' and client_id in self.peer_connections:
                del self.peer_connections[client_id]
                await self.distributor.unregister_peer(client_id)
    
    async def handle_gamer(self, gamer_id: str, websocket):
        """Handle messages from a gamer."""
        async for msg_str in websocket:
            try:
                msg = json.loads(msg_str)
                
                if msg['msg_type'] == 'frame_submit':
                    # Gamer submitting a frame for processing
                    frame_data_b64 = msg['frame_data']
                    frame_data = base64.b64decode(frame_data_b64)
                    
                    # Submit to distributor
                    frame_id = await self.distributor.submit_frame(gamer_id, frame_data)
                    self.frame_to_gamer[frame_id] = gamer_id
                    
                    # Send acknowledgment
                    await websocket.send(json.dumps({
                        'msg_type': 'frame_ack',
                        'frame_id': frame_id,
                        'status': 'queued'
                    }))
                    
                    logger.debug(f"Gamer {gamer_id} submitted frame {frame_id}")
                    
                elif msg['msg_type'] == 'frame_request':
                    # Gamer requesting processed frame
                    frame_id = msg['frame_id']
                    result_data = await self.distributor.get_frame_result(frame_id, timeout=5.0)
                    
                    if result_data:
                        # Send result
                        result_b64 = base64.b64encode(result_data).decode('utf-8')
                        await websocket.send(json.dumps({
                            'msg_type': 'frame_result',
                            'frame_id': frame_id,
                            'frame_data': result_b64,
                            'status': 'completed'
                        }))
                        logger.debug(f"Sent frame {frame_id} result to gamer {gamer_id}")
                    else:
                        # Frame not ready or failed
                        await websocket.send(json.dumps({
                            'msg_type': 'frame_result',
                            'frame_id': frame_id,
                            'status': 'failed'
                        }))
                
            except Exception as e:
                logger.error(f"Error handling gamer message: {e}")
    
    async def handle_peer(self, peer_id: str, websocket):
        """Handle messages from a peer."""
        # Start sending work to this peer
        asyncio.create_task(self.assign_work_to_peer(peer_id, websocket))
        
        # Handle peer responses
        async for msg_str in websocket:
            try:
                msg = json.loads(msg_str)
                
                if msg['msg_type'] == 'frame_result':
                    # Peer returning processed frame
                    frame_id = msg['frame_id']
                    result_b64 = msg['frame_data']
                    result_data = base64.b64decode(result_b64)
                    success = msg.get('status') == 'completed'
                    
                    # Submit result to distributor
                    await self.distributor.submit_result(
                        frame_id=frame_id,
                        peer_id=peer_id,
                        result_data=result_data,
                        success=success
                    )
                    
                    logger.debug(f"Peer {peer_id} completed frame {frame_id}")
                
            except Exception as e:
                logger.error(f"Error handling peer message: {e}")
    
    async def assign_work_to_peer(self, peer_id: str, websocket):
        """Continuously assign work to a peer."""
        while peer_id in self.peer_connections:
            try:
                # Check if peer has work assigned
                if peer_id in self.distributor.busy_peers:
                    frame_id = self.distributor.busy_peers[peer_id]
                    
                    if frame_id in self.distributor.active_frames:
                        frame = self.distributor.active_frames[frame_id]
                        
                        # Send frame to peer
                        frame_b64 = base64.b64encode(frame.data).decode('utf-8')
                        await websocket.send(json.dumps({
                            'msg_type': 'frame_assign',
                            'frame_id': frame_id,
                            'frame_data': frame_b64,
                            'timestamp': time.time()
                        }))
                        
                        logger.debug(f"Assigned frame {frame_id} to peer {peer_id}")
                        
                        # Wait a bit before checking again
                        await asyncio.sleep(0.1)
                else:
                    # No work, wait a bit
                    await asyncio.sleep(0.01)
                    
            except websockets.exceptions.ConnectionClosed:
                break
            except Exception as e:
                logger.error(f"Error assigning work to peer {peer_id}: {e}")
                await asyncio.sleep(0.1)
    
    async def start(self):
        """Start the frame coordinator server."""
        # Start distributor
        asyncio.create_task(self.distributor.start())
        
        # Start WebSocket server
        async with websockets.serve(self.handle_connection, self.host, self.port):
            logger.info(f"Frame coordinator listening on ws://{self.host}:{self.port}")
            await asyncio.Future()  # Run forever


class NetworkFramePeer:
    """
    Peer that connects to coordinator and processes frames.
    """
    
    def __init__(
        self,
        peer_id: str,
        coordinator_uri: str = "ws://localhost:8765",
        upscale_method: UpscaleMethod = UpscaleMethod.OPENCV_CUBIC
    ):
        self.peer_id = peer_id
        self.coordinator_uri = coordinator_uri
        
        # Frame upscaler
        self.upscaler = FrameUpscaler(
            target_resolution=(1920, 1080),
            method=upscale_method,
            quality=90
        )
        
        self.websocket = None
        logger.info(f"Peer {peer_id} initialized with method {upscale_method.value}")
    
    async def connect_and_run(self):
        """Connect to coordinator and process frames."""
        async with websockets.connect(self.coordinator_uri) as websocket:
            self.websocket = websocket
            
            # Register as peer
            await websocket.send(json.dumps({
                'msg_type': 'register_peer',
                'peer_id': self.peer_id
            }))
            
            # Wait for acknowledgment
            msg = json.loads(await websocket.recv())
            if msg['msg_type'] == 'registered':
                logger.info(f"Peer {self.peer_id} registered successfully")
            
            # Process frames
            async for msg_str in websocket:
                try:
                    msg = json.loads(msg_str)
                    
                    if msg['msg_type'] == 'frame_assign':
                        # Received frame to process
                        frame_id = msg['frame_id']
                        frame_b64 = msg['frame_data']
                        frame_data = base64.b64decode(frame_b64)
                        
                        logger.debug(f"Peer {self.peer_id} received frame {frame_id}")
                        
                        # Upscale the frame
                        start_time = time.time()
                        upscaled_data = self.upscaler.upscale_frame(frame_data)
                        process_time = time.time() - start_time
                        
                        logger.debug(f"Peer {self.peer_id} upscaled frame {frame_id} in {process_time*1000:.1f}ms")
                        
                        # Send result back
                        result_b64 = base64.b64encode(upscaled_data).decode('utf-8')
                        await websocket.send(json.dumps({
                            'msg_type': 'frame_result',
                            'frame_id': frame_id,
                            'frame_data': result_b64,
                            'status': 'completed',
                            'process_time': process_time
                        }))
                        
                except Exception as e:
                    logger.error(f"Peer {self.peer_id} error processing frame: {e}")


class NetworkFrameGamer:
    """
    Gamer client that submits frames and gets upscaled results.
    """
    
    def __init__(self, gamer_id: str, coordinator_uri: str = "ws://localhost:8765"):
        self.gamer_id = gamer_id
        self.coordinator_uri = coordinator_uri
        self.websocket = None
        logger.info(f"Gamer {gamer_id} initialized")
    
    async def connect(self):
        """Connect to coordinator."""
        self.websocket = await websockets.connect(self.coordinator_uri)
        
        # Register as gamer
        await self.websocket.send(json.dumps({
            'msg_type': 'register_gamer',
            'gamer_id': self.gamer_id
        }))
        
        # Wait for acknowledgment
        msg = json.loads(await self.websocket.recv())
        if msg['msg_type'] == 'registered':
            logger.info(f"Gamer {self.gamer_id} registered successfully")
    
    async def submit_frame(self, frame_data: bytes) -> int:
        """Submit a frame for processing."""
        frame_b64 = base64.b64encode(frame_data).decode('utf-8')
        
        await self.websocket.send(json.dumps({
            'msg_type': 'frame_submit',
            'frame_data': frame_b64
        }))
        
        # Wait for acknowledgment
        msg = json.loads(await self.websocket.recv())
        return msg['frame_id']
    
    async def get_frame_result(self, frame_id: int) -> Optional[bytes]:
        """Request processed frame result."""
        await self.websocket.send(json.dumps({
            'msg_type': 'frame_request',
            'frame_id': frame_id
        }))
        
        # Wait for result
        msg = json.loads(await self.websocket.recv())
        
        if msg['status'] == 'completed':
            result_b64 = msg['frame_data']
            return base64.b64decode(result_b64)
        
        return None
    
    async def disconnect(self):
        """Disconnect from coordinator."""
        if self.websocket:
            await self.websocket.close()


# Example usage
async def test_network_integration():
    """Test the network-integrated frame processing."""
    print("=" * 70)
    print("Frame Processing Network Integration Test")
    print("=" * 70)
    
    # This would be run in separate processes/machines:
    # 1. Run coordinator: python -c "from frame_network import FrameCoordinator; ..."
    # 2. Run peers: python -c "from frame_network import NetworkFramePeer; ..."
    # 3. Run gamer: python -c "from frame_network import NetworkFrameGamer; ..."
    
    print("\nTo test this network integration:")
    print("1. Run coordinator: python network/frame_network.py --coordinator")
    print("2. Run peer(s): python network/frame_network.py --peer <peer_id>")
    print("3. Run gamer: python network/frame_network.py --gamer <gamer_id>")
    print("=" * 70)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--coordinator":
            coordinator = FrameCoordinator()
            asyncio.run(coordinator.start())
        elif sys.argv[1] == "--peer" and len(sys.argv) > 2:
            peer_id = sys.argv[2]
            peer = NetworkFramePeer(peer_id)
            asyncio.run(peer.connect_and_run())
        elif sys.argv[1] == "--gamer" and len(sys.argv) > 2:
            gamer_id = sys.argv[2]
            print("Gamer client ready. Use NetworkFrameGamer class in your code.")
        else:
            print("Usage:")
            print("  python frame_network.py --coordinator")
            print("  python frame_network.py --peer <peer_id>")
            print("  python frame_network.py --gamer <gamer_id>")
    else:
        asyncio.run(test_network_integration())
