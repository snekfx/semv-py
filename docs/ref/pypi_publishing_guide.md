# PyPI Publishing Guide for semv-py

Quick reference for publishing your SEMV Python package to PyPI.

## Prerequisites

```bash
# Install build and upload tools
pip install build twine

# Make sure you have a PyPI account
# Register at: https://pypi.org/account/register/
```

## Project Setup

### 1. Verify pyproject.toml
```toml
[project]
name = "semv-py"
version = "3.0.0"
description = "SEMV - Semantic Version Manager for multi-language version synchronization"
# ... rest of config from buildout plan
```

### 2. Required Files
```
semv-py/
├── pyproject.toml          # Package configuration
├── README.md               # Package description
├── LICENSE                 # License file (MIT recommended)
└── semv/                   # Your Python package
    ├── __init__.py
    ├── cli.py
    └── ...
```

## Publishing Process

### 1. Clean Previous Builds
```bash
rm -rf dist/ build/ *.egg-info/
```

### 2. Build Package
```bash
python -m build
```
This creates:
- `dist/semv_py-3.0.0.tar.gz` (source distribution)
- `dist/semv_py-3.0.0-py3-none-any.whl` (wheel)

### 3. Test Build Locally
```bash
# Test install from wheel
pip install dist/semv_py-3.0.0-py3-none-any.whl

# Test the CLI
semv --version
```

### 4. Upload to PyPI

#### First Time Setup
```bash
# Configure PyPI credentials (one time)
python -m twine configure

# Or create ~/.pypirc manually:
cat > ~/.pypirc << EOF
[pypi]
username = your_pypi_username
password = your_pypi_password
EOF
```

#### Upload
```bash
# Upload to PyPI
python -m twine upload dist/*

# Or test first on TestPyPI
python -m twine upload --repository testpypi dist/*
```

## Verification

### 1. Check PyPI Page
Visit: https://pypi.org/project/semv-py/

### 2. Test Installation
```bash
# Clean install test
pip uninstall semv-py
pip install semv-py

# Verify CLI works
semv --version
semv --help
```

## Version Updates

### 1. Update Version
```toml
# pyproject.toml
[project]
version = "3.0.1"  # Bump version
```

### 2. Rebuild and Upload
```bash
rm -rf dist/
python -m build
python -m twine upload dist/*
```

## Quick Commands Reference

```bash
# Complete publishing workflow
rm -rf dist/ && python -m build && python -m twine upload dist/*

# Test on TestPyPI first
rm -rf dist/ && python -m build && python -m twine upload --repository testpypi dist/*

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ semv-py
```

## Troubleshooting

### Common Issues

**"File already exists"**: Version already uploaded, bump version number

**"Invalid authentication"**: Check PyPI username/password or use API token

**"Package name taken"**: `semv-py` should be available, but check alternatives

**CLI not working**: Verify `[project.scripts]` in pyproject.toml:
```toml
[project.scripts]
semv = "semv.cli:cli"
```

### Using API Tokens (Recommended)
1. Generate token at: https://pypi.org/manage/account/token/
2. Use as password with username `__token__`

```bash
python -m twine upload --username __token__ --password your-api-token dist/*
```

## Automation (Optional)

### GitHub Actions
```yaml
# .github/workflows/publish.yml
name: Publish to PyPI
on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.x'
      - run: pip install build twine
      - run: python -m build
      - run: python -m twine upload dist/*
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
```

## First Release Checklist

- [ ] Project name `semv-py` confirmed available
- [ ] pyproject.toml configured correctly
- [ ] README.md written
- [ ] LICENSE file added
- [ ] Version set to "3.0.0"
- [ ] Package builds without errors
- [ ] CLI command `semv` works after local install
- [ ] PyPI credentials configured
- [ ] Package uploaded successfully
- [ ] Installation from PyPI verified

That's it! Once published, users can simply:
```bash
pip install semv-py
semv --help
```