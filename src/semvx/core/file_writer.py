"""
File writer module for updating version information in manifest files.

Supports atomic file operations with backup for safe version updates.
"""

import re
import shutil
from pathlib import Path
from typing import Optional, Tuple

from semvx.core.version import SemanticVersion


class FileWriteError(Exception):
    """Raised when file writing operations fail."""

    pass


class VersionFileWriter:
    """
    Handles writing version updates to various manifest file formats.

    Supports:
    - pyproject.toml (Python)
    - Cargo.toml (Rust)
    - package.json (JavaScript)
    """

    @staticmethod
    def update_version_in_file(
        file_path: Path, new_version: SemanticVersion, backup: bool = True
    ) -> Tuple[bool, str]:
        """
        Update version in a manifest file.

        Args:
            file_path: Path to the manifest file
            new_version: New semantic version to write
            backup: Whether to create a backup before writing

        Returns:
            Tuple of (success: bool, message: str)

        Raises:
            FileWriteError: If file operations fail
        """
        if not file_path.exists():
            raise FileWriteError(f"File not found: {file_path}")

        # Determine file type and update strategy
        file_name = file_path.name.lower()

        if file_name == "pyproject.toml":
            return VersionFileWriter._update_pyproject_toml(file_path, new_version, backup)
        elif file_name == "cargo.toml":
            return VersionFileWriter._update_cargo_toml(file_path, new_version, backup)
        elif file_name == "package.json":
            return VersionFileWriter._update_package_json(file_path, new_version, backup)
        else:
            return False, f"Unsupported file type: {file_name}"

    @staticmethod
    def _create_backup(file_path: Path) -> Optional[Path]:
        """Create a backup of the file."""
        try:
            backup_path = file_path.with_suffix(file_path.suffix + ".bak")
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception as e:
            raise FileWriteError(f"Failed to create backup: {e}")

    @staticmethod
    def _update_pyproject_toml(
        file_path: Path, new_version: SemanticVersion, backup: bool
    ) -> Tuple[bool, str]:
        """Update version in pyproject.toml."""
        try:
            content = file_path.read_text()

            # Pattern: version = "X.Y.Z" or version = "X.Y.Z-prerelease"
            pattern = r'^version\s*=\s*["\']([^"\']+)["\']'
            new_line = f'version = "{new_version}"'

            # Check if version line exists
            if not re.search(pattern, content, re.MULTILINE):
                return False, "No version field found in pyproject.toml"

            # Create backup if requested
            if backup:
                VersionFileWriter._create_backup(file_path)

            # Replace version line
            updated_content = re.sub(pattern, new_line, content, count=1, flags=re.MULTILINE)

            # Write updated content
            file_path.write_text(updated_content)

            return True, f"Updated {file_path.name} to version {new_version}"

        except Exception as e:
            raise FileWriteError(f"Failed to update pyproject.toml: {e}")

    @staticmethod
    def _update_cargo_toml(
        file_path: Path, new_version: SemanticVersion, backup: bool
    ) -> Tuple[bool, str]:
        """Update version in Cargo.toml."""
        try:
            content = file_path.read_text()

            # Pattern: version = "X.Y.Z"
            pattern = r'^version\s*=\s*["\']([^"\']+)["\']'
            new_line = f'version = "{new_version}"'

            if not re.search(pattern, content, re.MULTILINE):
                return False, "No version field found in Cargo.toml"

            if backup:
                VersionFileWriter._create_backup(file_path)

            updated_content = re.sub(pattern, new_line, content, count=1, flags=re.MULTILINE)

            file_path.write_text(updated_content)

            return True, f"Updated {file_path.name} to version {new_version}"

        except Exception as e:
            raise FileWriteError(f"Failed to update Cargo.toml: {e}")

    @staticmethod
    def _update_package_json(
        file_path: Path, new_version: SemanticVersion, backup: bool
    ) -> Tuple[bool, str]:
        """Update version in package.json."""
        try:
            import json

            content = file_path.read_text()
            data = json.loads(content)

            if "version" not in data:
                return False, "No version field found in package.json"

            if backup:
                VersionFileWriter._create_backup(file_path)

            # Update version
            data["version"] = str(new_version)

            # Write with pretty formatting (2-space indent, common for package.json)
            updated_content = json.dumps(data, indent=2, ensure_ascii=False)
            # Add trailing newline (common convention)
            updated_content += "\n"

            file_path.write_text(updated_content)

            return True, f"Updated {file_path.name} to version {new_version}"

        except json.JSONDecodeError as e:
            raise FileWriteError(f"Invalid JSON in package.json: {e}")
        except Exception as e:
            raise FileWriteError(f"Failed to update package.json: {e}")
