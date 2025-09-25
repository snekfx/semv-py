"""
SemVer utilities for version normalization, comparison, and analysis.
"""

import re
from typing import List, Optional


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

    Examples:
        >>> normalize_semver("1.2.3")
        "v1.2.3"
        >>> normalize_semver("v1.2.3-alpha.1")
        "v1.2.3"
        >>> normalize_semver("1.2")
        "v1.2.0"
    """
    if not version:
        return "v0.0.0"

    # Remove any whitespace
    version = version.strip()

    # Add 'v' prefix if missing
    if not version.startswith('v'):
        version = f"v{version}"

    # Extract base version (remove pre-release and build metadata)
    # Pattern: vX.Y.Z[-pre-release][+build]
    base_match = re.match(r'v?(\d+)\.(\d+)\.?(\d*)', version)
    if not base_match:
        return "v0.0.0"

    major, minor, patch = base_match.groups()
    patch = patch or "0"  # Default patch to 0 if missing

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

    Examples:
        >>> compare_semver("v1.2.3", "v1.2.4")
        -1
        >>> compare_semver("v2.0.0", "v1.9.9")
        1
        >>> compare_semver("v1.2.3", "v1.2.3")
        0
    """
    # Normalize both versions
    v1_norm = normalize_semver(version1)
    v2_norm = normalize_semver(version2)

    # Extract version components
    v1_match = re.match(r'v(\d+)\.(\d+)\.(\d+)', v1_norm)
    v2_match = re.match(r'v(\d+)\.(\d+)\.(\d+)', v2_norm)

    if not v1_match or not v2_match:
        # Fallback to string comparison if parsing fails
        return -1 if v1_norm < v2_norm else (1 if v1_norm > v2_norm else 0)

    v1_parts = [int(x) for x in v1_match.groups()]
    v2_parts = [int(x) for x in v2_match.groups()]

    # Compare major, minor, patch in order
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

    Examples:
        >>> validate_semver_format("1.2.3")
        True
        >>> validate_semver_format("v1.2.3-alpha.1")
        True
        >>> validate_semver_format("1.2")
        False
        >>> validate_semver_format("invalid")
        False
    """
    if not version:
        return False

    # Allow optional 'v' prefix, require X.Y.Z core, allow pre-release and build
    pattern = r'^v?(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z\-\.]+))?(?:\+([0-9A-Za-z\-\.]+))?$'
    return bool(re.match(pattern, version.strip()))


def get_highest_version(versions: List[str]) -> Optional[str]:
    """
    Find the highest version from a list using semver comparison.

    Implements "highest version wins" logic for version synchronization.

    Args:
        versions: List of version strings to compare

    Returns:
        Highest version string, or None if list is empty

    Examples:
        >>> get_highest_version(["v1.2.3", "v1.2.4", "v1.1.0"])
        "v1.2.4"
        >>> get_highest_version([])
        None
    """
    if not versions:
        return None

    valid_versions = [v for v in versions if validate_semver_format(v)]
    if not valid_versions:
        return None

    highest = valid_versions[0]
    for version in valid_versions[1:]:
        if compare_semver(version, highest) > 0:
            highest = version

    return normalize_semver(highest)