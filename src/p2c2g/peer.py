"""
Peer agent implementation.

This module provides the PeerAgent class that represents a contributor node
executing tasks with simulated latency, reliability, and resource constraints.
"""

import asyncio
import random
import time
from .models import Task, Result, Telemetry


class PeerAgent:
    """
    Represents a contributor node that executes tasks.

    Attributes:
        peer_id (str): Unique identifier for the peer.
        base_latency_ms (int): Baseline latency for this peer (simulated).
        reliability (float): Probability of successful task execution [0, 1].
        max_throughput (int): Maximum parallel tasks allowed (simulated).
        in_flight (int): Current number of tasks being processed.

    Methods:
        process_task(task: Task) -> Result:
            Asynchronously executes a task with simulated latency, success/failure, and output.
        heartbeat() -> Telemetry:
            Returns a simulated telemetry snapshot for coordinator decisions.
    """

    def __init__(
        self,
        peer_id: str,
        base_latency_ms: int,
        reliability: float,
        max_throughput: int = 2,
    ):
        self.peer_id = peer_id
        self.base_latency_ms = base_latency_ms
        self.reliability = reliability
        self.max_throughput = max_throughput
        self.in_flight = 0

    async def process_task(self, task: Task) -> Result:
        """
        Process a task with simulated execution.

        Args:
            task: The task to process.

        Returns:
            Result object with execution outcome.
        """
        start = time.time()

        # Simulate queue wait if overloaded
        if self.in_flight >= self.max_throughput:
            wait_ms = random.randint(10, 40)
            await asyncio.sleep(wait_ms / 1000)

        self.in_flight += 1

        try:
            # Simulate network + execution latency
            jitter_ms = random.randint(0, 30)
            exec_ms = random.randint(20, 80)
            total_ms = self.base_latency_ms + jitter_ms + exec_ms

            # Random chance of failure based on reliability
            success = random.random() < self.reliability

            await asyncio.sleep(total_ms / 1000)

            duration_ms = int((time.time() - start) * 1000)

            if not success:
                return Result(
                    task.job_id,
                    task.task_id,
                    "failure",
                    b"",
                    duration_ms,
                    self.peer_id,
                    error="peer_error",
                )

            # Simulate output by transforming payload (reverse bytes as a stand-in)
            output = task.payload[::-1]
            return Result(
                task.job_id, task.task_id, "success", output, duration_ms, self.peer_id
            )

        finally:
            self.in_flight -= 1

    def heartbeat(self) -> Telemetry:
        """
        Generate telemetry snapshot for coordinator.

        Returns:
            Telemetry object with current peer metrics.
        """
        gpu_load = round(random.uniform(5.0, 25.0), 2)
        cpu_load = round(random.uniform(3.0, 20.0), 2)
        latency_ms = self.base_latency_ms + random.randint(0, 20)
        thermal_status = random.choice(
            ["normal", "normal", "throttling"]
        )  # skew to normal
        reliability_score = self.reliability
        return Telemetry(
            self.peer_id,
            gpu_load,
            cpu_load,
            latency_ms,
            thermal_status,
            reliability_score,
        )

    def __repr__(self) -> str:
        return f"PeerAgent(id={self.peer_id}, latency={self.base_latency_ms}ms, reliability={self.reliability})"
