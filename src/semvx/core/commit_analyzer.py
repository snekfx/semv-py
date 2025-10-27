"""
Commit analyzer for semv - Analyzes git commits to determine version bumps.

Implements the full semv commit label convention:
- major|breaking|api|arch|ux: → Major bump
- feat|feature|add|minor|ref|mrg: → Minor bump  
- fix|patch|bug|hotfix|up|imp|qol|stb: → Patch bump
- dev: → Dev build
- doc|admin|lic|clean|x: → Ignored
"""

import re
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple


class BumpType(Enum):
    """Version bump types."""
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    DEV = "dev"
    NONE = "none"


@dataclass
class CommitAnalysis:
    """Result of commit analysis."""
    bump_type: BumpType
    commit_count: int
    major_commits: List[str]
    minor_commits: List[str]
    patch_commits: List[str]
    dev_commits: List[str]
    ignored_commits: List[str]


class CommitAnalyzer:
    """Analyzes git commits to determine version bumps."""
    
    # Commit label patterns (order matters - checked in sequence)
    MAJOR_PREFIXES = [
        "major:", "breaking:", "api:", "arch:", "ux:"
    ]
    
    MINOR_PREFIXES = [
        "feat:", "feature:", "add:", "minor:", "ref:", "mrg:"
    ]
    
    PATCH_PREFIXES = [
        "fix:", "patch:", "bug:", "hotfix:", "up:", "imp:", "qol:", "stb:"
    ]
    
    DEV_PREFIXES = ["dev:"]
    
    IGNORED_PREFIXES = ["doc:", "admin:", "lic:", "clean:", "x:"]
    
    def __init__(self, repo_path: Path):
        """
        Initialize commit analyzer.
        
        Args:
            repo_path: Path to git repository
        """
        self.repo_path = repo_path
    
    def analyze_commits_since_tag(self, tag: Optional[str] = None) -> CommitAnalysis:
        """
        Analyze commits since a specific tag.
        
        Args:
            tag: Tag to analyze from (None = all commits)
            
        Returns:
            CommitAnalysis with bump recommendation
        """
        commits = self._get_commits_since(tag)
        
        major_commits = []
        minor_commits = []
        patch_commits = []
        dev_commits = []
        ignored_commits = []
        
        for commit in commits:
            bump = self._classify_commit(commit)
            
            if bump == BumpType.MAJOR:
                major_commits.append(commit)
            elif bump == BumpType.MINOR:
                minor_commits.append(commit)
            elif bump == BumpType.PATCH:
                patch_commits.append(commit)
            elif bump == BumpType.DEV:
                dev_commits.append(commit)
            else:
                ignored_commits.append(commit)
        
        # Determine overall bump type (highest priority wins)
        if major_commits:
            bump_type = BumpType.MAJOR
        elif minor_commits:
            bump_type = BumpType.MINOR
        elif patch_commits:
            bump_type = BumpType.PATCH
        elif dev_commits:
            bump_type = BumpType.DEV
        else:
            bump_type = BumpType.NONE
        
        return CommitAnalysis(
            bump_type=bump_type,
            commit_count=len(commits),
            major_commits=major_commits,
            minor_commits=minor_commits,
            patch_commits=patch_commits,
            dev_commits=dev_commits,
            ignored_commits=ignored_commits
        )
    
    def _get_commits_since(self, tag: Optional[str] = None) -> List[str]:
        """
        Get commit messages since a tag.
        
        Args:
            tag: Tag to get commits since (None = all commits)
            
        Returns:
            List of commit messages
        """
        try:
            if tag:
                # Get commits since tag
                cmd = ["git", "log", f"{tag}..HEAD", "--format=%s"]
            else:
                # Get all commits
                cmd = ["git", "log", "--format=%s"]
            
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            commits = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
            return commits
            
        except subprocess.CalledProcessError:
            return []
    
    def _classify_commit(self, commit_msg: str) -> BumpType:
        """
        Classify a commit message by its prefix.
        
        Args:
            commit_msg: Commit message to classify
            
        Returns:
            BumpType for this commit
        """
        msg_lower = commit_msg.lower()
        
        # Check major prefixes
        for prefix in self.MAJOR_PREFIXES:
            if msg_lower.startswith(prefix):
                return BumpType.MAJOR
        
        # Check minor prefixes
        for prefix in self.MINOR_PREFIXES:
            if msg_lower.startswith(prefix):
                return BumpType.MINOR
        
        # Check patch prefixes
        for prefix in self.PATCH_PREFIXES:
            if msg_lower.startswith(prefix):
                return BumpType.PATCH
        
        # Check dev prefixes
        for prefix in self.DEV_PREFIXES:
            if msg_lower.startswith(prefix):
                return BumpType.DEV
        
        # Check ignored prefixes
        for prefix in self.IGNORED_PREFIXES:
            if msg_lower.startswith(prefix):
                return BumpType.NONE
        
        # Default: treat as patch if no prefix matches
        # (conservative approach - any unlabeled commit is a patch)
        return BumpType.PATCH
    
    def get_suggested_bump(self, current_tag: Optional[str] = None) -> Tuple[BumpType, str]:
        """
        Get suggested version bump with reasoning.
        
        Args:
            current_tag: Current version tag
            
        Returns:
            Tuple of (BumpType, reasoning string)
        """
        analysis = self.analyze_commits_since_tag(current_tag)
        
        if analysis.bump_type == BumpType.NONE:
            return BumpType.NONE, "No version-affecting commits found"
        
        reasons = []
        
        if analysis.major_commits:
            reasons.append(f"{len(analysis.major_commits)} major/breaking change(s)")
        if analysis.minor_commits:
            reasons.append(f"{len(analysis.minor_commits)} feature(s)")
        if analysis.patch_commits:
            reasons.append(f"{len(analysis.patch_commits)} fix(es)")
        if analysis.dev_commits:
            reasons.append(f"{len(analysis.dev_commits)} dev commit(s)")
        
        reasoning = f"Based on {analysis.commit_count} commit(s): {', '.join(reasons)}"
        
        return analysis.bump_type, reasoning
    
    def format_analysis_report(self, analysis: CommitAnalysis) -> str:
        """
        Format commit analysis as human-readable report.
        
        Args:
            analysis: CommitAnalysis to format
            
        Returns:
            Formatted report string
        """
        lines = []
        lines.append(f"📊 Commit Analysis ({analysis.commit_count} commits)")
        lines.append("")
        lines.append(f"Recommended Bump: {analysis.bump_type.value.upper()}")
        lines.append("")
        
        if analysis.major_commits:
            lines.append(f"🔴 Major Changes ({len(analysis.major_commits)}):")
            for commit in analysis.major_commits[:5]:  # Show first 5
                lines.append(f"  - {commit}")
            if len(analysis.major_commits) > 5:
                lines.append(f"  ... and {len(analysis.major_commits) - 5} more")
            lines.append("")
        
        if analysis.minor_commits:
            lines.append(f"🟡 Features ({len(analysis.minor_commits)}):")
            for commit in analysis.minor_commits[:5]:
                lines.append(f"  - {commit}")
            if len(analysis.minor_commits) > 5:
                lines.append(f"  ... and {len(analysis.minor_commits) - 5} more")
            lines.append("")
        
        if analysis.patch_commits:
            lines.append(f"🟢 Fixes ({len(analysis.patch_commits)}):")
            for commit in analysis.patch_commits[:5]:
                lines.append(f"  - {commit}")
            if len(analysis.patch_commits) > 5:
                lines.append(f"  ... and {len(analysis.patch_commits) - 5} more")
            lines.append("")
        
        if analysis.dev_commits:
            lines.append(f"🔵 Dev Commits ({len(analysis.dev_commits)}):")
            for commit in analysis.dev_commits[:3]:
                lines.append(f"  - {commit}")
            if len(analysis.dev_commits) > 3:
                lines.append(f"  ... and {len(analysis.dev_commits) - 3} more")
            lines.append("")
        
        if analysis.ignored_commits:
            lines.append(f"⚪ Ignored ({len(analysis.ignored_commits)}): docs, admin, etc.")
        
        return "\n".join(lines)
