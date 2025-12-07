"""
P2C2R Network Layer - Real Distributed System

Architecture:
1. Cloud Coordinator (server) - Orchestrates tasks, runs on cloud
2. Peer Nodes (workers) - Execute tasks, contribute GPU/CPU
3. User Client (renter) - Sends tasks, receives results

Communication: WebSocket (async, bidirectional, real-time)
"""

import asyncio
import websockets
import json
import time
import uuid
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


@dataclass
class NetworkMessage:
    """Message format for P2C2R network protocol."""
    msg_type: str  # register, heartbeat, task, result, error
    msg_id: str
    timestamp: float
    data: dict
    
    def to_json(self) -> str:
        return json.dumps({
            'msg_type': self.msg_type,
            'msg_id': self.msg_id,
            'timestamp': self.timestamp,
            'data': self.data
        })
    
    @staticmethod
    def from_json(json_str: str) -> 'NetworkMessage':
        data = json.loads(json_str)
        return NetworkMessage(**data)


@dataclass
class PeerInfo:
    """Information about a registered peer."""
    peer_id: str
    websocket: websockets.WebSocketServerProtocol
    ip_address: str
    capabilities: dict
    status: str  # idle, busy, offline
    current_task: Optional[str] = None
    tasks_completed: int = 0
    tasks_failed: int = 0
    avg_completion_time: float = 0.0
    last_heartbeat: float = 0.0


