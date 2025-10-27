"""
Shared test fixtures and configuration for SEMVX tests.
"""

import json
import shutil
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test isolation."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # Cleanup after test
    if temp_path.exists():
        shutil.rmtree(temp_path)


@pytest.fixture
def python_project(temp_dir):
    """Create a mock Python project structure."""
    # Create pyproject.toml
    pyproject_content = """[project]
name = "test-project"
version = "1.2.3"
description = "Test Python project"

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
"""
    (temp_dir / "pyproject.toml").write_text(pyproject_content)

    # Create src directory
    src_dir = temp_dir / "src" / "test_project"
    src_dir.mkdir(parents=True)
    (src_dir / "__init__.py").write_text('__version__ = "1.2.3"')

    return temp_dir


@pytest.fixture
def rust_project(temp_dir):
    """Create a mock Rust project structure."""
    cargo_content = """[package]
name = "test-rust"
version = "2.3.4"
edition = "2021"

[dependencies]
"""
    (temp_dir / "Cargo.toml").write_text(cargo_content)

    # Create src directory
    src_dir = temp_dir / "src"
    src_dir.mkdir()
    (src_dir / "main.rs").write_text('fn main() { println!("Hello"); }')

    return temp_dir


@pytest.fixture
def javascript_project(temp_dir):
    """Create a mock JavaScript project structure."""
    package_json = {
        "name": "test-js",
        "version": "3.4.5",
        "description": "Test JavaScript project",
        "main": "index.js",
        "scripts": {
            "test": "echo 'Test'"
        }
    }
    (temp_dir / "package.json").write_text(json.dumps(package_json, indent=2))
    (temp_dir / "index.js").write_text('console.log("Hello");')

    return temp_dir


@pytest.fixture
def git_repository(temp_dir):
    """Create a git repository in the temp directory."""
    import subprocess

    # Initialize git repo
    subprocess.run(["git", "init"], cwd=temp_dir, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=temp_dir, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=temp_dir, capture_output=True)

    # Create and commit a file
    (temp_dir / "README.md").write_text("# Test Project")
    subprocess.run(["git", "add", "."], cwd=temp_dir, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=temp_dir, capture_output=True)

    return temp_dir


@pytest.fixture
def multi_project(temp_dir, git_repository):
    """Create a repository with multiple project types."""
    # Python project in root
    pyproject_content = """[project]
name = "multi-project"
version = "1.0.0"
"""
    (temp_dir / "pyproject.toml").write_text(pyproject_content)

    # Rust subproject
    rust_dir = temp_dir / "rust-component"
    rust_dir.mkdir()
    cargo_content = """[package]
name = "rust-component"
version = "1.0.0"
edition = "2021"
"""
    (rust_dir / "Cargo.toml").write_text(cargo_content)

    # JavaScript subproject
    js_dir = temp_dir / "js-frontend"
    js_dir.mkdir()
    package_json = {
        "name": "js-frontend",
        "version": "1.0.0"
    }
    (js_dir / "package.json").write_text(json.dumps(package_json, indent=2))

    return temp_dir
