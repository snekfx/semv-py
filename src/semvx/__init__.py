"""
SEMVX - Semantic Version Manager (Python Edition)
Version: 3.0.0-dev

A modular, performant Python implementation of the SEMV semantic versioning tool.
Provides intelligent version detection, management, and synchronization across
multi-language projects with Git and GitSim integration.
"""

__version__ = "3.0.0-dev"
__author__ = "SEMV Development Team"
__email__ = "dev@semv.tools"

# Core imports
try:
    from semvx.core import SemanticVersion, VersionParseError
    __all__ = ["SemanticVersion", "VersionParseError", "__version__"]
except ImportError:
    # Fallback if core module not available
    __all__ = ["__version__"]