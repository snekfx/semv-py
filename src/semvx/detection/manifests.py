"""
Manifest Detection Module - Language-specific project detection.
Part of the shared detection library.

This module handles detection and version extraction for:
- Rust (Cargo.toml)
- JavaScript/Node.js (package.json)
- Python (pyproject.toml, setup.py)
- Bash (scripts with version comments)

Zero dependencies - pure Python standard library only.
"""

import json
import re
from pathlib import Path
from typing import Optional

# ============================================================================
# Manifest File Detection (High Confidence Project Types)
# ============================================================================


def has_rust_manifest(repo_path: Path) -> bool:
    """
    Check for Rust project manifest (Cargo.toml with [package] section).

    Args:
        repo_path: Path to repository directory

    Returns:
        True if valid Rust manifest exists, False otherwise
    """
    cargo_toml = repo_path / "Cargo.toml"
    if not cargo_toml.exists():
        return False

    try:
        content = cargo_toml.read_text(encoding="utf-8")
        # Simple check for [package] section
        return "[package]" in content
    except (OSError, UnicodeDecodeError):
        return False


def has_javascript_manifest(repo_path: Path) -> bool:
    """
    Check for JavaScript project manifest (package.json with version field).

    Args:
        repo_path: Path to repository directory

    Returns:
        True if valid JavaScript manifest exists, False otherwise
    """
    package_json = repo_path / "package.json"
    if not package_json.exists():
        return False

    try:
        content = package_json.read_text(encoding="utf-8")
        data = json.loads(content)
        return isinstance(data, dict) and "version" in data
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return False


def has_python_manifest(repo_path: Path) -> bool:
    """
    Check for Python project manifest (pyproject.toml [project] OR setup.py).

    Priority: pyproject.toml preferred over setup.py when both exist.

    Args:
        repo_path: Path to repository directory

    Returns:
        True if valid Python manifest exists, False otherwise
    """
    # Check for pyproject.toml first (modern Python packaging)
    pyproject_toml = repo_path / "pyproject.toml"
    if pyproject_toml.exists():
        try:
            content = pyproject_toml.read_text(encoding="utf-8")
            # Check for [project] section (PEP 621) or [tool.poetry] (Poetry)
            return "[project]" in content or "[tool.poetry]" in content
        except (OSError, UnicodeDecodeError):
            pass

    # Check for setup.py as fallback
    setup_py = repo_path / "setup.py"
    if setup_py.exists():
        try:
            content = setup_py.read_text(encoding="utf-8")
            # Simple heuristic: contains setup() call and version parameter
            return "setup(" in content and "version" in content
        except (OSError, UnicodeDecodeError):
            pass

    return False


# ============================================================================
# Bash Pattern Detection (Complex, Multiple Patterns)
# ============================================================================


