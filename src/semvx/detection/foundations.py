"""
Detection Foundations - SemVer utilities and repository environment detection.

Part of the Shared Project Detection Library.
Zero dependencies - pure Python standard library only.
"""

from pathlib import Path
from typing import List, Dict, Union
import re
import shutil


# ============================================================================
# SemVer Utilities
# ============================================================================

def normalize_semver(version: str) -> str:
    """
    Normalize version to vX.Y.Z format for consistent comparison.
    
    Handles:
    - Optional 'v' prefix: "1.2.3" -> "v1.2.3"
    - Pre-release cleanup: "v1.2.3-alpha.1+meta" -> "v1.2.3"
    - Malformed versions: "1.2" -> "v1.2.0"
    
    Args:
        version: Raw version string from various sources
        
    Returns:
        Normalized version string in vX.Y.Z format
    """
    if not version:
        return "v0.0.0"
    
    # Remove any whitespace
    version = version.strip()
    
    # Add 'v' prefix if missing
    if not version.startswith('v'):
        version = f"v{version}"
    
    # Extract base version (remove pre-release and build metadata)
    base_match = re.match(r'v?(\d+)\.(\d+)\.?(\d*)', version)
    if not base_match:
        return "v0.0.0"
    
    major, minor, patch = base_match.groups()
    patch = patch or "0"
    
    return f"v{major}.{minor}.{patch}"


def compare_semver(version1: str, version2: str) -> int:
    """
    Compare semantic versions using standard semver precedence.
    
    Args:
        version1: First version to compare
        version2: Second version to compare
        
    Returns:
        -1 if version1 < version2
         0 if version1 == version2
         1 if version1 > version2
    """
    v1_norm = normalize_semver(version1)
    v2_norm = normalize_semver(version2)
    
    v1_match = re.match(r'v(\d+)\.(\d+)\.(\d+)', v1_norm)
    v2_match = re.match(r'v(\d+)\.(\d+)\.(\d+)', v2_norm)
    
    if not v1_match or not v2_match:
        return -1 if v1_norm < v2_norm else (1 if v1_norm > v2_norm else 0)
    
    v1_parts = [int(x) for x in v1_match.groups()]
    v2_parts = [int(x) for x in v2_match.groups()]
    
    for v1_part, v2_part in zip(v1_parts, v2_parts):
        if v1_part < v2_part:
            return -1
        elif v1_part > v2_part:
            return 1
    
    return 0


def validate_semver_format(version: str) -> bool:
    """
    Validate if a version string follows semantic versioning format.
    
    Args:
        version: Version string to validate
        
    Returns:
        True if valid semver format, False otherwise
    """
    if not version:
        return False
    
    pattern = r'^v?(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z\-\.]+))?(?:\+([0-9A-Za-z\-\.]+))?$'
    return bool(re.match(pattern, version.strip()))


def get_highest_version(versions: List[str]) -> str:
    """
    Find the highest version from a list using semver comparison.
    
    Args:
        versions: List of version strings to compare
        
    Returns:
        Highest version string, or "v0.0.0" if list is empty
    """
    if not versions:
        return "v0.0.0"
    
    valid_versions = [v for v in versions if validate_semver_format(v)]
    if not valid_versions:
        return "v0.0.0"
    
    highest = valid_versions[0]
    for version in valid_versions[1:]:
        if compare_semver(version, highest) > 0:
            highest = version
    
    return normalize_semver(highest)


# ============================================================================
# Repository Environment Detection
# ============================================================================

def detect_repository_type(repo_path: Path) -> str:
    """
    Determine repository environment type.
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        "gitsim" if .gitsim directory exists
        "git" if .git directory exists
        "directory" if neither exists
    """
    repo_path = Path(repo_path).resolve()
    
    if (repo_path / ".gitsim").exists():
        return "gitsim"
    
    if (repo_path / ".git").exists():
        return "git"
    
    return "directory"


def check_gitsim_availability() -> bool:
    """
    Check if gitsim command is available in PATH.
    
    Returns:
        True if gitsim command is available, False otherwise
    """
    return shutil.which("gitsim") is not None


def validate_gitsim_environment(repo_path: Path) -> Dict[str, Union[bool, str, None]]:
    """
    Complete GitSim environment validation and metadata extraction.
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        Dictionary with GitSim status and metadata
    """
    repo_path = Path(repo_path).resolve()
    is_gitsim = (repo_path / ".gitsim").exists()
    gitsim_available = check_gitsim_availability()
    
    result = {
        "is_gitsim": is_gitsim,
        "gitsim_available": gitsim_available,
        "status": "not_gitsim",
        "simulation_info": None
    }
    
    if not is_gitsim:
        return result
    
    if not gitsim_available:
        result["status"] = "gitsim_unavailable"
        return result
    
    try:
        result["status"] = "gitsim_active"
        result["simulation_info"] = {
            "simulation_active": True,
            "base_branch": "main",
            "simulated_commits": 0,
            "config_file": str(repo_path / ".gitsim" / "config")
        }
    except Exception:
        result["status"] = "gitsim_error"
    
    return result
