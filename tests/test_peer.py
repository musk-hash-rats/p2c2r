"""Tests for PeerAgent."""

import pytest
from src.p2c2g.peer import PeerAgent
from src.p2c2g.models import Task


class TestPeerAgent:
    """Test PeerAgent functionality."""

    def test_peer_creation(self):
        """Test creating a peer agent."""
        peer = PeerAgent(
            peer_id="peer_1", base_latency_ms=20, reliability=0.9, max_throughput=3
        )
        assert peer.peer_id == "peer_1"
        assert peer.base_latency_ms == 20
        assert peer.reliability == 0.9
        assert peer.max_throughput == 3
        assert peer.in_flight == 0

    def test_peer_default_throughput(self):
        """Test default max throughput."""
        peer = PeerAgent(peer_id="peer_1", base_latency_ms=20, reliability=0.9)
        assert peer.max_throughput == 2

    @pytest.mark.asyncio
    async def test_peer_process_task_success(self):
        """Test processing a task successfully."""
        peer = PeerAgent(peer_id="peer_1", base_latency_ms=10, reliability=1.0)
        task = Task(
            job_id="job_1",
            task_id="task_1",
            payload=b"test_data",
            deadline_ms=100,
            constraints={},
        )

        result = await peer.process_task(task)

        assert result.job_id == "job_1"
        assert result.task_id == "task_1"
        assert result.peer_id == "peer_1"
        assert result.status == "success"
        assert result.output == b"atad_tset"  # Reversed payload
        assert result.duration_ms > 0
        assert peer.in_flight == 0  # Should be reset after processing

    @pytest.mark.asyncio
    async def test_peer_process_task_failure(self):
        """Test processing a task with failure."""
        peer = PeerAgent(peer_id="peer_1", base_latency_ms=10, reliability=0.0)
        task = Task(
            job_id="job_1",
            task_id="task_1",
            payload=b"test_data",
            deadline_ms=100,
            constraints={},
        )

        result = await peer.process_task(task)

        assert result.status == "failure"
        assert result.error == "peer_error"
        assert result.output == b""

    def test_peer_heartbeat(self):
        """Test peer heartbeat generation."""
        peer = PeerAgent(peer_id="peer_1", base_latency_ms=20, reliability=0.9)
        telemetry = peer.heartbeat()

        assert telemetry.peer_id == "peer_1"
        assert 5.0 <= telemetry.gpu_load <= 25.0
        assert 3.0 <= telemetry.cpu_load <= 20.0
        assert 20 <= telemetry.latency_ms <= 40  # base + jitter
        assert telemetry.thermal_status in ["normal", "throttling"]
        assert telemetry.reliability_score == 0.9

    def test_peer_repr(self):
        """Test peer representation."""
        peer = PeerAgent(peer_id="peer_1", base_latency_ms=20, reliability=0.9)
        repr_str = repr(peer)
        assert "peer_1" in repr_str
        assert "20" in repr_str
        assert "0.9" in repr_str

    @pytest.mark.asyncio
    async def test_peer_concurrent_processing(self):
        """Test peer handling concurrent tasks."""
        peer = PeerAgent(
            peer_id="peer_1", base_latency_ms=10, reliability=1.0, max_throughput=2
        )

        tasks = [
            Task(f"job_1", f"task_{i}", b"data", 100, {}) for i in range(3)
        ]

        # Process tasks concurrently
        import asyncio

        results = await asyncio.gather(
            *[peer.process_task(task) for task in tasks]
        )

        assert len(results) == 3
        assert all(r.status == "success" for r in results)
        assert peer.in_flight == 0
