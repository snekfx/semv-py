# semvx

**Opinionated semantic versioning for modern development workflows**

A Python rewrite of SEMV with enhanced features, better performance, and AI-friendly output formats.

## Why semvx?

- 🚀 **1.5x faster** than the original bash implementation
- 🎯 **Intelligent version calculation** from commit history
- 🔄 **Multi-language support** - Python, Rust, JavaScript, Bash
- 🤖 **AI-friendly** - Structured output for automation
- 📦 **Monorepo ready** - Manage versions across multiple projects
- ✅ **Safe operations** - Dry-run mode and automatic backups

## Installation

### Using pipx (Recommended)
```bash
pipx install -e .
```

### Using pip
```bash
pip install -e .
```

## Quick Start

```bash
# Check your project's version status
semvx status

# Calculate next version from commits
semvx next

# Bump version and update files
semvx bump minor

# Create a git tag
semvx tag
```

## Core Features

### Version Detection
Automatically detects and manages versions across multiple project types:
- **Python** - `pyproject.toml`, `setup.py`
- **Rust** - `Cargo.toml`
- **JavaScript** - `package.json`
- **Bash** - Version comments in scripts

### Intelligent Version Calculation
Analyzes commit messages using semv conventions:
- `major|breaking|api` → Major version bump
- `feat|feature|minor` → Minor version bump
- `fix|patch|bug` → Patch version bump

### Version Management
```bash
# View versions
semvx get all              # Show all detected versions
semvx get python           # Show Python version

# Update versions
semvx set python 2.1.0     # Set specific version
semvx sync                 # Sync all versions to highest

# Bump versions
semvx bump major           # Bump major version
semvx bump minor --dry-run # Preview changes
```

### Build Operations
```bash
semvx bc                   # Show build count
semvx build                # Generate build info file
```

### Remote Operations
```bash
semvx fetch                # Fetch remote tags
semvx remote               # Show latest remote tag
semvx upst                 # Compare local vs remote
```

### Workflow Integration
```bash
semvx validate             # Check version consistency
semvx audit                # Full repository audit
semvx pre-commit           # Pre-commit validation
```

## Command Reference

### Detection & Status
- `semvx detect` - Detect project types and versions
- `semvx status` - Show comprehensive version status
- `semvx version` - Display current project versions

### Version Operations
- `semvx next` - Calculate next version from commits
- `semvx get [TYPE]` - Get version from project files
- `semvx set TYPE VER` - Set version in project files
- `semvx sync [FILE]` - Synchronize versions across files

### Version Bumping
- `semvx bump [major|minor|patch]` - Bump version
- `semvx bump --dry-run` - Preview changes

### Git Operations
- `semvx tag [VERSION]` - Create git tag
- `semvx tags` - List all version tags
- `semvx fetch` - Fetch remote tags
- `semvx remote` - Show latest remote tag
- `semvx upst` - Compare with upstream

### Build & Workflow
- `semvx bc` - Show build count
- `semvx build [FILE]` - Generate build info
- `semvx validate` - Validate version consistency
- `semvx audit` - Repository audit
- `semvx pre-commit` - Pre-commit checks

## Output Modes

### Normal Mode (Human-Readable)
```bash
semvx status
```
Uses boxy for formatted output with visual hierarchy.

### Data Mode (Machine-Readable)
```bash
semvx status --view=data
```
Returns JSON for AI agents and automation tools.

## Performance

**Benchmarked against bash semv:**
- semvx: ~0.26s
- bash semv: ~0.39s
- **Result: 1.5x faster** ⚡

## Documentation

- **[Getting Started](docs/GETTING_STARTED.md)** - Quick start guide
- **[Installation](docs/INSTALL.md)** - Detailed installation
- **[Development](docs/DEVELOPMENT.md)** - Contributing guide
- **[Workflow](docs/procs/PROCESS.md)** - Complete workflow documentation

## License

See [LICENSE](LICENSE) file for details.
