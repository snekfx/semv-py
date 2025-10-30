"""
Tests for the reporting module.
"""

from pathlib import Path

import pytest

from semvx.detection.reporting import (
    detect_dirty_directories,
    detect_emerging_tools,
    detect_script_metadata,
    detect_standard_bin_tools,
    validate_project_structure,
)


class TestStandardTools:
    """Test standard bin tools detection."""

    def test_detect_standard_bin_tools_all_present(self, tmp_path):
        """Test when all standard tools exist."""
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        (bin_dir / "build.sh").write_text("#!/bin/bash\necho 'build'")
        (bin_dir / "deploy.sh").write_text("#!/bin/bash\necho 'deploy'")
        (bin_dir / "test.sh").write_text("#!/bin/bash\necho 'test'")
        (bin_dir / "snap.sh").write_text("#!/bin/bash\necho 'snap'")

        result = detect_standard_bin_tools(tmp_path)
        assert result["build.sh"]["exists"] is True
        assert result["deploy.sh"]["exists"] is True
        assert result["test.sh"]["exists"] is True
        assert result["snap.sh"]["exists"] is True

    def test_detect_standard_bin_tools_none_present(self, tmp_path):
        """Test when no standard tools exist."""
        result = detect_standard_bin_tools(tmp_path)
        assert result["build.sh"]["exists"] is False
        assert result["deploy.sh"]["exists"] is False
        assert result["test.sh"]["exists"] is False
        assert result["snap.sh"]["exists"] is False

    def test_detect_standard_bin_tools_partial(self, tmp_path):
        """Test when only some tools exist."""
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        (bin_dir / "build.sh").write_text("#!/bin/bash\necho 'build'")

        result = detect_standard_bin_tools(tmp_path)
        assert result["build.sh"]["exists"] is True
        assert result["deploy.sh"]["exists"] is False


class TestEmergingTools:
    """Test emerging tools detection."""

    def test_detect_makefile_uppercase(self, tmp_path):
        """Test Makefile detection (uppercase)."""
        (tmp_path / "Makefile").write_text("all:\n\techo 'make'")
        result = detect_emerging_tools(tmp_path)
        assert result["makefile"]["exists"] is True
        assert result["makefile"]["path"] == "./Makefile"

    def test_detect_makefile_lowercase(self, tmp_path):
        """Test makefile detection (lowercase)."""
        (tmp_path / "makefile").write_text("all:\n\techo 'make'")
        result = detect_emerging_tools(tmp_path)
        assert result["makefile"]["exists"] is True
        assert result["makefile"]["path"] == "./makefile"

    def test_detect_python_scripts(self, tmp_path):
        """Test Python script detection in bin/."""
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        (bin_dir / "script1.py").write_text("print('hello')")
        (bin_dir / "script2.py").write_text("print('world')")

        result = detect_emerging_tools(tmp_path)
        assert len(result["python_scripts"]) == 2
        assert "./bin/script1.py" in result["python_scripts"]
        assert "./bin/script2.py" in result["python_scripts"]


class TestScriptMetadata:
    """Test script metadata detection."""

    def test_detect_script_metadata_with_bin(self, tmp_path):
        """Test metadata when bin/ directory exists."""
        (tmp_path / "bin").mkdir()
        result = detect_script_metadata(tmp_path)
        assert result["bin_directory"] == "./bin"

    def test_detect_script_metadata_root_scripts(self, tmp_path):
        """Test detection of root-level scripts."""
        (tmp_path / "custom-tool.sh").write_text("#!/bin/bash\necho 'custom'")
        (tmp_path / "migrate.sh").write_text("#!/bin/bash\necho 'migrate'")

        result = detect_script_metadata(tmp_path)
        assert "./custom-tool.sh" in result["root_scripts"]
        assert "./migrate.sh" in result["root_scripts"]

    def test_detect_script_metadata_script_directories(self, tmp_path):
        """Test detection of script directories."""
        (tmp_path / "scripts").mkdir()
        (tmp_path / "tools").mkdir()

        result = detect_script_metadata(tmp_path)
        assert "./scripts" in result["script_directories"]
        assert "./tools" in result["script_directories"]


class TestDirtyDirectories:
    """Test build artifact detection."""

    def test_detect_dirty_directories_node_modules(self, tmp_path):
        """Test detection of node_modules."""
        (tmp_path / "node_modules").mkdir()
        result = detect_dirty_directories(tmp_path)
        assert "./node_modules" in result

    def test_detect_dirty_directories_multiple(self, tmp_path):
        """Test detection of multiple dirty directories."""
        (tmp_path / "node_modules").mkdir()
        (tmp_path / "target").mkdir()
        (tmp_path / "__pycache__").mkdir()

        result = detect_dirty_directories(tmp_path)
        assert "./node_modules" in result
        assert "./target" in result
        assert "./__pycache__" in result

    def test_detect_dirty_directories_none(self, tmp_path):
        """Test when no dirty directories exist."""
        result = detect_dirty_directories(tmp_path)
        assert result == []


class TestProjectValidation:
    """Test project structure validation."""

    def test_validate_project_structure_valid(self, tmp_path):
        """Test validation of valid project."""
        (tmp_path / "Cargo.toml").write_text(
            '[package]\nname = "test"\nversion = "1.2.3"'
        )
        projects = [
            {"type": "rust", "version_file": "Cargo.toml", "version": "1.2.3"}
        ]

        result = validate_project_structure(tmp_path, projects)
        assert result["rust"]["ok"] is True
        assert result["rust"]["version"] == "1.2.3"

    def test_validate_project_structure_no_version_file(self, tmp_path):
        """Test validation when version file doesn't exist."""
        projects = [
            {"type": "rust", "version_file": "Cargo.toml", "version": "1.2.3"}
        ]

        result = validate_project_structure(tmp_path, projects)
        assert result["rust"]["ok"] is False
        assert result["rust"]["reason"] == "version_file_missing"

    def test_validate_project_structure_unknown_type(self, tmp_path):
        """Test validation of unknown project type."""
        projects = [{"type": "unknown", "version_file": None, "version": None}]

        result = validate_project_structure(tmp_path, projects)
        assert result["unknown"]["ok"] is False
        assert result["unknown"]["reason"] == "no_detectable_project"
