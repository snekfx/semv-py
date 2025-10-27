"""Build information and build count tracking.

This module provides functionality for calculating build counts and generating
build information for deployment tracking.
"""

import subprocess
from pathlib import Path
from typing import Optional, Tuple

from .git_ops import GitError


class BuildInfo:
    """Build information calculator and tracker."""

    @staticmethod
    def get_build_count(repo_path: Path, since_tag: Optional[str] = None) -> int:
        """Get build count (commit count) for repository.

        Build count is the number of commits since a specific tag or since
        the beginning of the repository.

        Args:
            repo_path: Path to git repository
            since_tag: Optional tag to count from (default: count all commits)

        Returns:
            Number of commits (build count)

        Raises:
            GitError: If git command fails
        """
        try:
            if since_tag:
                # Count commits since specific tag
                cmd = ["git", "rev-list", "--count", f"{since_tag}..HEAD"]
            else:
                # Count all commits
                cmd = ["git", "rev-list", "--count", "HEAD"]

            result = subprocess.run(
                cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True,
            )

            return int(result.stdout.strip())

        except subprocess.CalledProcessError as e:
            raise GitError(f"Failed to get build count: {e.stderr.strip()}")
        except ValueError as e:
            raise GitError(f"Invalid build count output: {e}")

    @staticmethod
    def get_commit_hash(repo_path: Path, short: bool = True) -> str:
        """Get current commit hash.

        Args:
            repo_path: Path to git repository
            short: If True, return short hash (7 chars), else full hash

        Returns:
            Commit hash string

        Raises:
            GitError: If git command fails
        """
        try:
            cmd = ["git", "rev-parse"]
            if short:
                cmd.append("--short")
            cmd.append("HEAD")

            result = subprocess.run(
                cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True,
            )

            return result.stdout.strip()

        except subprocess.CalledProcessError as e:
            raise GitError(f"Failed to get commit hash: {e.stderr.strip()}")

    @staticmethod
    def generate_build_file(
        repo_path: Path,
        version: str,
        output_file: str = ".build_info",
    ) -> Path:
        """Generate build information file.

        Creates a file with build metadata including version, build count,
        commit hash, and timestamp.

        Args:
            repo_path: Path to git repository
            version: Version string to include
            output_file: Name of output file (default: .build_info)

        Returns:
            Path to generated build file

        Raises:
            GitError: If git operations fail
            IOError: If file write fails
        """
        import datetime

        # Gather build information
        build_count = BuildInfo.get_build_count(repo_path)
        commit_hash = BuildInfo.get_commit_hash(repo_path, short=False)
        commit_hash_short = BuildInfo.get_commit_hash(repo_path, short=True)
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Create build info content
        content = f"""# Build Information
# Generated: {timestamp}

VERSION={version}
BUILD_COUNT={build_count}
COMMIT_HASH={commit_hash}
COMMIT_HASH_SHORT={commit_hash_short}
BUILD_TIMESTAMP={timestamp}
"""

        # Write to file
        output_path = repo_path / output_file
        output_path.write_text(content)

        return output_path
