# SEMVX Deployment Guide

## Package Information

- **Package Name:** `semvx`
- **CLI Command:** `semvx`
- **Python Module:** `semvx`
- **Version:** 3.0.0-dev (update before release)

## Pre-Deployment Checklist

### 1. Update Version
```bash
# Update version in pyproject.toml
# Current: version = "3.0.0-dev"
# Release: version = "3.0.0"
```

### 2. Run Full Test Suite
```bash
make test
make test-quick
make cli-test
```

### 3. Verify Package Build
```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Check distribution
twine check dist/*
```

### 4. Test Local Installation
```bash
# Install in development mode
pip install -e .

# Test CLI
semvx --version
semvx detect
semvx status
semvx bump patch --dry-run
semvx tag --help
```

## Deployment to PyPI

### Test PyPI (Recommended First)

```bash
# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ semvx

# Verify
semvx --version
```

### Production PyPI

```bash
# Upload to PyPI
twine upload dist/*

# Verify
pip install semvx
semvx --version
```

## Post-Deployment

### 1. Create Git Tag
```bash
git tag -a v3.0.0 -m "Release v3.0.0"
git push origin v3.0.0
```

### 2. Update Documentation
- Update README.md with installation instructions
- Update CHANGELOG.md with release notes
- Update version in docs

### 3. Verify Installation
```bash
# Fresh virtual environment
python -m venv test-env
source test-env/bin/activate
pip install semvx

# Test commands
semvx detect
semvx --help
```

## Namespace Separation

**IMPORTANT:** This package uses `semvx` to avoid conflicts with the bash `semv` tool.

- ✅ Bash tool: `semv` (remains unchanged)
- ✅ Python tool: `semvx` (new, no conflicts)
- ✅ Both can coexist on the same system

## Version Management

### Semantic Versioning
- **Major (X.0.0):** Breaking changes
- **Minor (X.Y.0):** New features, backward compatible
- **Patch (X.Y.Z):** Bug fixes, backward compatible

### Pre-release Versions
- **Alpha:** `3.0.0-alpha.1`
- **Beta:** `3.0.0-beta.1`
- **RC:** `3.0.0-rc.1`

## Distribution Files

After building, you'll have:
```
dist/
├── semvx-3.0.0-py3-none-any.whl  # Wheel distribution
└── semvx-3.0.0.tar.gz            # Source distribution
```

## Installation Methods

### From PyPI (Production)
```bash
pip install semvx
```

### From Test PyPI
```bash
pip install --index-url https://test.pypi.org/simple/ semvx
```

### From Source
```bash
git clone https://github.com/semv-tools/semv-py.git
cd semv-py
pip install -e .
```

### From Wheel
```bash
pip install semvx-3.0.0-py3-none-any.whl
```

## Troubleshooting

### Command Not Found
If `semvx` command is not found after installation:
```bash
# Check if it's installed
pip show semvx

# Check PATH
which semvx

# Try with python -m
python -m semvx.cli.main --version
```

### Import Errors
```bash
# Verify installation
python -c "import semvx; print(semvx.__version__)"

# Reinstall if needed
pip uninstall semvx
pip install semvx
```

## Development Installation

For contributors:
```bash
# Clone repository
git clone https://github.com/semv-tools/semv-py.git
cd semv-py

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run tests
make test

# Run CLI
semvx --help
```

## CI/CD Integration

### GitHub Actions
The project includes CI/CD workflows in `.github/workflows/`:
- `test.yml` - Run tests on multiple Python versions
- `quick-check.yml` - Quick validation for branches

### Automated Publishing
To set up automated PyPI publishing:
1. Add PyPI API token to GitHub secrets
2. Create release workflow
3. Tag releases trigger automatic deployment

## Support

- **Issues:** https://github.com/semv-tools/semv-py/issues
- **Documentation:** https://docs.semv.tools
- **Email:** dev@semv.tools
