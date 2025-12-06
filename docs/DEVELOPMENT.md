# Development Guide

## Setting Up Development Environment

### Prerequisites
- Python 3.9 or higher
- pip and virtualenv
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/musk-hash-rats/p2c2r.git
cd p2c2r
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Project Structure

```
P2c2gPOC/
├── src/
│   └── p2c2g/
│       ├── __init__.py
│       ├── __main__.py
│       ├── models.py          # Data contracts
│       ├── peer.py            # Peer agent implementation
│       ├── coordinator.py     # Coordinator logic
│       └── renter.py          # Renter client
├── tests/
│   ├── test_models.py
│   ├── test_peer.py
│   ├── test_coordinator.py
│   └── test_renter.py
├── docs/
│   ├── ARCHITECTURE.md
│   └── DEVELOPMENT.md
├── examples/
│   └── custom_simulation.py
├── p2c2g_poc.py              # Main entry point
├── setup.py
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## Code Style

This project follows:
- **PEP 8** style guide
- **Type hints** for all function signatures
- **Docstrings** for all classes and public methods
- Maximum line length: 100 characters

### Linting and Formatting

Run linters before committing:
```bash
# Flake8
flake8 src tests

# MyPy
mypy src/p2c2g

# Black (auto-format)
black src tests
```

## Testing

### Running Tests

Run all tests:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ --cov=src/p2c2g --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_coordinator.py -v
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files as `test_*.py`
- Use descriptive test function names
- Follow Arrange-Act-Assert pattern

Example:
```python
import pytest
from p2c2g.models import Task

def test_task_creation():
    # Arrange
    job_id = "job_001"
    task_id = "task_001"
    
    # Act
    task = Task(job_id, task_id, b"data", 100, {})
    
    # Assert
    assert task.job_id == job_id
    assert task.task_id == task_id
```

## Git Workflow

### Branch Strategy
- `main` - Production-ready code
- `develop` - Integration branch
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Urgent fixes

### Commit Messages
Follow conventional commits:
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Example:
```
feat(coordinator): add reputation-based peer selection

Implement scoring algorithm that considers:
- Network latency
- Current workload
- Historical reliability

Closes #123
```

### Pull Request Process

1. Create feature branch from `develop`
2. Make changes with tests
3. Ensure all tests pass
4. Run linters and fix issues
5. Update documentation if needed
6. Submit PR with description
7. Address review comments
8. Merge after approval

## Debugging

### Enable Debug Logging

Add to your script:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Using Debugger

With VS Code:
1. Set breakpoint in code
2. Press F5 to start debugging
3. Use debug console to inspect variables

With pdb:
```python
import pdb; pdb.set_trace()
```

## Performance Profiling

### Using cProfile
```bash
python -m cProfile -o profile.stats p2c2g_poc.py
python -m pstats profile.stats
```

### Memory Profiling
```bash
pip install memory_profiler
python -m memory_profiler p2c2g_poc.py
```

## Documentation

### Building Docs

Documentation is written in Markdown and located in `docs/`.

To generate API documentation:
```bash
pip install pdoc3
pdoc --html --output-dir docs/api src/p2c2g
```

### Docstring Format

Use Google-style docstrings:
```python
def schedule_task(self, task: Task) -> None:
    """
    Assign task to optimal peer and handle execution.
    
    Args:
        task: The task to schedule and execute.
        
    Raises:
        ValueError: If no peers are available.
        
    Examples:
        >>> coordinator.schedule_task(task)
    """
```

## Common Development Tasks

### Add New Feature
1. Create feature branch
2. Add implementation in `src/p2c2g/`
3. Add tests in `tests/`
4. Update documentation
5. Submit PR

### Fix Bug
1. Add failing test that reproduces bug
2. Fix implementation
3. Verify test passes
4. Submit PR with test and fix

### Update Dependencies
```bash
pip list --outdated
pip install --upgrade <package>
pip freeze > requirements.txt
```

## Release Process

1. Update version in `setup.py`
2. Update CHANGELOG.md
3. Merge to `main`
4. Create git tag: `git tag v0.1.0`
5. Push tag: `git push origin v0.1.0`
6. Create GitHub release

## Getting Help

- Read documentation in `docs/`
- Check existing issues on GitHub
- Review test cases for examples
- Ask questions in GitHub Discussions
