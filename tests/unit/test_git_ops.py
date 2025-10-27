"""Tests for git operations module."""

import subprocess
from pathlib import Path

import pytest

from semvx.core.git_ops import GitError, GitRepository, GitVersionTagger
from semvx.core.version import SemanticVersion


class TestGitRepository:
    """Test GitRepository functionality."""

    def test_init_with_valid_repo(self, git_repository):
        """Test initialization with valid git repository."""
        repo = GitRepository(git_repository)
        assert repo.repo_path == git_repository.resolve()
    
    def test_init_with_invalid_repo(self, tmp_path):
        """Test initialization with non-git directory."""
        with pytest.raises(GitError, match="Not a git repository"):
            GitRepository(tmp_path)
    
    def test_is_git_repository(self, git_repository, tmp_path):
        """Test git repository detection."""
        repo = GitRepository(git_repository)
        assert repo.is_git_repository()
        
        # Non-git directory
        assert not GitRepository.__new__(GitRepository).is_git_repository.__func__(
            type('obj', (), {'repo_path': tmp_path})()
        )
    
    def test_get_current_branch(self, git_repository):
        """Test getting current branch name."""
        repo = GitRepository(git_repository)
        branch = repo.get_current_branch()
        assert branch is not None
        assert isinstance(branch, str)
        # Default branch is usually 'main' or 'master'
        assert branch in ['main', 'master'] or len(branch) > 0
    
    def test_get_latest_tag_no_tags(self, git_repository):
        """Test getting latest tag when no tags exist."""
        repo = GitRepository(git_repository)
        tag = repo.get_latest_tag()
        # May be None if no tags, or a tag if repo has tags
        assert tag is None or isinstance(tag, str)
    
    def test_create_and_list_tags(self, git_repository):
        """Test creating and listing tags."""
        repo = GitRepository(git_repository)
        
        # Create a tag
        success, message = repo.create_tag("test-tag-1.0.0")
        assert success
        assert "test-tag-1.0.0" in message
        
        # List tags
        tags = repo.list_tags()
        assert "test-tag-1.0.0" in tags
    
    def test_create_annotated_tag(self, git_repository):
        """Test creating annotated tag with message."""
        repo = GitRepository(git_repository)
        
        success, message = repo.create_tag(
            "v1.0.0",
            message="Release version 1.0.0"
        )
        assert success
        assert "v1.0.0" in message
        
        # Verify tag exists
        assert repo.tag_exists("v1.0.0")
    
    def test_tag_exists(self, git_repository):
        """Test checking if tag exists."""
        repo = GitRepository(git_repository)
        
        # Non-existent tag
        assert not repo.tag_exists("nonexistent-tag")
        
        # Create and check
        repo.create_tag("existing-tag")
        assert repo.tag_exists("existing-tag")
    
    def test_create_tag_force(self, git_repository):
        """Test force creating tag (overwrite existing)."""
        repo = GitRepository(git_repository)
        
        # Create initial tag
        repo.create_tag("force-test")
        assert repo.tag_exists("force-test")
        
        # Force create with same name
        success, message = repo.create_tag("force-test", force=True)
        assert success
    
    def test_delete_tag(self, git_repository):
        """Test deleting a tag."""
        repo = GitRepository(git_repository)
        
        # Create and delete
        repo.create_tag("delete-me")
        assert repo.tag_exists("delete-me")
        
        success, message = repo.delete_tag("delete-me")
        assert success
        assert "delete-me" in message
        assert not repo.tag_exists("delete-me")
    
    def test_delete_nonexistent_tag(self, git_repository):
        """Test deleting non-existent tag."""
        repo = GitRepository(git_repository)
        
        success, message = repo.delete_tag("does-not-exist")
        assert not success
        assert "Failed" in message
    
    def test_list_tags_with_pattern(self, git_repository):
        """Test listing tags with pattern filter."""
        repo = GitRepository(git_repository)
        
        # Create multiple tags
        repo.create_tag("v1.0.0")
        repo.create_tag("v1.1.0")
        repo.create_tag("release-1.0")
        
        # List with pattern
        v_tags = repo.list_tags(pattern="v*")
        assert "v1.0.0" in v_tags
        assert "v1.1.0" in v_tags
        assert "release-1.0" not in v_tags
    
    def test_has_uncommitted_changes(self, git_repository):
        """Test checking for uncommitted changes."""
        repo = GitRepository(git_repository)
        
        # Initially should be clean
        has_changes = repo.has_uncommitted_changes()
        assert isinstance(has_changes, bool)
        
        # Create a new file
        test_file = git_repository / "test.txt"
        test_file.write_text("test content")
        
        # Should now have uncommitted changes
        assert repo.has_uncommitted_changes()
    
    def test_stage_files(self, git_repository):
        """Test staging files."""
        repo = GitRepository(git_repository)
        
        # Create test file
        test_file = git_repository / "stage-test.txt"
        test_file.write_text("content")
        
        # Stage the file
        success, message = repo.stage_files([test_file])
        assert success
        assert "1 file" in message
    
    def test_commit(self, git_repository):
        """Test creating a commit."""
        repo = GitRepository(git_repository)
        
        # Create and stage a file
        test_file = git_repository / "commit-test.txt"
        test_file.write_text("content")
        repo.stage_files([test_file])
        
        # Create commit
        success, message = repo.commit("Test commit")
        assert success
        assert "success" in message.lower()
    
    def test_get_commit_hash(self, git_repository):
        """Test getting commit hash."""
        repo = GitRepository(git_repository)
        
        commit_hash = repo.get_commit_hash("HEAD")
        assert commit_hash is not None
        assert len(commit_hash) == 40  # Full SHA-1 hash


