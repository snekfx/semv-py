"""
Unit tests for SemanticVersion class and related functionality.
"""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from semvx.core.version import (
    SemanticVersion,
    VersionParseError,
    SemanticVersionFormatter,
    SemanticVersionParser
)


class TestSemanticVersionParsing:
    """Test semantic version parsing."""

    def test_parse_basic_version(self):
        """Test parsing basic major.minor.patch versions."""
        version = SemanticVersion.parse("1.2.3")
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3
        assert version.prerelease is None
        assert version.build_metadata is None

    def test_parse_with_v_prefix(self):
        """Test parsing versions with 'v' prefix."""
        version = SemanticVersion.parse("v1.2.3")
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3

    def test_parse_with_prerelease(self):
        """Test parsing versions with pre-release."""
        version = SemanticVersion.parse("1.2.3-alpha.1")
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3
        assert version.prerelease == "alpha.1"
        assert version.build_metadata is None

    def test_parse_with_build_metadata(self):
        """Test parsing versions with build metadata."""
        version = SemanticVersion.parse("1.2.3+build.123")
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3
        assert version.prerelease is None
        assert version.build_metadata == "build.123"

    def test_parse_full_version(self):
        """Test parsing complete version with pre-release and build."""
        version = SemanticVersion.parse("1.2.3-beta.2+build.456")
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3
        assert version.prerelease == "beta.2"
        assert version.build_metadata == "build.456"

    def test_parse_invalid_versions(self):
        """Test that invalid versions raise VersionParseError."""
        invalid_versions = [
            "",
            "1.2",
            "1.2.3.4",
            "v1.2.x",
            "1.2.3-",
            "1.2.3+",
            "invalid"
        ]

        for invalid_version in invalid_versions:
            with pytest.raises(VersionParseError):
                SemanticVersion.parse(invalid_version)


class TestSemanticVersionComparison:
    """Test semantic version comparison and ordering."""

    def test_version_equality(self):
        """Test version equality (ignoring build metadata)."""
        v1 = SemanticVersion.parse("1.2.3")
        v2 = SemanticVersion.parse("1.2.3")
        v3 = SemanticVersion.parse("1.2.3+build")
        v4 = SemanticVersion.parse("1.2.3+different")

        assert v1 == v2
        assert v1 == v3  # Build metadata ignored
        assert v3 == v4  # Build metadata ignored

    def test_version_ordering(self):
        """Test version ordering."""
        versions = [
            SemanticVersion.parse("1.0.0"),
            SemanticVersion.parse("1.0.1"),
            SemanticVersion.parse("1.1.0"),
            SemanticVersion.parse("2.0.0")
        ]

        # Test ascending order
        for i in range(len(versions) - 1):
            assert versions[i] < versions[i + 1]

        # Test descending order
        for i in range(len(versions) - 1, 0, -1):
            assert versions[i] > versions[i - 1]

    def test_prerelease_ordering(self):
        """Test pre-release version ordering."""
        v_release = SemanticVersion.parse("1.0.0")
        v_prerelease = SemanticVersion.parse("1.0.0-alpha")

        # Pre-release versions have lower precedence
        assert v_prerelease < v_release

        # Pre-release ordering
        v_alpha = SemanticVersion.parse("1.0.0-alpha")
        v_beta = SemanticVersion.parse("1.0.0-beta")
        assert v_alpha < v_beta


class TestSemanticVersionBumping:
    """Test version bump operations."""

    def test_bump_major(self):
        """Test major version bump."""
        version = SemanticVersion.parse("1.2.3-alpha+build")
        bumped = version.bump_major()

        assert bumped.major == 2
        assert bumped.minor == 0
        assert bumped.patch == 0
        assert bumped.prerelease is None
        assert bumped.build_metadata is None

    def test_bump_minor(self):
        """Test minor version bump."""
        version = SemanticVersion.parse("1.2.3-alpha+build")
        bumped = version.bump_minor()

        assert bumped.major == 1
        assert bumped.minor == 3
        assert bumped.patch == 0
        assert bumped.prerelease is None
        assert bumped.build_metadata is None

    def test_bump_patch(self):
        """Test patch version bump."""
        version = SemanticVersion.parse("1.2.3-alpha+build")
        bumped = version.bump_patch()

        assert bumped.major == 1
        assert bumped.minor == 2
        assert bumped.patch == 4
        assert bumped.prerelease is None
        assert bumped.build_metadata is None

    def test_immutability(self):
        """Test that original version is unchanged after bump."""
        original = SemanticVersion.parse("1.2.3")
        bumped = original.bump_major()

        assert original.major == 1  # Original unchanged
        assert bumped.major == 2    # New instance


class TestSemanticVersionFormatting:
    """Test version string formatting."""

    def test_basic_string_formatting(self):
        """Test basic version string formatting."""
        version = SemanticVersion.parse("1.2.3")
        assert str(version) == "1.2.3"

    def test_full_string_formatting(self):
        """Test complete version string formatting."""
        version = SemanticVersion.parse("1.2.3-alpha.1+build.123")
        assert str(version) == "1.2.3-alpha.1+build.123"

    def test_formatter_helpers(self):
        """Test SemanticVersionFormatter helpers."""
        version = SemanticVersion.parse("1.2.3-alpha+build")

        # Test v-prefix formatter
        assert SemanticVersionFormatter.with_v_prefix(version) == "v1.2.3-alpha+build"

        # Test short format
        assert SemanticVersionFormatter.short_format(version) == "1.2.3"


class TestSemanticVersionParser:
    """Test SemanticVersionParser helpers."""

    def test_strict_parser(self):
        """Test strict parsing."""
        version = SemanticVersionParser.parse_strict("1.2.3")
        assert version.major == 1

        with pytest.raises(VersionParseError):
            SemanticVersionParser.parse_strict("invalid")

    def test_loose_parser(self):
        """Test loose parsing."""
        version = SemanticVersionParser.parse_loose("1.2.3")
        assert version is not None
        assert version.major == 1

        # Should return None instead of raising
        result = SemanticVersionParser.parse_loose("invalid")
        assert result is None


class TestSemanticVersionModifiers:
    """Test version modifier methods."""

    def test_with_prerelease(self):
        """Test adding pre-release."""
        version = SemanticVersion.parse("1.2.3")
        modified = version.with_prerelease("alpha.1")

        assert modified.major == 1
        assert modified.minor == 2
        assert modified.patch == 3
        assert modified.prerelease == "alpha.1"

    def test_with_build_metadata(self):
        """Test adding build metadata."""
        version = SemanticVersion.parse("1.2.3")
        modified = version.with_build_metadata("build.123")

        assert modified.major == 1
        assert modified.minor == 2
        assert modified.patch == 3
        assert modified.build_metadata == "build.123"