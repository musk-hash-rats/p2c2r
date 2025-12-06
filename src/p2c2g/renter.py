"""
Renter client implementation.

This module provides the RenterClient class representing the end-user
(gamer) consuming the distributed cloud gaming session.
"""

from typing import Dict


class RenterClient:
    """
    Represents the gamer consuming the distributed cloud session.

    Attributes:
        renter_id (str): Unique identifier for the renter.

    Methods:
        send_input(input_data: dict) -> None:
            Simulates sending user input to coordinator (no-op in PoC).
        receive_stream(stream: bytes) -> None:
            Prints received stream statistics and a preview.
    """

    def __init__(self, renter_id: str):
        self.renter_id = renter_id

    def send_input(self, input_data: Dict[str, str]) -> None:
        """
        Send user input to coordinator.

        Args:
            input_data: Dictionary containing user input data.

        Note:
            This is a no-op placeholder in the PoC; reserved for future interactive loop.
        """
        pass

    def receive_stream(self, stream: bytes) -> None:
        """
        Receive and display processed stream.

        Args:
            stream: Byte stream containing processed frames.
        """
        preview = stream[:16]
        print(
            f"[Renter:{self.renter_id}] Received stream ({len(stream)} bytes). Preview={preview}"
        )

    def __repr__(self) -> str:
        return f"RenterClient(id={self.renter_id})"
