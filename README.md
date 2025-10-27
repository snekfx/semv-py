# semv-py

Opinionated semantic versioning - Python rewrite of SEMV

## Installation

### Using pipx (Recommended)
```bash
pipx install -e .
```

### Using pip in virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

## Quick Start

```bash
# Detect projects and versions
semvx detect

# Show version status
semvx status

# Calculate next version based on commits
semvx next
semvx next --verbose  # Show detailed commit analysis

# Get/set versions
semvx get all         # Show all version sources
semvx get python      # Show Python version
semvx set python 2.1.0  # Set Python version

# Sync versions across files
semvx sync            # Sync to highest version
semvx sync pyproject.toml  # Use specific file as source

# Bump version (with preview)
semvx bump patch --dry-run

# Bump version (actually update files)
semvx bump minor

# Create git tag
semvx tag

# List version tags
semvx tags
```

## Features

- ✅ Multi-language project detection (Python, Rust, JavaScript)
- ✅ Semantic version parsing and comparison
- ✅ Intelligent version calculation from commit history
- ✅ Full semv commit prefix support (major|breaking|api, feat|feature, fix|patch, etc.)
- ✅ Version get/set operations for all project types
- ✅ Version synchronization across multiple files
- ✅ Version bumping (major/minor/patch)
- ✅ Automatic file updates with backups
- ✅ Git tag creation and management
- ✅ Dry-run mode for safe testing
- ✅ Boxy integration for AI agent workflows

## Performance

**1.5x faster than bash semv!**
- semvx (Python): ~0.26s
- semv (Bash): ~0.39s

## Documentation

- **[Getting Started](docs/GETTING_STARTED.md)** - Quick start guide
- **[Installation Guide](docs/INSTALL.md)** - Detailed installation instructions
- **[Development Guide](docs/DEVELOPMENT.md)** - Contributing and development setup
- **[Task Board](docs/TASKS.md)** - Project roadmap and completed features
- **[Process Documentation](docs/procs/PROCESS.md)** - Complete workflow documentation

## Project Status

- ✅ **100% feature parity** with bash semv
- ✅ **17 SP completed** in latest session
- ✅ **108/108 tests passing**
- ✅ **Production ready**
