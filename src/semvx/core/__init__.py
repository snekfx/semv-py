"""
Core module for SEMVX - Version management functionality.

Provides semantic version parsing, comparison, bump operations, file writing,
git repository operations, build information tracking, and comprehensive
repository status analysis.
"""

from .build_info import BuildInfo
from .commit_analyzer import BumpType, CommitAnalysis, CommitAnalyzer
from .file_writer import FileWriteError, VersionFileWriter
from .git_ops import GitError, GitRepository, GitVersionTagger
from .repository_status import RepositoryAnalyzer, RepositoryStatus
from .version import (
    SemanticVersion,
    SemanticVersionFormatter,
    SemanticVersionParser,
    VersionParseError,
)

__all__ = [
    "BuildInfo",
    "BumpType",
    "CommitAnalysis",
    "CommitAnalyzer",
    "FileWriteError",
    "GitError",
    "GitRepository",
    "GitVersionTagger",
    "RepositoryAnalyzer",
    "RepositoryStatus",
    "SemanticVersion",
    "SemanticVersionFormatter",
    "SemanticVersionParser",
    "VersionFileWriter",
    "VersionParseError",
]
