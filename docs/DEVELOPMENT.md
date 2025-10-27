# SEMVX Development Guide

## Quick Start

### 1. Setup Development Environment

```bash
# Using the setup script
./scripts/setup-dev.sh

# Or manually with Make
make install
make test-quick
```

### 2. Running Tests Locally

We provide multiple ways to run tests locally:

#### Using Make (Recommended)
```bash
# Run all tests with pytest
make test

# Run quick tests without pytest
make test-quick

# Run with coverage
make coverage

# Run only unit tests
make test-unit

# Test CLI commands
make cli-test
```

#### Using pytest directly (if using pyenv)
```bash
# With pyenv Python
~/.pyenv/shims/pytest tests/ -v

# Run specific test file
~/.pyenv/shims/pytest tests/unit/test_detection.py -v

# With coverage
~/.pyenv/shims/pytest tests/ --cov=src/semvx --cov-report=term-missing
```

#### Using the fallback test runner
```bash
# If pytest is not available
python3 tests/run_tests.py
```

### 3. Running the CLI

```bash
# Using Make
make cli-detect    # Run detection
make cli-status    # Show status
make cli-help      # Show help

# Direct Python execution
python3 src/semvx/cli/main.py detect
python3 src/semvx/cli/main.py status
python3 src/semvx/cli/main.py --help

# If installed with pip
semvx detect
semvx status
```

## Code Quality Tools

### Linting
```bash
# Run linter
make lint

# Or directly
ruff check src/ tests/
```

### Formatting
```bash
# Format code
make format

# Check formatting without changes
make format-check

# Or directly
black src/ tests/
```

### Type Checking
```bash
# Run type checker
make type-check

# Or directly
mypy src/
```

### All Quality Checks
```bash
# Run all quality checks at once
make quality
```

## Project Structure

```
semv-py/
├── src/
│   └── semvx/          # Main package
│       ├── cli/        # CLI interface
│       ├── detection/  # Project detection (shared module)
│       └── core/       # Core functionality (to be implemented)
├── tests/
│   ├── unit/          # Unit tests
│   ├── integration/   # Integration tests
│   ├── conftest.py    # pytest fixtures
│   └── run_tests.py   # Fallback test runner
├── scripts/
│   └── setup-dev.sh   # Development setup script
├── Makefile           # Development commands
├── pyproject.toml     # Project configuration
└── DEVELOPMENT.md     # This file
```

## Testing Strategy

### Unit Tests
- Located in `tests/unit/`
- Test individual functions and classes
- Should be fast and isolated
- Use fixtures from `conftest.py`

### Integration Tests
- Located in `tests/integration/`
- Test component interactions
- May create temporary directories/files
- Test real git operations

### Test Fixtures
Available fixtures in `tests/conftest.py`:
- `temp_dir`: Temporary directory for testing
- `python_project`: Mock Python project
- `rust_project`: Mock Rust project
- `javascript_project`: Mock JavaScript project
- `git_repository`: Git repo with initial commit
- `multi_project`: Repository with multiple project types

## Python Environment

### Using pyenv (Recommended)
If you have pyenv installed, the project will automatically use it:
```bash
# Check pyenv Python
~/.pyenv/shims/python --version

# Install dependencies
~/.pyenv/shims/pip install -e ".[dev]"
```

### Using System Python
If using system Python (Ubuntu/Debian):
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e ".[dev]"
```

## Common Tasks

### Adding a New Test
1. Create test file in appropriate directory
2. Import necessary functions
3. Use pytest fixtures for setup
4. Run with `make test`

### Updating Dependencies
1. Edit `pyproject.toml`
2. Run `make install`
3. Test with `make test`

### Before Committing
1. Run `make quality` for code quality
2. Run `make test` for all tests
3. Update documentation if needed

## Troubleshooting

### pytest not found
```bash
# Install with pyenv pip
~/.pyenv/shims/pip install pytest pytest-cov

# Or use the fallback runner
python3 tests/run_tests.py
```

### Import errors in tests
```bash
# Ensure package is installed in dev mode
make install
# or
pip install -e .
```

### Permission denied on scripts
```bash
chmod +x scripts/setup-dev.sh
```

## CI/CD

GitHub Actions workflows are configured in `.github/workflows/`:
- `test.yml`: Full test suite with multiple Python versions
- `quick-check.yml`: Quick validation for branches

## Need Help?

- Check `make help` for available commands
- Review `docs/procs/PROCESS.md` for workflow documentation
- See `docs/ref/` for technical documentation