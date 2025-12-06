"""
Data models for P2C2G system.

This module defines the core data structures used throughout the system:
- Task: Unit of work assigned to peers
- Result: Output returned by peers
- Telemetry: Heartbeat data from peers
"""

import time
from typing import Dict, Optional


class Task:
    """
    Represents a unit of work assigned to a peer.

    Attributes:
        job_id (str): Unique identifier for the overall job.
        task_id (str): Unique identifier for this task.
        payload (bytes): Binary payload representing the frame or chunk to process.
        deadline_ms (int): Time limit for task completion in milliseconds.
        constraints (dict): Resource limits (simulated), e.g., {'gpu_pct': 10, 'cpu_pct': 10}.
        created_at (float): Timestamp when task was created.
        attempts (int): Number of times this task has been attempted.
    """

    def __init__(
        self,
        job_id: str,
        task_id: str,
        payload: bytes,
        deadline_ms: int,
        constraints: Dict[str, int],
    ):
        self.job_id = job_id
        self.task_id = task_id
        self.payload = payload
        self.deadline_ms = deadline_ms
        self.constraints = constraints
        self.created_at = time.time()
        self.attempts = 0

    def __repr__(self) -> str:
        return f"Task(job_id={self.job_id}, task_id={self.task_id}, attempts={self.attempts})"


class Result:
    """
    Represents the output returned by a peer.

    Attributes:
        job_id (str): Associated job identifier.
        task_id (str): Associated task identifier.
        status (str): 'success' or 'failure'.
        output (bytes): Serialized result data.
        duration_ms (int): Execution time in milliseconds.
        peer_id (str): Identifier of the contributing peer.
        error (Optional[str]): Error message if status == 'failure'.
    """

    def __init__(
        self,
        job_id: str,
        task_id: str,
        status: str,
        output: bytes,
        duration_ms: int,
        peer_id: str,
        error: Optional[str] = None,
    ):
        self.job_id = job_id
        self.task_id = task_id
        self.status = status
        self.output = output
        self.duration_ms = duration_ms
        self.peer_id = peer_id
        self.error = error

    def __repr__(self) -> str:
        return f"Result(task_id={self.task_id}, status={self.status}, peer_id={self.peer_id})"


class Telemetry:
    """
    Represents heartbeat data sent from a peer to the coordinator.

    Attributes:
        peer_id (str): Unique identifier for the peer.
        gpu_load (float): Current GPU usage percentage (simulated).
        cpu_load (float): Current CPU usage percentage (simulated).
        latency_ms (int): Measured latency to coordinator (simulated).
        thermal_status (str): 'normal', 'throttling', or 'critical' (simulated).
        reliability_score (float): Peer reputation metric in [0, 1].
    """

    def __init__(
        self,
        peer_id: str,
        gpu_load: float,
        cpu_load: float,
        latency_ms: int,
        thermal_status: str,
        reliability_score: float,
    ):
        self.peer_id = peer_id
        self.gpu_load = gpu_load
        self.cpu_load = cpu_load
        self.latency_ms = latency_ms
        self.thermal_status = thermal_status
        self.reliability_score = reliability_score

    def __repr__(self) -> str:
        return f"Telemetry(peer_id={self.peer_id}, latency_ms={self.latency_ms}, reliability={self.reliability_score})"
