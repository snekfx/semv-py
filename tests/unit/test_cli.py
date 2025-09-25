"""
Unit tests for the CLI module.
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from io import StringIO

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from semvx.cli.main import main, print_help, do_detection, do_status


class TestCLIMain:
    """Test main CLI entry point."""

    def test_version_flag(self, capsys):
        """Test --version flag output."""
        with patch.object(sys, 'argv', ['semvx', '--version']):
            main()
        captured = capsys.readouterr()
        assert "semvx 3.0.0-dev" in captured.out
        assert "Python rewrite" in captured.out

    def test_help_flag(self, capsys):
        """Test --help flag output."""
        with patch.object(sys, 'argv', ['semvx', '--help']):
            main()
        captured = capsys.readouterr()
        assert "USAGE:" in captured.out
        assert "COMMANDS:" in captured.out
        assert "detect" in captured.out
        assert "status" in captured.out

    def test_no_arguments(self, capsys):
        """Test behavior with no arguments."""
        with patch.object(sys, 'argv', ['semvx']):
            main()
        captured = capsys.readouterr()
        assert "semvx 3.0.0-dev" in captured.out
        assert "Use 'semvx --help'" in captured.out

    @patch('semvx.cli.main.do_detection')
    def test_detect_command(self, mock_detect):
        """Test detect command routing."""
        with patch.object(sys, 'argv', ['semvx', 'detect']):
            main()
        mock_detect.assert_called_once()

    @patch('semvx.cli.main.do_status')
    def test_status_command(self, mock_status):
        """Test status command routing."""
        with patch.object(sys, 'argv', ['semvx', 'status']):
            main()
        mock_status.assert_called_once()

    def test_bump_command_stub(self, capsys):
        """Test bump command shows coming soon message."""
        with patch.object(sys, 'argv', ['semvx', 'bump', 'minor']):
            main()
        captured = capsys.readouterr()
        assert "coming soon" in captured.out.lower()
        assert "version management" in captured.out.lower()


class TestDetectionCommand:
    """Test detection command functionality."""

    @patch('semvx.cli.main.get_repository_context')
    def test_do_detection_success(self, mock_get_context, capsys):
        """Test successful project detection."""
        mock_context = {
            'repository': {'type': 'git'},
            'projects': [
                {
                    'type': 'python',
                    'version': '1.2.3',
                    'version_file': 'pyproject.toml'
                }
            ],
            'validation': {
                'python': {'ok': True}
            }
        }
        mock_get_context.return_value = mock_context

        do_detection()
        captured = capsys.readouterr()

        assert "Repository Analysis" in captured.out
        assert "Repository Type: git" in captured.out
        assert "Projects Found: 1" in captured.out
        assert "python" in captured.out.lower()
        assert "1.2.3" in captured.out

    @patch('semvx.cli.main.get_repository_context')
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

    @patch('semvx.cli.main.get_repository_context')
    def test_do_status_with_projects(self, mock_get_context, capsys):
        """Test status display with projects."""
        mock_context = {
            'repository': {'type': 'git'},
            'projects': [
                {
                    'type': 'python',
                    'version': '2.0.0',
                    'version_file': 'pyproject.toml',
                    'name': 'test-project'
                },
                {
                    'type': 'rust',
                    'version': '1.0.0',
                    'version_file': 'Cargo.toml'
                }
            ],
            'validation': {}
        }
        mock_get_context.return_value = mock_context

        do_status()
        captured = capsys.readouterr()

        assert "Version Status" in captured.out
        assert "PYTHON Project" in captured.out
        assert "Version:      2.0.0" in captured.out
        assert "test-project" in captured.out
        assert "RUST Project" in captured.out
        assert "Total projects found: 2" in captured.out

    @patch('semvx.cli.main.get_repository_context')
    def test_do_status_no_projects(self, mock_get_context, capsys):
        """Test status display with no projects."""
        mock_context = {
            'repository': {'type': 'directory'},
            'projects': [],
            'validation': {}
        }
        mock_get_context.return_value = mock_context

        do_status()
        captured = capsys.readouterr()

        assert "No projects detected" in captured.out


class TestHelp:
    """Test help message output."""

    def test_print_help_content(self, capsys):
        """Test help message contains all expected sections."""
        print_help()
        captured = capsys.readouterr()

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

        # Check for notes
        assert "Python rewrite" in captured.out
        assert "namespace separation" in captured.out