# SEMVX Installation Guide

## Prerequisites

- Python 3.8 or higher
- Git (for tag management features)

## Installation Methods

### Method 1: pipx (Recommended for CLI tools)

pipx installs the package in an isolated environment and makes the CLI globally available:

```bash
# Install pipx if you don't have it
sudo apt install pipx  # Ubuntu/Debian
# or
brew install pipx      # macOS

# Install semvx in editable mode (for development)
cd /path/to/semv-py
pipx install -e .

# Or install from a specific location
pipx install -e /path/to/semv-py
```

**Advantages:**
- Global `semvx` command available
- Isolated environment (no conflicts)
- Easy to uninstall: `pipx uninstall semvx`

### Method 2: Virtual Environment (For development)

```bash
cd /path/to/semv-py

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install in editable mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

**Advantages:**
- Full control over dependencies
- Good for development and testing
- Can install dev dependencies

### Method 3: System-wide (Not recommended)

```bash
# Only if you really need system-wide installation
pip install -e . --break-system-packages
```

⚠️ **Warning:** This can break your system Python. Use pipx or venv instead.

## Verification

After installation, verify semvx is working:

```bash
# Check version
semvx --version

# Show help
semvx --help

# Test detection
semvx detect
```

## Uninstallation

### If installed with pipx:
```bash
pipx uninstall semvx
```

### If installed with pip:
```bash
pip uninstall semvx
```

## Development Setup

For development work, use the Makefile:

```bash
# Install with dev dependencies
make install

# Run tests
make test

# Run CLI tests
make cli-test

# Check code quality
make quality
```

## Troubleshooting

### Command not found: semvx

If `semvx` is not found after installation:

1. **Check if pipx bin directory is in PATH:**
   ```bash
   echo $PATH | grep .local/bin
   ```
   
   If not, add to your shell config (~/.bashrc or ~/.zshrc):
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```

2. **Verify installation:**
   ```bash
   pipx list
   which semvx
   ```

### Import errors

If you get import errors:

1. **Make sure you're in the right directory:**
   ```bash
   cd /path/to/semv-py
   ```

2. **Reinstall in editable mode:**
   ```bash
   pipx reinstall semvx
   ```

### Permission errors

If you get permission errors:

- Don't use `sudo` with pipx or pip
- Use virtual environments or pipx instead of system Python
- Check file permissions in the project directory

## Next Steps

After installation, see:
- `README.md` for quick start guide
- `docs/procs/PROCESS.md` for complete workflow
- `DEVELOPMENT.md` for development setup

## Support

For issues or questions:
1. Check `docs/procs/PROCESS.md`
2. Run `semvx --help` for command documentation
3. Check test results with `make test`
