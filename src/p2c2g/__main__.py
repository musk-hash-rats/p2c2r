"""Main entry point for p2c2g package when run as module."""

import asyncio
import sys
from p2c2g_poc import demo_p2c2g


def main():
    """Run the P2C2G demo."""
    print("P2C2G Proof of Concept")
    print("=" * 50)
    
    # Parse command-line arguments if provided
    num_peers = 5
    num_frames = 30
    
    if len(sys.argv) > 1:
        try:
            num_peers = int(sys.argv[1])
        except ValueError:
            print(f"Invalid number of peers: {sys.argv[1]}")
            sys.exit(1)
    
    if len(sys.argv) > 2:
        try:
            num_frames = int(sys.argv[2])
        except ValueError:
            print(f"Invalid number of frames: {sys.argv[2]}")
            sys.exit(1)
    
    asyncio.run(demo_p2c2g(num_peers=num_peers, num_frames=num_frames))
    print("\nPoC complete!")


if __name__ == "__main__":
    main()