class CloudCoordinator:
    """
    Cloud Coordinator - Central server that orchestrates the P2C2R network.
    
    Responsibilities:
    - Accept peer registrations
    - Accept user connections
    - Assign tasks to best available peer
    - Handle peer failures and failover
    - Track peer performance metrics
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        self.host = host
        self.port = port
        self.peers: Dict[str, PeerInfo] = {}
        self.users: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.pending_tasks: Dict[str, dict] = {}
        self.task_results: Dict[str, dict] = {}
        self.logger = logging.getLogger("CloudCoordinator")
    
    async def start(self):
        """Start the coordinator server."""
        self.logger.info(f"🌩️  Starting Cloud Coordinator on {self.host}:{self.port}")
        
        async with websockets.serve(self.handle_connection, self.host, self.port):
            self.logger.info("✓ Cloud Coordinator is running!")
            self.logger.info(f"  Peers connect to: ws://{self.host}:{self.port}")
            self.logger.info(f"  Users connect to: ws://{self.host}:{self.port}")
            
            # Start background tasks
            asyncio.create_task(self.monitor_peers())
            
            await asyncio.Future()  # Run forever
    
    async def handle_connection(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """Handle incoming WebSocket connections."""
        client_ip = websocket.remote_address[0]
        self.logger.info(f"New connection from {client_ip}")
        
        try:
            async for message in websocket:
                await self.handle_message(websocket, message, client_ip)
        except websockets.exceptions.ConnectionClosed:
            self.logger.info(f"Connection closed: {client_ip}")
            await self.handle_disconnect(websocket)
        except Exception as e:
            self.logger.error(f"Error handling connection: {e}")
    
    async def handle_message(self, websocket, message: str, client_ip: str):
        """Process incoming messages."""
        try:
            msg = NetworkMessage.from_json(message)
            
            if msg.msg_type == "register_peer":
                await self.register_peer(websocket, msg, client_ip)
            
            elif msg.msg_type == "register_user":
                await self.register_user(websocket, msg)
            
            elif msg.msg_type == "heartbeat":
                await self.handle_heartbeat(msg)
            
            elif msg.msg_type == "task_request":
                await self.handle_task_request(websocket, msg)
            
            elif msg.msg_type == "task_result":
                await self.handle_task_result(msg)
            
            elif msg.msg_type == "task_failure":
                await self.handle_task_failure(msg)
            
            else:
                self.logger.warning(f"Unknown message type: {msg.msg_type}")
        
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
    
    async def register_peer(self, websocket, msg: NetworkMessage, ip: str):
        """Register a new peer node."""
        peer_id = msg.data['peer_id']
        capabilities = msg.data['capabilities']
        
        peer_info = PeerInfo(
            peer_id=peer_id,
            websocket=websocket,
            ip_address=ip,
            capabilities=capabilities,
            status='idle',
            last_heartbeat=time.time()
        )
        
        self.peers[peer_id] = peer_info
        self.logger.info(f"✓ Registered peer: {peer_id} from {ip}")
        self.logger.info(f"  Capabilities: GPU={capabilities.get('gpu', 'N/A')}, "
                        f"CPU cores={capabilities.get('cpu_cores', 'N/A')}")
        
        # Send confirmation
        response = NetworkMessage(
            msg_type="registration_ack",
            msg_id=str(uuid.uuid4()),
            timestamp=time.time(),
            data={'status': 'registered', 'peer_id': peer_id}
        )
        await websocket.send(response.to_json())
        
        # Broadcast peer count to all users
        await self.broadcast_peer_count()
    
    async def register_user(self, websocket, msg: NetworkMessage):
        """Register a user client."""
        user_id = msg.data['user_id']
        self.users[user_id] = websocket
        self.logger.info(f"✓ Registered user: {user_id}")
        
        # Send confirmation with available peers
        response = NetworkMessage(
            msg_type="registration_ack",
            msg_id=str(uuid.uuid4()),
            timestamp=time.time(),
            data={
                'status': 'registered',
                'user_id': user_id,
                'available_peers': len([p for p in self.peers.values() if p.status == 'idle'])
            }
        )
        await websocket.send(response.to_json())
    
    async def handle_heartbeat(self, msg: NetworkMessage):
        """Update peer heartbeat."""
        peer_id = msg.data['peer_id']
        if peer_id in self.peers:
            self.peers[peer_id].last_heartbeat = time.time()
            # self.logger.debug(f"Heartbeat from {peer_id}")
    
    async def handle_task_request(self, websocket, msg: NetworkMessage):
        """Handle task request from user."""
        task_id = msg.data['task_id']
        task_data = msg.data['task_data']
        requirements = msg.data.get('requirements', {})
        
        self.logger.info(f"📋 Task request: {task_id}")
        self.logger.info(f"   Type: {task_data.get('type', 'unknown')}")
        
        # Find best peer
        best_peer = self.select_best_peer(requirements)
        
        if best_peer:
            # Assign task to peer
            best_peer.status = 'busy'
            best_peer.current_task = task_id
            self.pending_tasks[task_id] = {
                'task_data': task_data,
                'user_ws': websocket,
                'peer_id': best_peer.peer_id,
                'start_time': time.time()
            }
            
            # Send task to peer
            task_msg = NetworkMessage(
                msg_type="task_assignment",
                msg_id=str(uuid.uuid4()),
                timestamp=time.time(),
                data={
                    'task_id': task_id,
                    'task_data': task_data
                }
            )
            await best_peer.websocket.send(task_msg.to_json())
            
            self.logger.info(f"   ✓ Assigned to peer: {best_peer.peer_id}")
        else:
            # No peers available
            self.logger.warning(f"   ✗ No peers available for task {task_id}")
            error_msg = NetworkMessage(
                msg_type="task_error",
                msg_id=str(uuid.uuid4()),
                timestamp=time.time(),
                data={
                    'task_id': task_id,
                    'error': 'No peers available'
                }
            )
            await websocket.send(error_msg.to_json())
    
    async def handle_task_result(self, msg: NetworkMessage):
        """Handle task completion from peer."""
        task_id = msg.data['task_id']
        peer_id = msg.data['peer_id']
        result_data = msg.data['result']
        
        if task_id not in self.pending_tasks:
            self.logger.warning(f"Received result for unknown task: {task_id}")
            return
        
        task_info = self.pending_tasks[task_id]
        completion_time = time.time() - task_info['start_time']
        
        # Update peer stats
        peer = self.peers[peer_id]
        peer.status = 'idle'
        peer.current_task = None
        peer.tasks_completed += 1
        
        # Update average completion time
        total_tasks = peer.tasks_completed + peer.tasks_failed
        peer.avg_completion_time = (
            (peer.avg_completion_time * (total_tasks - 1) + completion_time) / total_tasks
        )
        
        self.logger.info(f"✓ Task {task_id} completed by {peer_id} in {completion_time:.2f}s")
        
        # Send result to user
        result_msg = NetworkMessage(
            msg_type="task_result",
            msg_id=str(uuid.uuid4()),
            timestamp=time.time(),
            data={
                'task_id': task_id,
                'result': result_data,
                'peer_id': peer_id,
                'completion_time': completion_time
            }
        )
        
        user_ws = task_info['user_ws']
        try:
            await user_ws.send(result_msg.to_json())
        except Exception as e:
            self.logger.error(f"Failed to send result to user: {e}")
        
        # Cleanup
        del self.pending_tasks[task_id]
    
    async def handle_task_failure(self, msg: NetworkMessage):
        """Handle task failure from peer."""
        task_id = msg.data['task_id']
        peer_id = msg.data['peer_id']
        error = msg.data.get('error', 'Unknown error')
        
        self.logger.warning(f"✗ Task {task_id} failed on {peer_id}: {error}")
        
        if peer_id in self.peers:
            peer = self.peers[peer_id]
            peer.status = 'idle'
            peer.current_task = None
            peer.tasks_failed += 1
        
        # TODO: Implement failover to another peer
        # For now, just notify user
        if task_id in self.pending_tasks:
            task_info = self.pending_tasks[task_id]
            error_msg = NetworkMessage(
                msg_type="task_error",
                msg_id=str(uuid.uuid4()),
                timestamp=time.time(),
                data={
                    'task_id': task_id,
                    'error': error,
                    'peer_id': peer_id
                }
            )
            
            user_ws = task_info['user_ws']
            try:
                await user_ws.send(error_msg.to_json())
            except Exception as e:
                self.logger.error(f"Failed to send error to user: {e}")
            
            del self.pending_tasks[task_id]
    
    def select_best_peer(self, requirements: dict) -> Optional[PeerInfo]:
        """Select best available peer for task."""
        available = [p for p in self.peers.values() if p.status == 'idle']
        
        if not available:
            return None
        
        # Simple selection: prefer peers with lower average completion time
        return min(available, key=lambda p: p.avg_completion_time if p.avg_completion_time > 0 else 999)
    
    async def handle_disconnect(self, websocket):
        """Handle client disconnect."""
        # Find and remove peer
        for peer_id, peer in list(self.peers.items()):
            if peer.websocket == websocket:
                self.logger.info(f"Peer disconnected: {peer_id}")
                del self.peers[peer_id]
                await self.broadcast_peer_count()
                return
        
        # Find and remove user
        for user_id, ws in list(self.users.items()):
            if ws == websocket:
                self.logger.info(f"User disconnected: {user_id}")
                del self.users[user_id]
                return
    
    async def monitor_peers(self):
        """Monitor peer health and remove dead peers."""
        while True:
            await asyncio.sleep(10)
            
            current_time = time.time()
            dead_peers = []
            
            for peer_id, peer in self.peers.items():
                if current_time - peer.last_heartbeat > 30:  # 30 second timeout
                    dead_peers.append(peer_id)
            
            for peer_id in dead_peers:
                self.logger.warning(f"Peer timeout: {peer_id}")
                del self.peers[peer_id]
                await self.broadcast_peer_count()
    
    async def broadcast_peer_count(self):
        """Broadcast current peer count to all users."""
        peer_count = len([p for p in self.peers.values() if p.status == 'idle'])
        
        msg = NetworkMessage(
            msg_type="peer_count_update",
            msg_id=str(uuid.uuid4()),
            timestamp=time.time(),
            data={'available_peers': peer_count, 'total_peers': len(self.peers)}
        )
        
        for user_ws in self.users.values():
            try:
                await user_ws.send(msg.to_json())
            except:
                pass


async def main():
    """Run the cloud coordinator."""
    coordinator = CloudCoordinator(host="0.0.0.0", port=8765)
    await coordinator.start()


if __name__ == '__main__':
    print("=" * 70)
    print("☁️  P2C2R CLOUD COORDINATOR")
    print("=" * 70)
    print()
    print("This is the central server that coordinates the P2C2R network.")
    print()
    print("Waiting for connections...")
    print("  - Peers will connect and register their capabilities")
    print("  - Users will connect and submit tasks")
    print("  - Coordinator will assign tasks to best available peer")
    print()
    print("=" * 70)
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Coordinator shutting down...")
