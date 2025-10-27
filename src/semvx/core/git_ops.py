"""
Git operations module for SEMVX.

Provides git repository operations including tag creation, commit management,
and repository validation.
"""

import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

from semvx.core.version import SemanticVersion


class GitError(Exception):
    """Raised when git operations fail."""

    pass


class GitRepository:
    """
    Handles git repository operations.

    Provides methods for tag creation, commit operations, and repository validation.
    """

    def __init__(self, repo_path: Path):
        """
        Initialize git repository handler.

        Args:
            repo_path: Path to the git repository

        Raises:
            GitError: If path is not a valid git repository
        """
        self.repo_path = repo_path.resolve()
        if not self.is_git_repository():
            raise GitError(f"Not a git repository: {repo_path}")

    def is_git_repository(self) -> bool:
        """Check if the path is a valid git repository."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False,
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def get_current_branch(self) -> Optional[str]:
        """Get the current branch name."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise GitError(f"Failed to get current branch: {e}")

    def get_latest_tag(self) -> Optional[str]:
        """Get the latest semantic version tag."""
        try:
            result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except subprocess.CalledProcessError:
            return None

    def list_tags(self, pattern: Optional[str] = None) -> List[str]:
        """
        List all tags in the repository.

        Args:
            pattern: Optional glob pattern to filter tags (e.g., "v*")

        Returns:
            List of tag names
        """
        try:
            cmd = ["git", "tag", "-l"]
            if pattern:
                cmd.append(pattern)

            result = subprocess.run(
                cmd, cwd=self.repo_path, capture_output=True, text=True, check=True
            )
            tags = result.stdout.strip().split("\n")
            return [t for t in tags if t]  # Filter empty strings
        except subprocess.CalledProcessError as e:
            raise GitError(f"Failed to list tags: {e}")

    def tag_exists(self, tag_name: str) -> bool:
        """Check if a tag exists."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", tag_name],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False,
            )
            return result.returncode == 0
        except subprocess.CalledProcessError:
            return False

    def has_remote(self) -> bool:
        """Check if repository has a remote configured."""
        try:
            result = subprocess.run(
                ["git", "remote"], cwd=self.repo_path, capture_output=True, text=True, check=True
            )
            return bool(result.stdout.strip())
        except subprocess.CalledProcessError:
            return False

    def fetch_tags(self, remote: str = "origin") -> Tuple[bool, str]:
        """
        Fetch tags from remote repository.

        Args:
            remote: Name of remote (default: "origin")

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            subprocess.run(
                ["git", "fetch", remote, "--tags"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            return True, f"Fetched tags from {remote}"
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else str(e)
            return False, f"Failed to fetch tags: {error_msg}"

    def get_remote_latest_tag(self, remote: str = "origin") -> Optional[str]:
        """
        Get the latest semantic version tag from remote.

        Args:
            remote: Name of remote (default: "origin")

        Returns:
            Latest tag name or None if no tags found
        """
        try:
            # List remote tags
            result = subprocess.run(
                ["git", "ls-remote", "--tags", remote],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )

            if not result.stdout.strip():
                return None

            # Parse tags from output
            tags = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                # Format: <hash>\trefs/tags/<tagname>
                parts = line.split("\t")
                if len(parts) == 2:
                    tag_ref = parts[1]
                    if tag_ref.startswith("refs/tags/"):
                        tag_name = tag_ref.replace("refs/tags/", "")
                        # Skip ^{} annotations
                        if not tag_name.endswith("^{}"):
                            tags.append(tag_name)

            if not tags:
                return None

            # Filter and sort semantic version tags
            from semvx.core.version import SemanticVersion, VersionParseError

            version_tags = []
            for tag in tags:
                try:
                    # Try parsing as semantic version
                    version = SemanticVersion.parse(tag)
                    version_tags.append((version, tag))
                except VersionParseError:
                    continue

            if not version_tags:
                return None

            # Sort by version and return latest
            version_tags.sort(key=lambda x: x[0], reverse=True)
            return version_tags[0][1]

        except subprocess.CalledProcessError as e:
            raise GitError(f"Failed to get remote tags: {e.stderr.strip() if e.stderr else str(e)}")

    def compare_with_remote(self, local_tag: str, remote_tag: str) -> Tuple[str, str]:
        """
        Compare local and remote tags.

        Args:
            local_tag: Local tag name
            remote_tag: Remote tag name

        Returns:
            Tuple of (status: str, message: str)
            Status can be: "ahead", "behind", "equal", "diverged"
        """
        from semvx.core.version import SemanticVersion, VersionParseError

        try:
            local_version = SemanticVersion.parse(local_tag)
            remote_version = SemanticVersion.parse(remote_tag)

            if local_version > remote_version:
                return "ahead", f"Local is ahead: {local_tag} > {remote_tag}"
            elif local_version < remote_version:
                return "behind", f"Local is behind: {local_tag} < {remote_tag}"
            else:
                return "equal", f"Local and remote are equal: {local_tag}"

        except VersionParseError:
            # Fall back to string comparison
            if local_tag == remote_tag:
                return "equal", f"Local and remote are equal: {local_tag}"
            else:
                return "diverged", f"Cannot compare: {local_tag} vs {remote_tag}"

    def create_tag(
        self, tag_name: str, message: Optional[str] = None, force: bool = False
    ) -> Tuple[bool, str]:
        """
        Create a git tag.

        Args:
            tag_name: Name of the tag to create
            message: Optional tag message (creates annotated tag)
            force: Whether to force tag creation (overwrite existing)

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            cmd = ["git", "tag"]

            if force:
                cmd.append("-f")

            if message:
                cmd.extend(["-a", tag_name, "-m", message])
            else:
                cmd.append(tag_name)

            subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True, check=True)

            return True, f"Created tag '{tag_name}'"

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else str(e)
            return False, f"Failed to create tag: {error_msg}"

    def delete_tag(self, tag_name: str) -> Tuple[bool, str]:
        """
        Delete a git tag.

        Args:
            tag_name: Name of the tag to delete

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            subprocess.run(
                ["git", "tag", "-d", tag_name],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            return True, f"Deleted tag '{tag_name}'"
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else str(e)
            return False, f"Failed to delete tag: {error_msg}"

    def has_uncommitted_changes(self) -> bool:
        """Check if there are uncommitted changes."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            return bool(result.stdout.strip())
        except subprocess.CalledProcessError as e:
            raise GitError(f"Failed to check git status: {e}")

    def stage_files(self, files: List[Path]) -> Tuple[bool, str]:
        """
        Stage files for commit.

        Args:
            files: List of file paths to stage

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            file_paths = [str(f) for f in files]
            subprocess.run(
                ["git", "add"] + file_paths,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            return True, f"Staged {len(files)} file(s)"
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else str(e)
            return False, f"Failed to stage files: {error_msg}"

    def commit(self, message: str, amend: bool = False, no_edit: bool = False) -> Tuple[bool, str]:
        """
        Create a git commit.

        Args:
            message: Commit message
            amend: Whether to amend the previous commit
            no_edit: Don't edit commit message when amending

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            cmd = ["git", "commit", "-m", message]

            if amend:
                cmd.append("--amend")
                if no_edit:
                    cmd.append("--no-edit")

            subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True, check=True)

            return True, "Commit created successfully"

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else str(e)
            return False, f"Failed to commit: {error_msg}"

    def get_commit_hash(self, ref: str = "HEAD") -> Optional[str]:
        """Get the commit hash for a reference."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", ref],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None


class GitVersionTagger:
    """Helper class for creating semantic version tags."""

    @staticmethod
    def create_version_tag(
        repo: GitRepository,
        version: SemanticVersion,
        prefix: str = "v",
        message: Optional[str] = None,
        force: bool = False,
    ) -> Tuple[bool, str]:
        """
        Create a semantic version tag.

        Args:
            repo: GitRepository instance
            version: SemanticVersion to tag
            prefix: Tag prefix (default "v")
            message: Optional tag message
            force: Whether to force tag creation

        Returns:
            Tuple of (success: bool, message: str)
        """
        tag_name = f"{prefix}{version}"

        if not force and repo.tag_exists(tag_name):
            return False, f"Tag '{tag_name}' already exists (use --force to overwrite)"

        if message is None:
            message = f"Release {version}"

        return repo.create_tag(tag_name, message, force)

    @staticmethod
    def get_version_tags(repo: GitRepository, prefix: str = "v") -> List[str]:
        """Get all version tags with the specified prefix."""
        return repo.list_tags(pattern=f"{prefix}*")
