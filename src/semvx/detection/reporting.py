"""
Reporting Module - Repository metadata and tooling detection.
Part of the shared detection library.

This module handles:
- Project structure validation
- Standard tooling detection (build.sh, deploy.sh, etc.)
- Emerging patterns detection
- Script and directory discovery
- Build artifact detection

Zero dependencies - pure Python standard library only.
"""

from pathlib import Path
from typing import Dict, List, Union

from .foundations import validate_semver_format
from .manifests import is_generated_file

# ============================================================================
# Project Validation
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
    validation: Dict[str, Dict[str, Union[bool, str, None]]] = {}

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
    tools: Dict[str, Dict[str, Union[bool, str]]] = {}

    for tool in standard_tools:
        # Standard tools MUST be in ./bin/ directory
        bin_path = repo_path / "bin" / tool
        if bin_path.exists():
            tools[tool] = {"exists": True, "path": f"./bin/{tool}"}
        else:
            tools[tool] = {"exists": False}

    return tools


def detect_emerging_tools(
    repo_path: Path,
) -> Dict[str, Union[bool, List[str], Dict[str, Union[bool, str]]]]:
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
    emerging: Dict[str, Union[bool, List[str], Dict[str, Union[bool, str]]]] = {}

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
