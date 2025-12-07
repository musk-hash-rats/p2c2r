"""
Network configuration shared across all devices
"""

# Default cloud coordinator settings
DEFAULT_CLOUD_HOST = "0.0.0.0"  # Listen on all interfaces
DEFAULT_CLOUD_PORT = 8765

# Billing rates (per hour)
PEER_EARNING_RATE = 0.15  # $0.15/hour for contributors
GAMER_COST_RATE = 0.01    # $0.01/hour for renters
COORDINATOR_FEE = 0.10     # 10% coordinator fee

# Task timeouts (seconds)
TASK_TIMEOUT = 30
HEARTBEAT_INTERVAL = 5

# Storage settings
RESULT_CACHE_HOURS = 24
DATABASE_PATH = "p2c2r_cloud.db"

# Network settings
MAX_RECONNECT_ATTEMPTS = 5
RECONNECT_DELAY = 3  # seconds
