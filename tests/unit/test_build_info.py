"""Tests for build_info module."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from semvx.core.build_info import BuildInfo
from semvx.core.git_ops import GitError


class TestBuildInfo:
    """Tests for BuildInfo class."""

    def test_get_build_count_all_commits(self, tmp_path):
        """Test getting total build count."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="42\n", stderr="", returncode=0
            )

            count = BuildInfo.get_build_count(tmp_path)

            assert count == 42
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert args == ["git", "rev-list", "--count", "HEAD"]

    def test_get_build_count_since_tag(self, tmp_path):
        """Test getting build count since specific tag."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="15\n", stderr="", returncode=0
            )

            count = BuildInfo.get_build_count(tmp_path, since_tag="v0.0.1")

            assert count == 15
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert args == ["git", "rev-list", "--count", "v0.0.1..HEAD"]

    def test_get_build_count_zero(self, tmp_path):
        """Test build count of zero."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="0\n", stderr="", returncode=0
            )

            count = BuildInfo.get_build_count(tmp_path)

            assert count == 0

    def test_get_build_count_git_error(self, tmp_path):
        """Test build count with git error."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                1, "git", stderr="fatal: not a git repository"
            )

            with pytest.raises(GitError, match="Failed to get build count"):
                BuildInfo.get_build_count(tmp_path)

    def test_get_build_count_invalid_output(self, tmp_path):
        """Test build count with invalid output."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="not-a-number\n", stderr="", returncode=0
            )

            with pytest.raises(GitError, match="Invalid build count output"):
                BuildInfo.get_build_count(tmp_path)

    def test_get_commit_hash_short(self, tmp_path):
        """Test getting short commit hash."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="abc1234\n", stderr="", returncode=0
            )

            hash_val = BuildInfo.get_commit_hash(tmp_path, short=True)

            assert hash_val == "abc1234"
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert args == ["git", "rev-parse", "--short", "HEAD"]

    def test_get_commit_hash_full(self, tmp_path):
        """Test getting full commit hash."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="abc1234567890def1234567890abcdef12345678\n",
                stderr="",
                returncode=0,
            )

            hash_val = BuildInfo.get_commit_hash(tmp_path, short=False)

            assert hash_val == "abc1234567890def1234567890abcdef12345678"
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert args == ["git", "rev-parse", "HEAD"]

    def test_get_commit_hash_git_error(self, tmp_path):
        """Test commit hash with git error."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                1, "git", stderr="fatal: not a git repository"
            )

            with pytest.raises(GitError, match="Failed to get commit hash"):
                BuildInfo.get_commit_hash(tmp_path)


    def test_generate_build_file(self, tmp_path):
        """Test generating build info file."""
        with patch("subprocess.run") as mock_run:
            # Mock build count
            mock_run.side_effect = [
                MagicMock(stdout="42\n", stderr="", returncode=0),  # build count
                MagicMock(
                    stdout="abc1234567890def1234567890abcdef12345678\n",
                    stderr="",
                    returncode=0,
                ),  # full hash
                MagicMock(
                    stdout="abc1234\n", stderr="", returncode=0
                ),  # short hash
            ]

            output_file = BuildInfo.generate_build_file(
                tmp_path, version="1.2.3"
            )

            assert output_file.exists()
            assert output_file.name == ".build_info"

            content = output_file.read_text()
            assert "VERSION=1.2.3" in content
            assert "BUILD_COUNT=42" in content
            assert "COMMIT_HASH=abc1234567890def1234567890abcdef12345678" in content
            assert "COMMIT_HASH_SHORT=abc1234" in content
            assert "BUILD_TIMESTAMP=" in content

    def test_generate_build_file_custom_name(self, tmp_path):
        """Test generating build info file with custom name."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                MagicMock(stdout="10\n", stderr="", returncode=0),
                MagicMock(stdout="def5678\n", stderr="", returncode=0),
                MagicMock(stdout="def5678\n", stderr="", returncode=0),
            ]

            output_file = BuildInfo.generate_build_file(
                tmp_path, version="2.0.0", output_file="build.info"
            )

            assert output_file.exists()
            assert output_file.name == "build.info"

    def test_generate_build_file_git_error(self, tmp_path):
        """Test build file generation with git error."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                1, "git", stderr="fatal: not a git repository"
            )

            with pytest.raises(GitError):
                BuildInfo.generate_build_file(tmp_path, version="1.0.0")
