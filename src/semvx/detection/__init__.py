"""
Detection Module - Shared project detection library for SEMV and Blade integration.

This module provides consistent project type detection across multiple programming
languages with zero external dependencies. It's designed to be copied and used
independently by both SEMV and Blade tools.

Distribution Model: Source code copying (not package dependency)
Compatible with: SEMV v3.0+, Blade Next v1.0+
"""

# Import what actually exists in the detector module
from .detector import compare_semver, get_highest_version, get_repository_context, normalize_semver

__all__ = ["get_repository_context", "normalize_semver", "compare_semver", "get_highest_version"]
