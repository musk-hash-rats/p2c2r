"""
Coordinator implementation.

This module provides the Coordinator class that orchestrates task scheduling,
peer selection, failover handling, and result assembly.
"""

import asyncio
from typing import Dict, List, Optional
from .models import Task, Result
from .peer import PeerAgent


class Coordinator:
    """
    Orchestrates tasks across peers and assembles results.

    Attributes:
        peers (Dict[str, PeerAgent]): Registered peers.
        reputation (Dict[str, float]): Peer reputation score updated on successes/failures.
        pending (Dict[str, Task]): Tasks not yet completed.
        completed (Dict[str, Result]): Completed results by task_id.
        max_attempts (int): Maximum retries per task before marking failure.
        renter_buffer (List[Result]): Ordered buffer for renter stream assembly.

    Methods:
        register_peer(peer: PeerAgent) -> None:
            Register a peer for scheduling.
        pick_peer() -> PeerAgent:
            Select the best available peer by latency + load + reputation.
        schedule_task(task: Task) -> None:
            Assign task to a peer and handle execution with failover.
        handle_failover(task: Task, last_error: Optional[str]) -> bool:
            Retry task on another peer; returns True if reissued, False otherwise.
        assemble_stream(frame_order: List[str]) -> bytes:
            Assemble results in given order into a single byte stream.
    """

    def __init__(self, max_attempts: int = 3):
        self.peers: Dict[str, PeerAgent] = {}
        self.reputation: Dict[str, float] = {}
        self.pending: Dict[str, Task] = {}
        self.completed: Dict[str, Result] = {}
        self.max_attempts = max_attempts
        self.renter_buffer: List[Result] = []

    def register_peer(self, peer: PeerAgent) -> None:
        """Register a peer for task scheduling."""
        self.peers[peer.peer_id] = peer
        self.reputation[peer.peer_id] = peer.reliability

    def pick_peer(self) -> Optional[PeerAgent]:
        """
        Select the best available peer based on multiple factors.

        Returns:
            The selected peer or None if no peers available.
        """
        # Score peers by latency + inflight + (1 - reputation)
        scored = []
        for p in self.peers.values():
            t = p.heartbeat()
            cost = (
                t.latency_ms
                + (p.in_flight * 15)
                + int((1.0 - self.reputation[p.peer_id]) * 50)
            )
            scored.append((cost, p))
        scored.sort(key=lambda x: x[0])
        return scored[0][1] if scored else None

    async def schedule_task(self, task: Task) -> None:
        """
        Schedule a task to an appropriate peer.

        Args:
            task: The task to schedule.
        """
        self.pending[task.task_id] = task
        task.attempts += 1

        peer = self.pick_peer()
        if not peer:
            print(f"[Coordinator] No peers available for task {task.task_id}")
            return

        print(
            f"[Coordinator] Assign task {task.task_id} to peer {peer.peer_id} (attempt {task.attempts})"
        )
        result = await peer.process_task(task)

        if result.status == "success":
            self.completed[task.task_id] = result
            self.pending.pop(task.task_id, None)
            # Update reputation (bounded)
            self.reputation[peer.peer_id] = min(
                1.0, self.reputation[peer.peer_id] + 0.02
            )
            self.renter_buffer.append(result)
            print(
                f"[Coordinator] Task {task.task_id} completed by {peer.peer_id} in {result.duration_ms} ms"
            )
        else:
            # Penalize reputation
            self.reputation[peer.peer_id] = max(
                0.0, self.reputation[peer.peer_id] - 0.05
            )
            print(
                f"[Coordinator] Task {task.task_id} failed on {peer.peer_id}: {result.error}"
            )
            reissued = await self.handle_failover(task, result.error)
            if not reissued:
                print(
                    f"[Coordinator] Task {task.task_id} exhausted retries and failed permanently"
                )
                self.pending.pop(task.task_id, None)

    async def handle_failover(
        self, task: Task, last_error: Optional[str]
    ) -> bool:
        """
        Handle task failover by reassigning to another peer.

        Args:
            task: The task that failed.
            last_error: Error message from the previous attempt.

        Returns:
            True if task was successfully reissued, False otherwise.
        """
        if task.attempts >= self.max_attempts:
            return False

        await asyncio.sleep(0.01)  # small backoff
        task.attempts += 1
        peer = self.pick_peer()
        if not peer:
            return False

        print(
            f"[Coordinator] Reassign task {task.task_id} to {peer.peer_id} "
            f"(attempt {task.attempts}) after error: {last_error}"
        )
        result = await peer.process_task(task)

        if result.status == "success":
            self.completed[task.task_id] = result
            self.pending.pop(task.task_id, None)
            self.reputation[peer.peer_id] = min(
                1.0, self.reputation[peer.peer_id] + 0.01
            )
            self.renter_buffer.append(result)
            print(
                f"[Coordinator] Task {task.task_id} completed by {peer.peer_id} "
                f"in {result.duration_ms} ms (failover)"
            )
            return True
        else:
            self.reputation[peer.peer_id] = max(
                0.0, self.reputation[peer.peer_id] - 0.08
            )
            print(
                f"[Coordinator] Task {task.task_id} failed again on {peer.peer_id}: {result.error}"
            )
            # Try one more time recursively (bounded by max_attempts)
            return await self.handle_failover(task, result.error)

    def assemble_stream(self, frame_order: List[str]) -> bytes:
        """
        Assemble completed task results into a byte stream.

        Args:
            frame_order: Ordered list of task IDs defining the stream order.

        Returns:
            Assembled byte stream.
        """
        ordered = []
        missing = []
        for tid in frame_order:
            res = self.completed.get(tid)
            if res and res.status == "success":
                ordered.append(res.output)
            else:
                missing.append(tid)

        stream = b"".join(ordered)
        if missing:
            print(f"[Coordinator] Missing frames in assembly: {missing}")
        print(f"[Coordinator] Assembled stream length: {len(stream)} bytes")
        return stream
