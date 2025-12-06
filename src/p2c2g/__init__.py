"""
P2C2G - Peer-to-Cloud-to-Gamer
================================

A distributed computing framework for cloud gaming sessions.

This package provides components for:
- Peer agents that execute compute tasks
- Coordinator for task scheduling and failover
- Renter client for consuming processed streams
"""

__version__ = "0.1.0"
__author__ = "musk-hash-rats"

from .peer import PeerAgent
from .coordinator import Coordinator
from .renter import RenterClient
from .models import Task, Result, Telemetry

__all__ = [
    "PeerAgent",
    "Coordinator",
    "RenterClient",
    "Task",
    "Result",
    "Telemetry",
]
