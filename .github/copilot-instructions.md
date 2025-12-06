# P2C2G Project Instructions

## Project Overview
P2C2G (Peer-to-Cloud-to-Gamer) is a distributed computing proof of concept that simulates multiple peers contributing compute resources for cloud gaming sessions.

## Architecture
- **Peers**: Contributor nodes that execute tasks with varied latency and reliability
- **Coordinator**: Orchestrates task scheduling, handles failovers, and assembles outputs
- **Renter**: End-user (gamer) consuming the distributed cloud session

## Code Style
- Follow PEP 8 guidelines
- Use type hints for all function signatures
- Add docstrings for all classes and public methods
- Keep functions focused and under 50 lines where possible

## Development Workflow
1. Make changes in `src/p2c2g/` directory
2. Run tests with `pytest tests/`
3. Ensure code passes linting with `flake8` and `mypy`
4. Update documentation if APIs change
