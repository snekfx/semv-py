"""
Shared Project Detection Library - Core Module
Version: 1.0.0
Last Updated: 2025-10-26
Compatible: SEMV v3.0+, Blade Next v1.0+
Distribution: Copy into target projects (no dependency)

Zero dependencies - pure Python standard library only.

Note: Foundation functions moved to foundations.py for better organization.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Union

# Import foundation functions
from .foundations import (
    detect_repository_type,
    validate_gitsim_environment,
    validate_semver_format,
)

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


# ============================================================================
# Project Detection with Fallback Hierarchy
# ============================================================================


def detect_projects(repo_path: Path) -> List[Dict[str, Union[str, None]]]:
    """
    Detect all projects in repository with fallback hierarchy.

    Detection Priority:
    1. Manifest files (Cargo.toml, package.json, pyproject.toml)
    2. BashFX patterns (structured bash projects)
    3. Simple bash fallback (any .sh with version comments)
    4. Unknown project type (git repo but no detectable patterns)

    Args:
        repo_path: Path to repository directory

    Returns:
        List of project dictionaries:
        [
            {
                "type": "rust|javascript|python|bash|unknown",
                "root": "./relative/path",
                "version_file": "relative/path/to/file",
                "version": "extracted_version"
            }
        ]
    """
    repo_path = Path(repo_path).resolve()
    projects = []

    # Priority 1: Manifest files (high confidence)
    if has_rust_manifest(repo_path):
        version_file = repo_path / "Cargo.toml"
        version = extract_rust_version(version_file)
        projects.append(
            {"type": "rust", "root": "./", "version_file": "Cargo.toml", "version": version}
        )

    if has_javascript_manifest(repo_path):
        version_file = repo_path / "package.json"
        version = extract_javascript_version(version_file)
        projects.append(
            {"type": "javascript", "root": "./", "version_file": "package.json", "version": version}
        )

    if has_python_manifest(repo_path):
        # Prefer pyproject.toml over setup.py
        if (repo_path / "pyproject.toml").exists():
            version_file = repo_path / "pyproject.toml"
            version_file_name = "pyproject.toml"
        else:
            version_file = repo_path / "setup.py"
            version_file_name = "setup.py"

        version = extract_python_version(version_file)
        projects.append(
            {"type": "python", "root": "./", "version_file": version_file_name, "version": version}
        )

    # Priority 2: BashFX patterns (structured bash projects)
    bash_pattern = detect_bash_patterns(repo_path)
    if bash_pattern and bash_pattern != "generic":
        bash_file = get_bash_project_file(repo_path, bash_pattern)
        if bash_file:
            version = extract_bash_version(bash_file)
            # Make path relative to repo root
            relative_path = bash_file.relative_to(repo_path)
            projects.append(
                {
                    "type": "bash",
                    "root": "./",
                    "version_file": str(relative_path),
                    "version": version,
                }
            )

    # Priority 3: Simple bash fallback (only if no manifest files or BashFX)
    elif not projects and bash_pattern == "generic":
        bash_file = get_bash_project_file(repo_path, bash_pattern)
        if bash_file:
            version = extract_bash_version(bash_file)
            relative_path = bash_file.relative_to(repo_path)
            projects.append(
                {
                    "type": "bash",
                    "root": "./",
                    "version_file": str(relative_path),
                    "version": version,
                }
            )

    # Priority 4: Unknown project type (git repo but no detectable patterns)
    elif not projects and detect_repository_type(repo_path) in ["git", "gitsim"]:
        projects.append({"type": "unknown", "root": "./", "version_file": None, "version": None})

    return projects


# ============================================================================
# Validation Functions
# ============================================================================


def validate_project_structure(
    repo_path: Path, projects: List[Dict]
) -> Dict[str, Dict[str, Union[bool, str, None]]]:
    """
    Validate detected projects have parseable files and valid versions.

    Args:
        repo_path: Path to repository directory
        projects: List of detected projects

    Returns:
        Validation results per project type:
        {
            "rust": {"ok": True, "version": "1.2.3"},
            "javascript": {"ok": False, "reason": "malformed_json"}
        }
    """
    repo_path = Path(repo_path).resolve()
    validation = {}

    for project in projects:
        project_type = project["type"]
        version_file = project.get("version_file")
        version = project.get("version")

        if project_type == "unknown":
            validation[project_type] = {"ok": False, "reason": "no_detectable_project"}
            continue

        if not version_file:
            validation[project_type] = {"ok": False, "reason": "no_version_file"}
            continue

        file_path = repo_path / version_file
        if not file_path.exists():
            validation[project_type] = {"ok": False, "reason": "version_file_missing"}
            continue

        if not version:
            validation[project_type] = {"ok": False, "reason": "version_not_found"}
            continue

        if not validate_semver_format(version):
            validation[project_type] = {"ok": False, "reason": "invalid_semver_format"}
            continue

        validation[project_type] = {"ok": True, "version": version}

    return validation


# ============================================================================
# Standard Tools and Script Detection
# ============================================================================


def detect_standard_bin_tools(repo_path: Path) -> Dict[str, Dict[str, Union[bool, str]]]:
    """
    Detect standard bin tools for infrastructure gap analysis.

    Standard tools that MUST be in ./bin/ directory:
    - build.sh: Build automation
    - deploy.sh: Deployment automation
    - test.sh: Testing automation
    - snap.sh: Benchmarking automation

    Args:
        repo_path: Path to repository directory

    Returns:
        Dictionary of tool status:
        {
            "build.sh": {"exists": True, "path": "./bin/build.sh"},
            "deploy.sh": {"exists": False},
            "test.sh": {"exists": True, "path": "./bin/test.sh"},
            "snap.sh": {"exists": False}
        }
    """
    repo_path = Path(repo_path).resolve()
    standard_tools = ["build.sh", "deploy.sh", "test.sh", "snap.sh"]
    tools = {}

    for tool in standard_tools:
        # Standard tools MUST be in ./bin/ directory
        bin_path = repo_path / "bin" / tool
        if bin_path.exists():
            tools[tool] = {"exists": True, "path": f"./bin/{tool}"}
        else:
            tools[tool] = {"exists": False}

    return tools


def detect_emerging_tools(repo_path: Path) -> Dict[str, Union[bool, List[str]]]:
    """
    Detect emerging development tools and patterns.

    Current emerging patterns:
    - Makefile/makefile: Build system detection
    - Python scripts in ./bin/: Automation scripts

    Args:
        repo_path: Path to repository directory

    Returns:
        Dictionary of emerging tool detection results
    """
    repo_path = Path(repo_path).resolve()
    emerging = {}

    # Check for Makefile
    makefile_exists = (repo_path / "Makefile").exists() or (repo_path / "makefile").exists()
    if makefile_exists:
        makefile_path = "Makefile" if (repo_path / "Makefile").exists() else "makefile"
        emerging["makefile"] = {"exists": True, "path": f"./{makefile_path}"}
    else:
        emerging["makefile"] = {"exists": False}

    # Check for Python scripts in bin directory
    bin_dir = repo_path / "bin"
    python_scripts = []
    if bin_dir.exists():
        for script in bin_dir.glob("*.py"):
            python_scripts.append(f"./bin/{script.name}")

    emerging["python_scripts"] = python_scripts

    return emerging


def detect_script_metadata(repo_path: Path) -> Dict[str, Union[str, List[str], None]]:
    """
    Detect general script directories and files for discovery metadata.

    Finds:
    - bin/ directory existence
    - Root-level .sh scripts (excluding standard tools)
    - Script directories (./scripts, ./tools)

    Args:
        repo_path: Path to repository directory

    Returns:
        Dictionary of script metadata:
        {
            "bin_directory": "./bin" or None,
            "root_scripts": ["./custom-tool.sh", "./migrate.sh"],
            "script_directories": ["./scripts", "./tools"]
        }
    """
    repo_path = Path(repo_path).resolve()

    # Check for bin directory
    bin_directory = "./bin" if (repo_path / "bin").exists() else None

    # Find root-level .sh scripts (excluding standard tools)
    standard_tools = {"build.sh", "deploy.sh", "test.sh", "snap.sh"}
    root_scripts = []

    for script in repo_path.glob("*.sh"):
        if script.name not in standard_tools and not is_generated_file(script):
            root_scripts.append(f"./{script.name}")

    # Find script directories
    script_dir_names = ["scripts", "tools", "bin"]
    script_directories = []

    for item in repo_path.iterdir():
        if (
            item.is_dir() and item.name in script_dir_names and item.name != "bin"
        ):  # bin handled separately
            script_directories.append(f"./{item.name}")

    return {
        "bin_directory": bin_directory,
        "root_scripts": root_scripts,
        "script_directories": script_directories,
    }


def detect_dirty_directories(repo_path: Path) -> List[str]:
    """
    Find gitignore-type directories that could be cleaned up.

    Common build artifacts and dependency directories:
    - node_modules, target, .venv, build, dist, etc.

    Args:
        repo_path: Path to repository directory

    Returns:
        List of dirty directory paths found
    """
    repo_path = Path(repo_path).resolve()

    dirty_patterns = [
        "node_modules",
        "target",
        ".venv",
        "venv",
        "__pycache__",
        "build",
        "dist",
        ".tox",
        ".pytest_cache",
        ".coverage",
        ".nyc_output",
        "coverage",
        ".next",
        ".nuxt",
    ]

    found_dirty = []
    for pattern in dirty_patterns:
        dir_path = repo_path / pattern
        if dir_path.exists() and dir_path.is_dir():
            found_dirty.append(f"./{pattern}")

    return found_dirty


# ============================================================================
# Primary Detection API
# ============================================================================


def get_repository_context(repo_path: Path) -> Dict:
    """
    Single entry point returning complete repository analysis.

    This is the primary interface for both SEMV and Blade integration.

    Args:
        repo_path: Path to repository directory

    Returns:
        Complete repository context dictionary with all detection results
    """
    repo_path = Path(repo_path).resolve()

    # Core detection
    repo_type = detect_repository_type(repo_path)
    projects = detect_projects(repo_path)
    gitsim_status = validate_gitsim_environment(repo_path)
    validation = validate_project_structure(repo_path, projects)

    # Tooling detection
    standard_bin_tools = detect_standard_bin_tools(repo_path)
    emerging_tools = detect_emerging_tools(repo_path)
    script_metadata = detect_script_metadata(repo_path)
    dirty_directories = detect_dirty_directories(repo_path)

    # Repository metadata (would extract from actual git/gitsim commands)
    repository_info = {
        "path": str(repo_path),
        "root": str(repo_path),  # Add missing 'root' field
        "type": repo_type,
        "branch": "main",  # Would extract from git/gitsim
        "is_clean": True,  # Would check git status
        "last_commit": None,  # Would extract from git log
    }

    # Basic workspace detection (placeholder for future enhancement)
    workspace_info = {"is_workspace": False, "type": None, "members": []}

    # Detection metadata
    meta_info = {
        "detector_version": "1.0.0",
        "detection_time": "2025-09-23T10:30:00Z",  # Would use actual timestamp
        "detection_duration_ms": 50,  # Would measure actual time
    }

    return {
        "repository": repository_info,
        "projects": projects,
        "tools": {"standard_bin": standard_bin_tools, "emerging": emerging_tools},
        "scripts": script_metadata,
        "dirty_directories": dirty_directories,
        "workspace": workspace_info,
        "validation": validation,
        "gitsim": gitsim_status,
        "meta": meta_info,
    }


# ============================================================================
# Convenience Functions
# ============================================================================


def get_project_types(repo_path: Path) -> List[str]:
    """
    Get list of detected project types (for backward compatibility).

    Args:
        repo_path: Path to repository directory

    Returns:
        List of project type strings: ["rust", "javascript", "python", "bash", "unknown"]
    """
    projects = detect_projects(repo_path)
    return [project["type"] for project in projects]


def get_version_files_map(repo_path: Path) -> Dict[str, str]:
    """
    Get mapping of project types to version files (for backward compatibility).

    Args:
        repo_path: Path to repository directory

    Returns:
        Dictionary mapping project types to version file paths:
        {"rust": "Cargo.toml", "javascript": "package.json"}
    """
    projects = detect_projects(repo_path)
    version_files = {}

    for project in projects:
        project_type = project["type"]
        version_file = project.get("version_file")
        if version_file:
            version_files[project_type] = version_file

    return version_files


def get_all_versions(repo_path: Path) -> Dict[str, str]:
    """
    Get all detected versions for highest-wins comparison.

    Args:
        repo_path: Path to repository directory

    Returns:
        Dictionary mapping project types to versions:
        {"rust": "1.2.3", "javascript": "1.2.1"}
    """
    projects = detect_projects(repo_path)
    versions = {}

    for project in projects:
        project_type = project["type"]
        version = project.get("version")
        if version:
            versions[project_type] = version

    return versions
