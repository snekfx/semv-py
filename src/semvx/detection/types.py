"""
Type definitions for the detection module.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Union


@dataclass
class ProjectInfo:
    """Information about a detected project."""
    type: str  # "rust", "javascript", "python", "bash", "unknown"
    root: str  # Relative path from repo root
    version_file: Optional[str]  # Relative path to version file
    version: Optional[str]  # Extracted version string
    pattern: Optional[str] = None  # For bash projects: pattern type


@dataclass
class RepositoryContext:
    """Complete repository analysis context."""
    repository: Dict[str, Union[str, bool, None]]
    projects: List[ProjectInfo]
    tools: Dict[str, Dict[str, Union[bool, str, List[str]]]]
    scripts: Dict[str, Union[str, List[str], None]]
    dirty_directories: List[str]
    workspace: Dict[str, Union[bool, str, List[str], None]]
    validation: Dict[str, Dict[str, Union[bool, str, None]]]
    gitsim: Dict[str, Union[bool, str, Dict, None]]
    meta: Dict[str, Union[str, int]]


@dataclass
class ValidationResult:
    """Result of project validation."""
    ok: bool
    reason: Optional[str] = None
    version: Optional[str] = None
