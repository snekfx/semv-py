#!/bin/bash
# SEMVX Development Environment Setup Script
# Sets up a complete development environment for SEMVX

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print colored messages
info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Header
echo "================================================"
echo "SEMVX Development Environment Setup"
echo "================================================"
echo ""

# Check Python version
info "Checking Python installation..."

# Prefer pyenv Python if available
if [ -x ~/.pyenv/shims/python ]; then
    PYTHON=~/.pyenv/shims/python
    PIP=~/.pyenv/shims/pip
    info "Using pyenv Python"
elif command -v python3 &> /dev/null; then
    PYTHON=python3
    PIP=pip3
    info "Using system Python 3"
else
    error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Display Python version
PYTHON_VERSION=$($PYTHON --version 2>&1)
info "Python version: $PYTHON_VERSION"

# Check minimum Python version (3.8+)
MIN_VERSION="3.8"
CURRENT_VERSION=$($PYTHON -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if [ "$(printf '%s\n' "$MIN_VERSION" "$CURRENT_VERSION" | sort -V | head -n1)" != "$MIN_VERSION" ]; then
    error "Python $MIN_VERSION or higher is required. Current version: $CURRENT_VERSION"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    error "Please run this script from the SEMVX project root directory"
    exit 1
fi

# Create virtual environment (optional)
if [ "$1" == "--venv" ]; then
    info "Creating virtual environment..."
    $PYTHON -m venv venv
    source venv/bin/activate
    PYTHON=python
    PIP=pip
    info "Virtual environment activated"
fi

# Upgrade pip
info "Upgrading pip..."
$PIP install --upgrade pip -q

# Install package in development mode
info "Installing SEMVX in development mode..."
$PIP install -e ".[dev]" -q

# Verify installation
info "Verifying installation..."

# Check if pytest is available
if $PYTHON -c "import pytest" 2>/dev/null; then
    info "✅ pytest installed"
else
    warn "pytest not found, installing..."
    $PIP install pytest pytest-cov
fi

# Check if other tools are available
for tool in black mypy ruff; do
    if $PYTHON -c "import $tool" 2>/dev/null; then
        info "✅ $tool installed"
    else
        warn "$tool not found, installing..."
        $PIP install $tool
    fi
done

# Run basic tests
info "Running basic tests..."
if $PYTHON tests/run_tests.py; then
    info "✅ Basic tests passed"
else
    warn "Some basic tests failed - check output above"
fi

# Test CLI commands
info "Testing CLI commands..."
$PYTHON src/semvx/cli/main.py --version > /dev/null 2>&1 && info "✅ CLI version command works"
$PYTHON src/semvx/cli/main.py detect > /dev/null 2>&1 && info "✅ CLI detect command works"
$PYTHON src/semvx/cli/main.py status > /dev/null 2>&1 && info "✅ CLI status command works"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    info "Creating .env file..."
    cat > .env << EOF
# SEMVX Development Environment Variables
PYTHONPATH=src:\$PYTHONPATH
SEMVX_DEBUG=1
EOF
    info "✅ .env file created"
fi

# Display summary
echo ""
echo "================================================"
echo "Development Environment Setup Complete!"
echo "================================================"
echo ""
echo "Available commands:"
echo "  make help        - Show all available make commands"
echo "  make test        - Run all tests with pytest"
echo "  make test-quick  - Run basic tests without pytest"
echo "  make cli-test    - Test all CLI commands"
echo "  make coverage    - Run tests with coverage report"
echo "  make quality     - Run code quality checks"
echo ""
echo "Quick start:"
echo "  $PYTHON src/semvx/cli/main.py detect    # Run detection"
echo "  $PYTHON src/semvx/cli/main.py status    # Show status"
echo "  $PYTHON src/semvx/cli/main.py --help    # Show help"
echo ""

if [ "$1" == "--venv" ]; then
    echo "Virtual environment created. Activate with:"
    echo "  source venv/bin/activate"
fi

echo ""
info "Happy coding! 🚀"