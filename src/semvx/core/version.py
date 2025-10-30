"""
Core version management module for SEMVX.

Provides immutable SemanticVersion class with parsing, formatting, and bump operations.
Follows semantic versioning specification (https://semver.org/).
"""

import re
from dataclasses import dataclass
from functools import total_ordering
from typing import Optional


class VersionParseError(Exception):
    """Raised when version string cannot be parsed as semantic version."""

    pass


@dataclass(frozen=True)
@total_ordering
class SemanticVersion:
    """
    Immutable semantic version representation.

    Supports major.minor.patch with optional pre-release and build metadata.
    Implements comparison operators for version ordering.

    Examples:
        >>> v1 = SemanticVersion.parse("1.2.3")
        >>> v2 = SemanticVersion.parse("1.2.4-alpha.1+build.123")
        >>> v1 < v2
        True
        >>> v1.bump_major()
        SemanticVersion(major=2, minor=0, patch=0, prerelease=None, build_metadata=None)
    """

    major: int
    minor: int
    patch: int
    prerelease: Optional[str] = None
    build_metadata: Optional[str] = None

    @classmethod
    def parse(cls, version_string: str) -> "SemanticVersion":
        """
        Parse a version string into SemanticVersion.

        Args:
            version_string: Version string to parse (e.g., "1.2.3-alpha+build")

        Returns:
            SemanticVersion instance

        Raises:
            VersionParseError: If version string is invalid
        """
        if not version_string:
            raise VersionParseError("Version string cannot be empty")

        # Remove optional 'v' prefix
        version = version_string.strip()
        if version.startswith("v"):
            version = version[1:]

        # Semantic version regex pattern
        # Captures: major.minor.patch[-prerelease][+build]
        pattern = r"^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z\-\.]+))?(?:\+([0-9A-Za-z\-\.]+))?$"
        match = re.match(pattern, version)

        if not match:
            raise VersionParseError(f"Invalid semantic version format: {version_string}")

        major, minor, patch, prerelease, build_metadata = match.groups()

        return cls(
            major=int(major),
            minor=int(minor),
            patch=int(patch),
            prerelease=prerelease,
            build_metadata=build_metadata,
        )

    def bump_major(self) -> "SemanticVersion":
        """
        Return new version with major increment.
        Minor and patch are reset to 0, pre-release and build metadata cleared.
        """
        return SemanticVersion(
            major=self.major + 1, minor=0, patch=0, prerelease=None, build_metadata=None
        )

    def bump_minor(self) -> "SemanticVersion":
        """
        Return new version with minor increment.
        Patch is reset to 0, pre-release and build metadata cleared.
        """
        return SemanticVersion(
            major=self.major, minor=self.minor + 1, patch=0, prerelease=None, build_metadata=None
        )

    def bump_patch(self) -> "SemanticVersion":
        """
        Return new version with patch increment.
        Pre-release and build metadata cleared.
        """
        return SemanticVersion(
            major=self.major,
            minor=self.minor,
            patch=self.patch + 1,
            prerelease=None,
            build_metadata=None,
        )

    def with_prerelease(self, prerelease: str) -> "SemanticVersion":
        """Return new version with specified pre-release."""
        return SemanticVersion(
            major=self.major,
            minor=self.minor,
            patch=self.patch,
            prerelease=prerelease,
            build_metadata=self.build_metadata,
        )

    def with_build_metadata(self, build_metadata: str) -> "SemanticVersion":
        """Return new version with specified build metadata."""
        return SemanticVersion(
            major=self.major,
            minor=self.minor,
            patch=self.patch,
            prerelease=self.prerelease,
            build_metadata=build_metadata,
        )

    def __str__(self) -> str:
        """Format as semantic version string."""
        version = f"{self.major}.{self.minor}.{self.patch}"

        if self.prerelease:
            version += f"-{self.prerelease}"

        if self.build_metadata:
            version += f"+{self.build_metadata}"

        return version

    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (
            f"SemanticVersion(major={self.major}, minor={self.minor}, "
            f"patch={self.patch}, prerelease={self.prerelease!r}, "
            f"build_metadata={self.build_metadata!r})"
        )

    def __eq__(self, other) -> bool:
        """Check equality (build metadata ignored per semver spec)."""
        if not isinstance(other, SemanticVersion):
            return NotImplemented

        return (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
            and self.prerelease == other.prerelease
        )

    def __lt__(self, other) -> bool:
        """Compare versions (build metadata ignored per semver spec)."""
        if not isinstance(other, SemanticVersion):
            return NotImplemented

        # Compare major.minor.patch
        core_comparison = (self.major, self.minor, self.patch)
        other_core = (other.major, other.minor, other.patch)

        if core_comparison != other_core:
            return core_comparison < other_core

        # If core versions are equal, compare pre-release
        # No pre-release > pre-release
        if self.prerelease is None and other.prerelease is not None:
            return False
        if self.prerelease is not None and other.prerelease is None:
            return True
        if self.prerelease is None and other.prerelease is None:
            return False

        # Both have pre-release, compare lexically
        # mypy needs help understanding both are non-None at this point
        assert self.prerelease is not None and other.prerelease is not None
        return self.prerelease < other.prerelease


class SemanticVersionFormatter:
    """Composition helper for custom version formatting."""

    @staticmethod
    def with_v_prefix(version: SemanticVersion) -> str:
        """Format version with 'v' prefix."""
        return f"v{version}"

    @staticmethod
    def short_format(version: SemanticVersion) -> str:
        """Format version without pre-release and build metadata."""
        return f"{version.major}.{version.minor}.{version.patch}"


class SemanticVersionParser:
    """Composition helper for extensible version parsing."""

    @staticmethod
    def parse_strict(version_string: str) -> SemanticVersion:
        """Parse version with strict validation."""
        return SemanticVersion.parse(version_string)

    @staticmethod
    def parse_loose(version_string: str) -> Optional[SemanticVersion]:
        """Parse version, returning None on failure instead of raising."""
        try:
            return SemanticVersion.parse(version_string)
        except VersionParseError:
            return None