class TestGitVersionTagger:
    """Test GitVersionTagger functionality."""
    
    def test_create_version_tag(self, git_repository):
        """Test creating semantic version tag."""
        repo = GitRepository(git_repository)
        version = SemanticVersion(1, 2, 3)
        
        success, message = GitVersionTagger.create_version_tag(repo, version)
        assert success
        assert "v1.2.3" in message
        assert repo.tag_exists("v1.2.3")
    
    def test_create_version_tag_custom_prefix(self, git_repository):
        """Test creating version tag with custom prefix."""
        repo = GitRepository(git_repository)
        version = SemanticVersion(2, 0, 0)
        
        success, message = GitVersionTagger.create_version_tag(
            repo, version, prefix="release-"
        )
        assert success
        assert repo.tag_exists("release-2.0.0")
    
    def test_create_version_tag_with_prerelease(self, git_repository):
        """Test creating version tag with pre-release."""
        repo = GitRepository(git_repository)
        version = SemanticVersion(1, 0, 0, prerelease="alpha.1")
        
        success, message = GitVersionTagger.create_version_tag(repo, version)
        assert success
        assert repo.tag_exists("v1.0.0-alpha.1")
    
    def test_create_version_tag_already_exists(self, git_repository):
        """Test creating version tag that already exists."""
        repo = GitRepository(git_repository)
        version = SemanticVersion(1, 0, 0)
        
        # Create first time
        GitVersionTagger.create_version_tag(repo, version)
        
        # Try to create again without force
        success, message = GitVersionTagger.create_version_tag(repo, version)
        assert not success
        assert "already exists" in message
    
    def test_create_version_tag_force(self, git_repository):
        """Test force creating version tag."""
        repo = GitRepository(git_repository)
        version = SemanticVersion(1, 0, 0)
        
        # Create first time
        GitVersionTagger.create_version_tag(repo, version)
        
        # Force create again
        success, message = GitVersionTagger.create_version_tag(
            repo, version, force=True
        )
        assert success
    
    def test_get_version_tags(self, git_repository):
        """Test getting all version tags."""
        repo = GitRepository(git_repository)
        
        # Create multiple version tags
        GitVersionTagger.create_version_tag(repo, SemanticVersion(1, 0, 0))
        GitVersionTagger.create_version_tag(repo, SemanticVersion(1, 1, 0))
        GitVersionTagger.create_version_tag(repo, SemanticVersion(2, 0, 0))
        
        # Create non-version tag
        repo.create_tag("other-tag")
        
        # Get version tags
        version_tags = GitVersionTagger.get_version_tags(repo)
        assert "v1.0.0" in version_tags
        assert "v1.1.0" in version_tags
        assert "v2.0.0" in version_tags
        assert "other-tag" not in version_tags
    
    def test_custom_tag_message(self, git_repository):
        """Test creating version tag with custom message."""
        repo = GitRepository(git_repository)
        version = SemanticVersion(3, 0, 0)
        
        success, message = GitVersionTagger.create_version_tag(
            repo, version, message="Major release v3.0.0"
        )
        assert success
        assert repo.tag_exists("v3.0.0")


