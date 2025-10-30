"""
Shared Project Detection Library - Core Module
Version: 1.0.0
Last Updated: 2025-10-30
Compatible: SEMV v3.0+, Blade Next v1.0+
Distribution: Copy into target projects (no dependency)

Zero dependencies - pure Python standard library only.

Note: Refactored into focused submodules:
- foundations.py: Core utilities (semver, gitsim)
- manifests.py: Language-specific detection/extraction
- reporting.py: Repository metadata and tooling
- detector.py: Orchestration and primary API
"""

from pathlib import Path
from typing import Dict, List, Union

# Import foundation functions
from .foundations import detect_repository_type, validate_gitsim_environment

# Import manifest detection and extraction
from .manifests import (
    detect_bash_patterns,
    extract_bash_version,
    extract_javascript_version,
    extract_python_version,
    extract_rust_version,
    get_bash_project_file,
    has_javascript_manifest,
    has_python_manifest,
    has_rust_manifest,
)

# Import reporting and validation
from .reporting import (
    detect_dirty_directories,
    detect_emerging_tools,
    detect_script_metadata,
    detect_standard_bin_tools,
    validate_project_structure,
)


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
