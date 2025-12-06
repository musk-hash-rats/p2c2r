"""Tests for data models."""

import pytest
import time
from src.p2c2g.models import Task, Result, Telemetry


class TestTask:
    """Test Task model."""

    def test_task_creation(self):
        """Test creating a task."""
        task = Task(
            job_id="job_1",
            task_id="task_1",
            payload=b"test_data",
            deadline_ms=100,
            constraints={"gpu_pct": 10, "cpu_pct": 5},
        )
        assert task.job_id == "job_1"
        assert task.task_id == "task_1"
        assert task.payload == b"test_data"
        assert task.deadline_ms == 100
        assert task.constraints == {"gpu_pct": 10, "cpu_pct": 5}
        assert task.attempts == 0
        assert isinstance(task.created_at, float)

    def test_task_repr(self):
        """Test task representation."""
        task = Task("job_1", "task_1", b"data", 100, {})
        repr_str = repr(task)
        assert "job_1" in repr_str
        assert "task_1" in repr_str


class TestResult:
    """Test Result model."""

    def test_result_success(self):
        """Test successful result."""
        result = Result(
            job_id="job_1",
            task_id="task_1",
            status="success",
            output=b"result_data",
            duration_ms=50,
            peer_id="peer_1",
        )
        assert result.job_id == "job_1"
        assert result.task_id == "task_1"
        assert result.status == "success"
        assert result.output == b"result_data"
        assert result.duration_ms == 50
        assert result.peer_id == "peer_1"
        assert result.error is None

    def test_result_failure(self):
        """Test failed result."""
        result = Result(
            job_id="job_1",
            task_id="task_1",
            status="failure",
            output=b"",
            duration_ms=30,
            peer_id="peer_1",
            error="timeout",
        )
        assert result.status == "failure"
        assert result.error == "timeout"

    def test_result_repr(self):
        """Test result representation."""
        result = Result("job_1", "task_1", "success", b"data", 50, "peer_1")
        repr_str = repr(result)
        assert "task_1" in repr_str
        assert "success" in repr_str
        assert "peer_1" in repr_str


class TestTelemetry:
    """Test Telemetry model."""

    def test_telemetry_creation(self):
        """Test creating telemetry."""
        telemetry = Telemetry(
            peer_id="peer_1",
            gpu_load=15.5,
            cpu_load=10.2,
            latency_ms=25,
            thermal_status="normal",
            reliability_score=0.9,
        )
        assert telemetry.peer_id == "peer_1"
        assert telemetry.gpu_load == 15.5
        assert telemetry.cpu_load == 10.2
        assert telemetry.latency_ms == 25
        assert telemetry.thermal_status == "normal"
        assert telemetry.reliability_score == 0.9

    def test_telemetry_repr(self):
        """Test telemetry representation."""
        telemetry = Telemetry("peer_1", 15.0, 10.0, 25, "normal", 0.9)
        repr_str = repr(telemetry)
        assert "peer_1" in repr_str
        assert "25" in repr_str
        assert "0.9" in repr_str
