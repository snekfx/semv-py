"""
Unit tests for the detection module.
"""

import pytest
from pathlib import Path
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from semvx.detection.detector import (
    get_repository_context,
    normalize_semver,
    compare_semver,
    get_highest_version,
    detect_python_project,
    detect_rust_project,
    detect_javascript_project
)


class TestSemverUtilities:
    """Test semantic version utility functions."""

    def test_normalize_semver_basic(self):
        """Test basic version normalization."""
        assert normalize_semver("1.2.3") == "v1.2.3"
        assert normalize_semver("v1.2.3") == "v1.2.3"
        assert normalize_semver("1.2") == "v1.2.0"
        assert normalize_semver("") == "v0.0.0"

    def test_normalize_semver_prerelease(self):
        """Test normalization with pre-release versions."""
        assert normalize_semver("1.2.3-alpha") == "v1.2.3"
        assert normalize_semver("v1.2.3-beta.1") == "v1.2.3"
        assert normalize_semver("1.2.3-rc.1+build.123") == "v1.2.3"

    def test_compare_semver(self):
        """Test semantic version comparison."""
        assert compare_semver("1.2.3", "1.2.4") == -1
        assert compare_semver("2.0.0", "1.9.9") == 1
        assert compare_semver("1.2.3", "1.2.3") == 0
        assert compare_semver("v1.2.3", "1.2.3") == 0

    def test_get_highest_version(self):
        """Test finding highest version from list."""
        versions = ["1.2.3", "2.0.0", "1.9.9", "2.0.1"]
        assert get_highest_version(versions) == "v2.0.1"

        versions = ["v0.0.1", "0.0.2", "v0.0.3"]
        assert get_highest_version(versions) == "v0.0.3"

        assert get_highest_version([]) == "v0.0.0"


class TestProjectDetection:
    """Test project type detection functions."""

    def test_detect_python_project(self, python_project):
        """Test Python project detection."""
        projects = detect_python_project(python_project)
        assert len(projects) == 1
        assert projects[0]["type"] == "python"
        assert projects[0]["version"] == "1.2.3"
        assert projects[0]["version_file"] == "pyproject.toml"

    def test_detect_rust_project(self, rust_project):
        """Test Rust project detection."""
        projects = detect_rust_project(rust_project)
        assert len(projects) == 1
        assert projects[0]["type"] == "rust"
        assert projects[0]["version"] == "2.3.4"
        assert projects[0]["version_file"] == "Cargo.toml"

    def test_detect_javascript_project(self, javascript_project):
        """Test JavaScript project detection."""
        projects = detect_javascript_project(javascript_project)
        assert len(projects) == 1
        assert projects[0]["type"] == "javascript"
        assert projects[0]["version"] == "3.4.5"
        assert projects[0]["version_file"] == "package.json"

    def test_no_project_detection(self, temp_dir):
        """Test behavior when no project is found."""
        projects = detect_python_project(temp_dir)
        assert len(projects) == 0

        projects = detect_rust_project(temp_dir)
        assert len(projects) == 0

        projects = detect_javascript_project(temp_dir)
        assert len(projects) == 0


class TestRepositoryContext:
    """Test full repository context detection."""

    def test_git_repository_detection(self, git_repository):
        """Test git repository detection."""
        context = get_repository_context(git_repository)
        assert context["repository"]["type"] == "git"
        assert context["repository"]["root"] == str(git_repository)

    def test_multi_project_detection(self, multi_project):
        """Test detection of multiple project types."""
        context = get_repository_context(multi_project)
        assert context["repository"]["type"] == "git"

        # Should find all three projects
        project_types = [p["type"] for p in context["projects"]]
        assert "python" in project_types
        assert "rust" in project_types
        assert "javascript" in project_types

        # All should have version 1.0.0
        versions = [p["version"] for p in context["projects"]]
        assert all(v == "1.0.0" for v in versions)

    def test_validation_results(self, python_project):
        """Test validation results in context."""
        context = get_repository_context(python_project)
        assert "validation" in context
        assert "python" in context["validation"]
        assert context["validation"]["python"]["ok"] is True

    def test_empty_directory(self, temp_dir):
        """Test detection in empty directory."""
        context = get_repository_context(temp_dir)
        assert context["repository"]["type"] == "directory"
        assert len(context["projects"]) == 0
        assert context["validation"] == {}