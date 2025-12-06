# Contributing to P2C2G

Thank you for your interest in contributing to P2C2G! This document provides guidelines for contributing to the project.

## Code of Conduct

Be respectful, inclusive, and constructive in all interactions.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/musk-hash-rats/p2c2r/issues)
2. If not, create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - Python version and OS
   - Relevant code snippets or logs

### Suggesting Enhancements

1. Check existing issues and discussions
2. Create an issue describing:
   - The problem you're trying to solve
   - Your proposed solution
   - Any alternatives considered
   - Potential impact on existing functionality

### Pull Requests

1. **Fork the repository** and create a branch from `main`
2. **Make your changes**:
   - Follow the existing code style (PEP 8)
   - Add type hints to function signatures
   - Write clear docstrings
   - Keep functions focused and under 50 lines
3. **Add tests** for new functionality
4. **Run the test suite**: `pytest tests/`
5. **Run linters**:
   ```bash
   flake8 src/p2c2g tests/
   mypy src/p2c2g
   black src/p2c2g tests/
   ```
6. **Update documentation** if needed
7. **Commit with clear messages**:
   - Use present tense ("Add feature" not "Added feature")
   - Reference issues: "Fix #123: Description"
8. **Push to your fork** and submit a pull request

### Pull Request Guidelines

- Target the `main` branch
- Include a clear description of changes
- Reference related issues
- Ensure all tests pass
- Maintain or improve code coverage
- Update CHANGELOG.md if applicable

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/p2c2g.git
cd p2c2g

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run linters
flake8 src/p2c2g tests/
mypy src/p2c2g
black --check src/p2c2g tests/
```

## Code Style

- **PEP 8**: Follow Python style guidelines
- **Type Hints**: Use for all function signatures
- **Docstrings**: Google-style docstrings for classes and public methods
- **Line Length**: 88 characters (Black default)
- **Imports**: Organized with isort
- **Naming**:
  - `snake_case` for functions and variables
  - `PascalCase` for classes
  - `UPPER_CASE` for constants

## Testing

- Write tests for all new functionality
- Use pytest fixtures for common setup
- Test both success and failure paths
- Aim for >80% code coverage
- Use pytest-asyncio for async tests

Example test structure:
```python
import pytest
from p2c2g import PeerAgent

def test_peer_creation():
    peer = PeerAgent("peer_1", 20, 0.9)
    assert peer.peer_id == "peer_1"
    assert peer.base_latency_ms == 20

@pytest.mark.asyncio
async def test_peer_process_task():
    # Test async functionality
    pass
```

## Documentation

- Update README.md for user-facing changes
- Update docstrings for API changes
- Add examples in `examples/` for new features
- Update `docs/` for architectural changes

## Commit Messages

Format: `<type>: <subject>`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
- `feat: Add peer discovery mechanism`
- `fix: Correct failover retry logic`
- `docs: Update API documentation`

## Questions?

Feel free to:
- Open an issue for discussion
- Reach out to maintainers
- Check existing documentation in `docs/`

Thank you for contributing to P2C2G! 🎮