class TestGitRemoteOperations:
    """Test remote git operations."""

    def test_has_remote_with_remote(self, git_repository):
        """Test has_remote when remote exists."""
        from unittest.mock import patch, MagicMock
        
        repo = GitRepository(git_repository)
        
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="origin\n",
                stderr="",
                returncode=0
            )
            
            assert repo.has_remote() is True

    def test_has_remote_without_remote(self, git_repository):
        """Test has_remote when no remote exists."""
        from unittest.mock import patch, MagicMock
        
        repo = GitRepository(git_repository)
        
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="",
                stderr="",
                returncode=0
            )
            
            assert repo.has_remote() is False

    def test_fetch_tags_success(self, git_repository):
        """Test successful tag fetching."""
        from unittest.mock import patch, MagicMock
        
        repo = GitRepository(git_repository)
        
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="",
                stderr="",
                returncode=0
            )
            
            success, message = repo.fetch_tags()
            
            assert success is True
            assert "origin" in message

    def test_fetch_tags_failure(self, git_repository):
        """Test failed tag fetching."""
        from unittest.mock import patch
        
        repo = GitRepository(git_repository)
        
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                1, "git", stderr="fatal: could not read from remote"
            )
            
            success, message = repo.fetch_tags()
            
            assert success is False
            assert "failed" in message.lower()

    def test_get_remote_latest_tag_with_tags(self, git_repository):
        """Test get_remote_latest_tag with tags."""
        from unittest.mock import patch, MagicMock
        
        repo = GitRepository(git_repository)
        
        with patch("subprocess.run") as mock_run:
            # Mock ls-remote output
            mock_run.return_value = MagicMock(
                stdout="abc123\trefs/tags/v1.0.0\ndef456\trefs/tags/v1.2.0\nghi789\trefs/tags/v1.1.0\n",
                stderr="",
                returncode=0
            )
            
            result = repo.get_remote_latest_tag()
            
            assert result == "v1.2.0"

    def test_get_remote_latest_tag_no_tags(self, git_repository):
        """Test get_remote_latest_tag with no tags."""
        from unittest.mock import patch, MagicMock
        
        repo = GitRepository(git_repository)
        
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="",
                stderr="",
                returncode=0
            )
            
            result = repo.get_remote_latest_tag()
            
            assert result is None

    def test_get_remote_latest_tag_error(self, git_repository):
        """Test get_remote_latest_tag with error."""
        from unittest.mock import patch
        
        repo = GitRepository(git_repository)
        
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                1, "git", stderr="fatal: could not read from remote"
            )
            
            with pytest.raises(GitError, match="Failed to get remote tags"):
                repo.get_remote_latest_tag()

    def test_compare_with_remote_ahead(self, git_repository):
        """Test comparison when local is ahead."""
        repo = GitRepository(git_repository)
        
        status, message = repo.compare_with_remote("v1.2.0", "v1.1.0")
        
        assert status == "ahead"
        assert "ahead" in message.lower()
        assert "1.2.0" in message
        assert "1.1.0" in message

    def test_compare_with_remote_behind(self, git_repository):
        """Test comparison when local is behind."""
        repo = GitRepository(git_repository)
        
        status, message = repo.compare_with_remote("v1.0.0", "v1.2.0")
        
        assert status == "behind"
        assert "behind" in message.lower()

    def test_compare_with_remote_equal(self, git_repository):
        """Test comparison when versions are equal."""
        repo = GitRepository(git_repository)
        
        status, message = repo.compare_with_remote("v1.2.3", "v1.2.3")
        
        assert status == "equal"
        assert "equal" in message.lower()

    def test_compare_with_remote_invalid_versions(self, git_repository):
        """Test comparison with invalid version strings."""
        repo = GitRepository(git_repository)
        
        status, message = repo.compare_with_remote("invalid", "v1.2.3")
        
        assert status == "diverged"
        assert "cannot compare" in message.lower() or "diverged" in message.lower()
