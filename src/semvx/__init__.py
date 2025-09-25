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

from semvx.core.version import SemanticVersion
from semvx.detection.detector import ProjectDetector

__all__ = ["SemanticVersion", "ProjectDetector", "__version__"]