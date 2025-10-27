"""
Repository status module for comprehensive project analysis.
"""

import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from semvx.core.git_ops import GitRepository
from semvx.core.version import SemanticVersion, VersionParseError


@dataclass
class RepositoryStatus:
    """Comprehensive repository status information."""
    user: str
    repo_name: str
    current_branch: str
    main_branch: str
    changed_files: int
    uncommitted_changes: bool
    local_build: Optional[int]
    remote_build: Optional[int]
    days_since_last: int
    last_commit_msg: Optional[str]
    last_tag: Optional[str]
    release_tag: Optional[str]
    current_version: Optional[str]
    next_version: Optional[str]
    package_version: Optional[str]
    pending_actions: List[str]


class RepositoryAnalyzer:
    """Analyzes repository state and provides comprehensive status."""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.git_repo = GitRepository(repo_path)
    
    def get_status(self, fetch_remote: bool = False) -> RepositoryStatus:
        """
        Get comprehensive repository status.
        
        Args:
            fetch_remote: If True, fetch remote data (slow, requires network).
                         Default False for fast local-only status.
        """
        return RepositoryStatus(
            user=self._get_user(),
            repo_name=self._get_repo_name(),
            current_branch=self._get_current_branch(),
            main_branch=self._get_main_branch(),
            changed_files=self._get_changed_files_count(),
            uncommitted_changes=self.git_repo.has_uncommitted_changes(),
            local_build=self._get_local_build(),
            remote_build=self._get_remote_build(fetch=fetch_remote),
            days_since_last=self._get_days_since_last_commit(),
            last_commit_msg=self._get_last_commit_message(),
            last_tag=self._get_last_tag(),
            release_tag=self._get_release_tag(),
            current_version=self._get_current_version(),
            next_version=self._calculate_next_version(),
            package_version=self._get_package_version(),
            pending_actions=self._analyze_pending_actions()
        )

    def _get_user(self) -> str:
        """Get git user name."""
        try:
            result = subprocess.run(
                ["git", "config", "user.name"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip() or "unknown"
        except subprocess.CalledProcessError:
            return "unknown"
    
    def _get_repo_name(self) -> str:
        """Get repository name."""
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                url = result.stdout.strip()
                if url:
                    name = url.rstrip('/').split('/')[-1]
                    return name.replace('.git', '')
        except subprocess.CalledProcessError:
            pass
        return self.repo_path.name
    
    def _get_current_branch(self) -> str:
        """Get current branch name."""
        branch = self.git_repo.get_current_branch()
        return branch or "unknown"
    
    def _get_main_branch(self) -> str:
        """Determine main branch."""
        try:
            result = subprocess.run(
                ["git", "branch", "-r"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            branches = result.stdout
            if "origin/main" in branches:
                return "main"
            elif "origin/master" in branches:
                return "master"
            return "main"
        except subprocess.CalledProcessError:
            return "main"
    
    def _get_changed_files_count(self) -> int:
        """Get count of changed files."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            lines = [line for line in result.stdout.strip().split('\n') if line]
            return len(lines)
        except subprocess.CalledProcessError:
            return 0

    def _get_local_build(self) -> Optional[int]:
        """Get local build count."""
        try:
            result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return int(result.stdout.strip())
        except (subprocess.CalledProcessError, ValueError):
            return None
    
    def _get_remote_build(self, fetch: bool = False) -> Optional[int]:
        """
        Get remote build count.
        
        Args:
            fetch: If True, fetch remote tags first (slow, requires network)
        """
        try:
            # Only fetch if explicitly requested (network operation)
            if fetch:
                subprocess.run(
                    ["git", "fetch", "--tags", "--quiet"],
                    cwd=self.repo_path,
                    capture_output=True,
                    check=False,
                    timeout=5  # Add timeout to prevent hanging
                )
            
            # Try to get remote build count without fetching
            result = subprocess.run(
                ["git", "rev-list", "--count", "origin/HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False,
                timeout=2
            )
            if result.returncode == 0:
                return int(result.stdout.strip())
        except (subprocess.CalledProcessError, ValueError, subprocess.TimeoutExpired):
            pass
        return None
    
    def _get_days_since_last_commit(self) -> int:
        """Get days since last commit."""
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%ct"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            timestamp = int(result.stdout.strip())
            commit_date = datetime.fromtimestamp(timestamp)
            delta = datetime.now() - commit_date
            return delta.days
        except (subprocess.CalledProcessError, ValueError):
            return 0
    
    def _get_last_commit_message(self) -> Optional[str]:
        """Get last commit message."""
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%s"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip() or None
        except subprocess.CalledProcessError:
            return None

    def _get_last_tag(self) -> Optional[str]:
        """Get last tag."""
        return self.git_repo.get_latest_tag()
    
    def _get_release_tag(self) -> Optional[str]:
        """Get last release tag."""
        tags = self.git_repo.list_tags(pattern="v*")
        release_tags = []
        for tag in tags:
            try:
                version = SemanticVersion.parse(tag)
                if not version.prerelease:
                    release_tags.append((tag, version))
            except VersionParseError:
                continue
        if release_tags:
            release_tags.sort(key=lambda x: x[1], reverse=True)
            return release_tags[0][0]
        return None
    
    def _get_current_version(self) -> Optional[str]:
        """Get current version from git tags."""
        tag = self._get_last_tag()
        if tag:
            try:
                SemanticVersion.parse(tag)
                return tag
            except VersionParseError:
                pass
        return None
    
    def _calculate_next_version(self) -> Optional[str]:
        """Calculate next version based on commit analysis."""
        from semvx.core.commit_analyzer import CommitAnalyzer, BumpType
        
        current = self._get_current_version()
        if not current:
            return "v0.1.0"
        
        try:
            version = SemanticVersion.parse(current)
            
            # Analyze commits to determine bump type
            analyzer = CommitAnalyzer(self.repo_path)
            bump_type, _ = analyzer.get_suggested_bump(current)
            
            # Apply bump based on analysis
            if bump_type == BumpType.MAJOR:
                next_ver = version.bump_major()
            elif bump_type == BumpType.MINOR:
                next_ver = version.bump_minor()
            elif bump_type == BumpType.PATCH or bump_type == BumpType.DEV:
                next_ver = version.bump_patch()
            else:
                # No version-affecting commits
                return current
            
            return f"v{next_ver}"
        except VersionParseError:
            return None
    
    def _get_package_version(self) -> Optional[str]:
        """Get version from package files."""
        import re
        import json
        
        # Check pyproject.toml
        pyproject = self.repo_path / "pyproject.toml"
        if pyproject.exists():
            try:
                content = pyproject.read_text()
                match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
                if match:
                    return match.group(1)
            except Exception:
                pass
        
        # Check Cargo.toml
        cargo = self.repo_path / "Cargo.toml"
        if cargo.exists():
            try:
                content = cargo.read_text()
                match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
                if match:
                    return match.group(1)
            except Exception:
                pass
        
        # Check package.json
        package = self.repo_path / "package.json"
        if package.exists():
            try:
                data = json.loads(package.read_text())
                return data.get("version")
            except Exception:
                pass
        return None
    
    def _analyze_pending_actions(self) -> List[str]:
        """Analyze pending actions."""
        actions = []
        if self.git_repo.has_uncommitted_changes():
            count = self._get_changed_files_count()
            actions.append(f"{count} changes pending commit")
        current = self._get_current_version()
        next_ver = self._calculate_next_version()
        if current and next_ver and current != next_ver:
            actions.append(f"version needs bump ({current} -> {next_ver})")
        package_ver = self._get_package_version()
        if package_ver and current:
            try:
                pkg_semver = SemanticVersion.parse(package_ver)
                git_semver = SemanticVersion.parse(current)
                if pkg_semver != git_semver:
                    actions.append(f"version needs sync (package: {package_ver}, git: {current})")
            except VersionParseError:
                pass
        return actions
