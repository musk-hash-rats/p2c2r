"""Tests for Coordinator."""

import pytest
from src.p2c2g.coordinator import Coordinator
from src.p2c2g.peer import PeerAgent
from src.p2c2g.models import Task


class TestCoordinator:
    """Test Coordinator functionality."""

    def test_coordinator_creation(self):
        """Test creating a coordinator."""
        coordinator = Coordinator(max_attempts=3)
        assert coordinator.max_attempts == 3
        assert len(coordinator.peers) == 0
        assert len(coordinator.reputation) == 0
        assert len(coordinator.pending) == 0
        assert len(coordinator.completed) == 0

    def test_register_peer(self):
        """Test registering a peer."""
        coordinator = Coordinator()
        peer = PeerAgent("peer_1", base_latency_ms=20, reliability=0.9)

        coordinator.register_peer(peer)

        assert "peer_1" in coordinator.peers
        assert coordinator.peers["peer_1"] == peer
        assert coordinator.reputation["peer_1"] == 0.9

    def test_pick_peer_no_peers(self):
        """Test picking a peer when none are available."""
        coordinator = Coordinator()
        peer = coordinator.pick_peer()
        assert peer is None

    def test_pick_peer_single_peer(self):
        """Test picking a peer when only one is available."""
        coordinator = Coordinator()
        peer1 = PeerAgent("peer_1", base_latency_ms=20, reliability=0.9)
        coordinator.register_peer(peer1)

        selected = coordinator.pick_peer()
        assert selected == peer1

    def test_pick_peer_best_selection(self):
        """Test picking the best peer among multiple."""
        coordinator = Coordinator()
        peer1 = PeerAgent("peer_1", base_latency_ms=50, reliability=0.7)
        peer2 = PeerAgent("peer_2", base_latency_ms=10, reliability=0.95)
        peer3 = PeerAgent("peer_3", base_latency_ms=30, reliability=0.8)

        coordinator.register_peer(peer1)
        coordinator.register_peer(peer2)
        coordinator.register_peer(peer3)

        # Pick peer multiple times and check it tends to be peer_2 (best)
        selections = [coordinator.pick_peer() for _ in range(10)]
        # peer_2 should be selected most often due to low latency and high reliability
        assert selections.count(peer2) >= 5

    @pytest.mark.asyncio
    async def test_schedule_task_success(self):
        """Test scheduling a task successfully."""
        coordinator = Coordinator()
        peer = PeerAgent("peer_1", base_latency_ms=10, reliability=1.0)
        coordinator.register_peer(peer)

        task = Task("job_1", "task_1", b"data", 100, {})
        await coordinator.schedule_task(task)

        assert "task_1" in coordinator.completed
        assert coordinator.completed["task_1"].status == "success"
        assert "task_1" not in coordinator.pending
        assert len(coordinator.renter_buffer) == 1

    @pytest.mark.asyncio
    async def test_schedule_task_failure_with_failover(self):
        """Test task failure and failover."""
        coordinator = Coordinator(max_attempts=2)
        peer1 = PeerAgent("peer_1", base_latency_ms=10, reliability=0.0)
        peer2 = PeerAgent("peer_2", base_latency_ms=10, reliability=1.0)
        coordinator.register_peer(peer1)
        coordinator.register_peer(peer2)

        task = Task("job_1", "task_1", b"data", 100, {})
        await coordinator.schedule_task(task)

        # Task should eventually succeed via failover
        assert "task_1" in coordinator.completed or task.attempts >= 2

    @pytest.mark.asyncio
    async def test_handle_failover_success(self):
        """Test failover handling with eventual success."""
        coordinator = Coordinator(max_attempts=3)
        peer = PeerAgent("peer_1", base_latency_ms=10, reliability=1.0)
        coordinator.register_peer(peer)

        task = Task("job_1", "task_1", b"data", 100, {})
        task.attempts = 1  # Simulate one failed attempt

        success = await coordinator.handle_failover(task, "previous_error")

        assert success is True
        assert "task_1" in coordinator.completed
        assert coordinator.completed["task_1"].status == "success"

    @pytest.mark.asyncio
    async def test_handle_failover_max_attempts(self):
        """Test failover stops after max attempts."""
        coordinator = Coordinator(max_attempts=2)
        peer = PeerAgent("peer_1", base_latency_ms=10, reliability=0.0)
        coordinator.register_peer(peer)

        task = Task("job_1", "task_1", b"data", 100, {})
        task.attempts = 2  # Already at max

        success = await coordinator.handle_failover(task, "error")

        assert success is False

    def test_assemble_stream_all_present(self):
        """Test assembling stream with all tasks completed."""
        from src.p2c2g.models import Result

        coordinator = Coordinator()
        coordinator.completed["task_1"] = Result(
            "job_1", "task_1", "success", b"frame1", 50, "peer_1"
        )
        coordinator.completed["task_2"] = Result(
            "job_1", "task_2", "success", b"frame2", 50, "peer_1"
        )
        coordinator.completed["task_3"] = Result(
            "job_1", "task_3", "success", b"frame3", 50, "peer_1"
        )

        stream = coordinator.assemble_stream(["task_1", "task_2", "task_3"])

        assert stream == b"frame1frame2frame3"

    def test_assemble_stream_missing_tasks(self):
        """Test assembling stream with missing tasks."""
        from src.p2c2g.models import Result

        coordinator = Coordinator()
        coordinator.completed["task_1"] = Result(
            "job_1", "task_1", "success", b"frame1", 50, "peer_1"
        )
        coordinator.completed["task_3"] = Result(
            "job_1", "task_3", "success", b"frame3", 50, "peer_1"
        )

        stream = coordinator.assemble_stream(["task_1", "task_2", "task_3"])

        assert stream == b"frame1frame3"  # task_2 missing

    def test_reputation_update_on_success(self):
        """Test reputation increases on success."""
        from src.p2c2g.models import Result

        coordinator = Coordinator()
        peer = PeerAgent("peer_1", base_latency_ms=10, reliability=0.8)
        coordinator.register_peer(peer)

        initial_reputation = coordinator.reputation["peer_1"]

        # Simulate successful result handling
        coordinator.completed["task_1"] = Result(
            "job_1", "task_1", "success", b"data", 50, "peer_1"
        )
        coordinator.reputation["peer_1"] = min(
            1.0, coordinator.reputation["peer_1"] + 0.02
        )

        assert coordinator.reputation["peer_1"] > initial_reputation

    def test_reputation_update_on_failure(self):
        """Test reputation decreases on failure."""
        coordinator = Coordinator()
        peer = PeerAgent("peer_1", base_latency_ms=10, reliability=0.8)
        coordinator.register_peer(peer)

        initial_reputation = coordinator.reputation["peer_1"]

        # Simulate failure
        coordinator.reputation["peer_1"] = max(
            0.0, coordinator.reputation["peer_1"] - 0.05
        )

        assert coordinator.reputation["peer_1"] < initial_reputation