def is_generated_file(file_path: Path) -> bool:
    """
    Check if file contains '# generated' tag (build artifact protection).

    Args:
        file_path: Path to file to check

    Returns:
        True if file is marked as generated, False otherwise
    """
    try:
        # Only check first few lines for performance
        with file_path.open("r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i > 10:  # Only check first 10 lines
                    break
                if "# generated" in line.lower():
                    return True
        return False
    except (OSError, UnicodeDecodeError):
        return False


def has_version_comment(file_path: Path) -> bool:
    """
    Check if bash script contains version comment.

    Looks for patterns like:
    - # semv-version: 1.2.3
    - # version: 1.2.3

    Args:
        file_path: Path to script file

    Returns:
        True if version comment found, False otherwise
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        # Look for version comment patterns
        patterns = [r"#\s*semv-version:\s*\S+", r"#\s*version:\s*\S+"]
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False
    except (OSError, UnicodeDecodeError):
        return False


def detect_bash_patterns(repo_path: Path) -> Optional[str]:
    """
    Detect which of 5 bash patterns applies to repository.

    Patterns (in priority order):
    1. bashfx-buildsh: build.sh + parts/ + build.map
    2. bashfx-simple: prefix-name/ folder with name.sh
    3. standalone: foldername.sh with version comment
    4. semvrc: .semvrc configuration file
    5. generic: .sh files with version comments (excluding generated)

    Args:
        repo_path: Path to repository directory

    Returns:
        Pattern name if detected, None if no pattern matches
    """
    repo_path = Path(repo_path).resolve()

    # Pattern 1: BashFX build.sh (build.sh + parts/ directory)
    if (
        (repo_path / "build.sh").exists()
        and (repo_path / "parts").exists()
        and (repo_path / "parts").is_dir()
    ):
        return "bashfx-buildsh"

    # Pattern 2: BashFX simple (prefix-name/ directory with name.sh)
    for item in repo_path.iterdir():
        if item.is_dir() and "-" in item.name:
            # Look for name.sh inside prefix-name/ directory
            prefix, name = item.name.split("-", 1)
            script_file = item / f"{name}.sh"
            if script_file.exists():
                return "bashfx-simple"

    # Pattern 3: Standalone (foldername.sh matching directory name)
    expected_script = repo_path / f"{repo_path.name}.sh"
    if expected_script.exists() and has_version_comment(expected_script):
        return "standalone"

    # Pattern 4: semvrc (legacy .semvrc configuration)
    if (repo_path / ".semvrc").exists():
        return "semvrc"

    # Pattern 5: Generic (any .sh file with version comments, excluding generated)
    for script in repo_path.glob("*.sh"):
        if is_generated_file(script):
            continue  # Skip generated files
        if has_version_comment(script):
            return "generic"

    return None


def get_bash_project_file(repo_path: Path, pattern: str) -> Optional[Path]:
    """
    Get the actual file containing version info for detected bash pattern.

    Routes from generated files to source files when needed.

    Args:
        repo_path: Path to repository directory
        pattern: Detected bash pattern name

    Returns:
        Path to file containing version information, or None if not found
    """
    repo_path = Path(repo_path).resolve()

    if pattern == "bashfx-buildsh":
        # For build.sh projects, version is typically in parts/01_config.sh or similar
        parts_dir = repo_path / "parts"
        if parts_dir.exists():
            # Look for version in numbered parts files
            for part_file in sorted(parts_dir.glob("*.sh")):
                if has_version_comment(part_file):
                    return part_file
        # Fallback to build.sh itself
        return repo_path / "build.sh"

    elif pattern == "bashfx-simple":
        # Find the main script in prefix-name/ directory
        for item in repo_path.iterdir():
            if item.is_dir() and "-" in item.name:
                prefix, name = item.name.split("-", 1)
                script_file = item / f"{name}.sh"
                if script_file.exists():
                    return script_file

    elif pattern == "standalone":
        return repo_path / f"{repo_path.name}.sh"

    elif pattern == "semvrc":
        # Parse .semvrc to find BASH_VERSION_FILE
        semvrc = repo_path / ".semvrc"
        try:
            content = semvrc.read_text(encoding="utf-8")
            # Look for BASH_VERSION_FILE=path
            match = re.search(r"BASH_VERSION_FILE=([^\s]+)", content)
            if match:
                return repo_path / match.group(1)
        except (OSError, UnicodeDecodeError):
            pass

    elif pattern == "generic":
        # Find first .sh file with version comment (excluding generated)
        for script in repo_path.glob("*.sh"):
            if not is_generated_file(script) and has_version_comment(script):
                return script

    return None


# ============================================================================
# Version Extraction Functions
# ============================================================================


def extract_rust_version(file_path: Path) -> Optional[str]:
    """
    Extract version from Rust Cargo.toml file.

    Args:
        file_path: Path to Cargo.toml file

    Returns:
        Version string if found, None otherwise
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        # Simple regex for version in [package] section
        # This avoids needing a TOML parser dependency
        match = re.search(r'\[package\].*?version\s*=\s*["\']([^"\']+)["\']', content, re.DOTALL)
        if match:
            return match.group(1)
    except (OSError, UnicodeDecodeError):
        pass
    return None


def extract_javascript_version(file_path: Path) -> Optional[str]:
    """
    Extract version from JavaScript package.json file.

    Args:
        file_path: Path to package.json file

    Returns:
        Version string if found, None otherwise
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        data = json.loads(content)
        return data.get("version")
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        pass
    return None


def extract_python_version(file_path: Path) -> Optional[str]:
    """
    Extract version from Python project files (pyproject.toml or setup.py).

    Args:
        file_path: Path to pyproject.toml or setup.py file

    Returns:
        Version string if found, None otherwise
    """
    try:
        content = file_path.read_text(encoding="utf-8")

        if file_path.name == "pyproject.toml":
            # Look for [project] version or [tool.poetry] version
            patterns = [
                r'\[project\].*?version\s*=\s*["\']([^"\']+)["\']',
                r'\[tool\.poetry\].*?version\s*=\s*["\']([^"\']+)["\']',
            ]
            for pattern in patterns:
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    return match.group(1)

        elif file_path.name == "setup.py":
            # Look for version in setup() call
            patterns = [r'version\s*=\s*["\']([^"\']+)["\']', r"version\s*=\s*([^,\s)]+)"]
            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    version = match.group(1).strip("'\"")
                    return version

    except (OSError, UnicodeDecodeError):
        pass
    return None


def extract_bash_version(file_path: Path) -> Optional[str]:
    """
    Extract version from bash script version comments.

    Looks for patterns like:
    - # semv-version: 1.2.3
    - # version: 1.2.3

    Excludes lines with code artifacts ($ variables, quotes).

    Args:
        file_path: Path to bash script file

    Returns:
        Version string if found, None otherwise
    """
    try:
        content = file_path.read_text(encoding="utf-8")

        patterns = [r"#\s*semv-version:\s*([^\s]+)", r"#\s*version:\s*([^\s]+)"]

        for line in content.split("\n"):
            # Skip lines with code artifacts
            if "$" in line or '"' in line:
                continue

            for pattern in patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    return match.group(1)

    except (OSError, UnicodeDecodeError):
        pass
    return None
