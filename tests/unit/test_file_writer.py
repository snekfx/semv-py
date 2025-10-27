"""Tests for file writer module."""

import json

import pytest

from semvx.core.file_writer import FileWriteError, VersionFileWriter
from semvx.core.version import SemanticVersion


class TestVersionFileWriter:
    """Test VersionFileWriter functionality."""

    def test_update_pyproject_toml(self, tmp_path):
        """Test updating version in pyproject.toml."""
        # Create test file
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            """[project]
name = "test-project"
version = "1.2.3"
description = "Test project"
"""
        )

        new_version = SemanticVersion(2, 0, 0)
        success, message = VersionFileWriter.update_version_in_file(
            pyproject, new_version, backup=False
        )

        assert success
        assert "2.0.0" in message

        # Verify content
        content = pyproject.read_text()
        assert 'version = "2.0.0"' in content
        assert 'version = "1.2.3"' not in content

    def test_update_pyproject_toml_with_backup(self, tmp_path):
        """Test backup creation when updating pyproject.toml."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            """[project]
name = "test"
version = "1.0.0"
"""
        )

        new_version = SemanticVersion(1, 1, 0)
        success, _ = VersionFileWriter.update_version_in_file(pyproject, new_version, backup=True)

        assert success

        # Check backup exists
        backup = tmp_path / "pyproject.toml.bak"
        assert backup.exists()
        assert 'version = "1.0.0"' in backup.read_text()

    def test_update_cargo_toml(self, tmp_path):
        """Test updating version in Cargo.toml."""
        cargo = tmp_path / "Cargo.toml"
        cargo.write_text(
            """[package]
name = "test-crate"
version = "0.1.0"
edition = "2021"
"""
        )

        new_version = SemanticVersion(0, 2, 0)
        success, message = VersionFileWriter.update_version_in_file(
            cargo, new_version, backup=False
        )

        assert success
        assert "0.2.0" in message

        content = cargo.read_text()
        assert 'version = "0.2.0"' in content

    def test_update_package_json(self, tmp_path):
        """Test updating version in package.json."""
        package = tmp_path / "package.json"
        data = {"name": "test-package", "version": "1.0.0", "description": "Test"}
        package.write_text(json.dumps(data, indent=2))

        new_version = SemanticVersion(1, 5, 0)
        success, message = VersionFileWriter.update_version_in_file(
            package, new_version, backup=False
        )

        assert success
        assert "1.5.0" in message

        # Verify JSON is still valid and formatted
        updated_data = json.loads(package.read_text())
        assert updated_data["version"] == "1.5.0"
        assert updated_data["name"] == "test-package"

    def test_update_with_prerelease(self, tmp_path):
        """Test updating to version with pre-release."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nversion = "1.0.0"\n')

        new_version = SemanticVersion(2, 0, 0, prerelease="alpha.1")
        success, _ = VersionFileWriter.update_version_in_file(pyproject, new_version, backup=False)

        assert success
        content = pyproject.read_text()
        assert 'version = "2.0.0-alpha.1"' in content

    def test_file_not_found(self, tmp_path):
        """Test error when file doesn't exist."""
        nonexistent = tmp_path / "missing.toml"
        new_version = SemanticVersion(1, 0, 0)

        with pytest.raises(FileWriteError, match="File not found"):
            VersionFileWriter.update_version_in_file(nonexistent, new_version, backup=False)

    def test_unsupported_file_type(self, tmp_path):
        """Test handling of unsupported file types."""
        unknown = tmp_path / "version.txt"
        unknown.write_text("1.0.0")

        new_version = SemanticVersion(2, 0, 0)
        success, message = VersionFileWriter.update_version_in_file(
            unknown, new_version, backup=False
        )

        assert not success
        assert "Unsupported file type" in message

    def test_no_version_field(self, tmp_path):
        """Test handling when version field is missing."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "test"\n')

        new_version = SemanticVersion(1, 0, 0)
        success, message = VersionFileWriter.update_version_in_file(
            pyproject, new_version, backup=False
        )

        assert not success
        assert "No version field found" in message

    def test_invalid_json(self, tmp_path):
        """Test handling of invalid JSON in package.json."""
        package = tmp_path / "package.json"
        package.write_text('{"name": "test", invalid json}')

        new_version = SemanticVersion(1, 0, 0)

        with pytest.raises(FileWriteError, match="Invalid JSON"):
            VersionFileWriter.update_version_in_file(package, new_version, backup=False)
