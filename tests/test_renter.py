"""Tests for RenterClient."""

import pytest
from src.p2c2g.renter import RenterClient


class TestRenterClient:
    """Test RenterClient functionality."""

    def test_renter_creation(self):
        """Test creating a renter client."""
        renter = RenterClient("renter_1")
        assert renter.renter_id == "renter_1"

    def test_send_input(self):
        """Test sending input (no-op in PoC)."""
        renter = RenterClient("renter_1")
        # Should not raise any errors
        renter.send_input({"key": "value"})
        renter.send_input({})

    def test_receive_stream(self, capsys):
        """Test receiving a stream."""
        renter = RenterClient("renter_1")
        stream = b"test_stream_data_here"

        renter.receive_stream(stream)

        captured = capsys.readouterr()
        assert "renter_1" in captured.out
        assert str(len(stream)) in captured.out
        assert "test_stream_data" in captured.out  # Preview

    def test_receive_stream_short(self, capsys):
        """Test receiving a short stream."""
        renter = RenterClient("renter_1")
        stream = b"short"

        renter.receive_stream(stream)

        captured = capsys.readouterr()
        assert "5 bytes" in captured.out
        assert "short" in captured.out

    def test_receive_stream_empty(self, capsys):
        """Test receiving an empty stream."""
        renter = RenterClient("renter_1")
        stream = b""

        renter.receive_stream(stream)

        captured = capsys.readouterr()
        assert "0 bytes" in captured.out

    def test_renter_repr(self):
        """Test renter representation."""
        renter = RenterClient("renter_1")
        repr_str = repr(renter)
        assert "renter_1" in repr_str
