"""
Detection Module - Shared project detection library for SEMV and Blade integration.

This module provides consistent project type detection across multiple programming
languages with zero external dependencies. It's designed to be copied and used
independently by both SEMV and Blade tools.

Distribution Model: Source code copying (not package dependency)
Compatible with: SEMV v3.0+, Blade Next v1.0+
"""

from .detector import ProjectDetector
from .types import ProjectInfo, RepositoryContext
from .version import normalize_semver, compare_semver, get_highest_version

__all__ = [
    "ProjectDetector",
    "ProjectInfo",
    "RepositoryContext",
    "normalize_semver",
    "compare_semver",
    "get_highest_version"
]