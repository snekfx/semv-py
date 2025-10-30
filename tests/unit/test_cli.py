"""
Unit tests for the CLI module.
"""

import os
import sys
from unittest.mock import patch

import pytest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from semvx.cli.main import do_detection, do_status, main, print_help


class TestCLIMain:
    """Test main CLI entry point."""

    def test_version_flag(self, capsys):
        """Test --version flag output."""
        with patch.object(sys, "argv", ["semvx", "--version"]):
            main()
        captured = capsys.readouterr()
        # Should output version from pyproject.toml with branding
        assert "Version:" in captured.out
        assert "1.3.0" in captured.out
        assert "AGPL-3.0" in captured.out
        assert "Copyright" in captured.out

    def test_help_flag(self, capsys):
        """Test --help flag output."""
        with patch.object(sys, "argv", ["semvx", "--help"]):
            main()
        captured = capsys.readouterr()
        assert "USAGE:" in captured.out
        assert "COMMANDS:" in captured.out
        assert "detect" in captured.out
        assert "status" in captured.out

    def test_no_arguments(self, capsys):
        """Test behavior with no arguments."""
        with patch.object(sys, "argv", ["semvx"]):
            main()
        captured = capsys.readouterr()
        # Should show full help menu with branding
        assert "Version:" in captured.out
        assert "1.3.0" in captured.out
        assert "USAGE:" in captured.out
        assert "COMMANDS:" in captured.out
        assert "COMMIT LABELS:" in captured.out

    @patch("semvx.cli.main.do_detection")
    def test_detect_command(self, mock_detect):
        """Test detect command routing."""
        with patch.object(sys, "argv", ["semvx", "detect"]):
            main()
        mock_detect.assert_called_once()

    @patch("semvx.cli.main.do_status")
    def test_status_command(self, mock_status):
        """Test status command routing."""
        with patch.object(sys, "argv", ["semvx", "status"]):
            main()
        mock_status.assert_called_once()

    @patch("semvx.cli.main.get_repository_context")
    def test_bump_command(self, mock_get_context, capsys):
        """Test bump command with version calculation."""
        mock_context = {
            "repository": {"type": "git", "root": "/test"},
            "projects": [{"type": "python", "version": "1.2.3", "version_file": "pyproject.toml"}],
            "validation": {},
        }
        mock_get_context.return_value = mock_context

        with patch.object(sys, "argv", ["semvx", "bump", "minor"]):
            main()
        captured = capsys.readouterr()
        assert "bumping minor version" in captured.out.lower()
        assert "1.2.3" in captured.out
        assert "1.3.0" in captured.out


class TestDetectionCommand:
    """Test detection command functionality."""

    @patch("semvx.cli.main.get_repository_context")
    def test_do_detection_success(self, mock_get_context, capsys):
        """Test successful project detection."""
        mock_context = {
            "repository": {"type": "git"},
            "projects": [{"type": "python", "version": "1.2.3", "version_file": "pyproject.toml"}],
            "validation": {"python": {"ok": True}},
        }
        mock_get_context.return_value = mock_context

        do_detection()
        captured = capsys.readouterr()

        assert "Repository Analysis" in captured.out
        assert "Repository Type: git" in captured.out
        assert "Projects Found: 1" in captured.out
        assert "python" in captured.out.lower()
        assert "1.2.3" in captured.out

    @patch("semvx.cli.main.get_repository_context")
    def test_do_detection_error(self, mock_get_context, capsys):
        """Test detection with error."""
        mock_get_context.side_effect = Exception("Test error")

        with pytest.raises(SystemExit) as exc_info:
            do_detection()
        assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "Error during detection" in captured.err
        assert "Test error" in captured.err


class TestStatusCommand:
    """Test status command functionality."""

    @patch("semvx.cli.main.RepositoryAnalyzer")
    def test_do_status_with_repository(self, mock_analyzer_class, capsys):
        """Test status display with repository."""
        from semvx.core.repository_status import RepositoryStatus

        # Create mock status
        mock_status = RepositoryStatus(
            user="testuser",
            repo_name="test-repo",
            current_branch="main",
            main_branch="main",
            changed_files=5,
            uncommitted_changes=True,
            local_build=10,
            remote_build=8,
            days_since_last=2,
            last_commit_msg="test commit",
            last_tag="v1.0.0",
            release_tag="v1.0.0",
            current_version="v1.0.0",
            next_version="v1.1.0",
            package_version="1.0.0",
            pending_actions=["5 changes pending commit"],
        )

        # Mock the analyzer
        mock_analyzer = mock_analyzer_class.return_value
        mock_analyzer.get_status.return_value = mock_status

        # Set environment to use plain mode for easier testing
        import os

        os.environ["SEMVX_USE_BOXY"] = "false"

        do_status()
        captured = capsys.readouterr()

        # Clean up
        os.environ.pop("SEMVX_USE_BOXY", None)

        assert "Repository Status" in captured.out
        assert "testuser" in captured.out
        assert "test-repo" in captured.out
        assert "5 changes pending commit" in captured.out

    @patch("semvx.cli.main.RepositoryAnalyzer")
    def test_do_status_data_mode(self, mock_analyzer_class, capsys):
        """Test status display in data mode (JSON)."""
        import json

        from semvx.core.repository_status import RepositoryStatus

        mock_status = RepositoryStatus(
            user="testuser",
            repo_name="test-repo",
            current_branch="main",
            main_branch="main",
            changed_files=0,
            uncommitted_changes=False,
            local_build=5,
            remote_build=5,
            days_since_last=1,
            last_commit_msg="test",
            last_tag="v1.0.0",
            release_tag="v1.0.0",
            current_version="v1.0.0",
            next_version="v1.0.0",
            package_version="1.0.0",
            pending_actions=[],
        )

        mock_analyzer = mock_analyzer_class.return_value
        mock_analyzer.get_status.return_value = mock_status

        # Set data view mode
        import os

        os.environ["SEMVX_VIEW"] = "data"

        do_status()
        captured = capsys.readouterr()

        # Clean up
        os.environ.pop("SEMVX_VIEW", None)

        # Should be valid JSON
        data = json.loads(captured.out)
        assert data["user"] == "testuser"
        assert data["repo_name"] == "test-repo"


class TestHelp:
    """Test help message output."""

    def test_print_help_content(self, capsys):
        """Test help message contains all expected sections."""
        print_help()
        captured = capsys.readouterr()

        # Check for branding signature
        assert "Version:" in captured.out
        assert "AGPL-3.0" in captured.out
        assert "Copyright" in captured.out
        assert "📊 Semantic Version Manager for Modern Development" in captured.out

        # Check for main sections
        assert "USAGE:" in captured.out
        assert "COMMANDS:" in captured.out
        assert "EXAMPLES:" in captured.out

        # Check for commands
        assert "detect" in captured.out
        assert "status" in captured.out
        assert "bump" in captured.out
        assert "version" in captured.out
        assert "tag" in captured.out

        # Check for examples
        assert "semvx detect" in captured.out
        assert "semvx status" in captured.out

        # Check for commit labels section
        assert "COMMIT LABELS:" in captured.out
        assert "major, breaking, api" in captured.out
        assert "feat, feature, add, minor" in captured.out
        assert "fix, patch, bug, hotfix, up" in captured.out

        # Check for notes
        assert "Python rewrite" in captured.out
        assert "namespace separation" in captured.out
