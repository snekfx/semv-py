"""Tests for commit analyzer module."""

from unittest.mock import patch

from semvx.core.commit_analyzer import BumpType, CommitAnalyzer


class TestCommitClassification:
    """Test commit message classification."""

    def test_major_prefixes(self, git_repository):
        """Test major version bump prefixes."""
        analyzer = CommitAnalyzer(git_repository)

        major_commits = [
            "major: complete rewrite",
            "breaking: remove deprecated API",
            "api: change interface",
            "arch: restructure modules",
            "ux: redesign interface"
        ]

        for commit in major_commits:
            assert analyzer._classify_commit(commit) == BumpType.MAJOR

    def test_minor_prefixes(self, git_repository):
        """Test minor version bump prefixes."""
        analyzer = CommitAnalyzer(git_repository)

        minor_commits = [
            "feat: add new feature",
            "feature: implement auth",
            "add: new command",
            "minor: small addition",
            "ref: refactor module",
            "mrg: merge feature branch"
        ]

        for commit in minor_commits:
            assert analyzer._classify_commit(commit) == BumpType.MINOR

    def test_patch_prefixes(self, git_repository):
        """Test patch version bump prefixes."""
        analyzer = CommitAnalyzer(git_repository)

        patch_commits = [
            "fix: bug in parser",
            "patch: security issue",
            "bug: null pointer",
            "hotfix: critical bug",
            "up: update dependencies",
            "imp: improve performance",
            "qol: better error messages",
            "stb: mark as stable"
        ]

        for commit in patch_commits:
            assert analyzer._classify_commit(commit) == BumpType.PATCH

    def test_dev_prefix(self, git_repository):
        """Test dev build prefix."""
        analyzer = CommitAnalyzer(git_repository)
        assert analyzer._classify_commit("dev: refactor tests") == BumpType.DEV

    def test_ignored_prefixes(self, git_repository):
        """Test ignored commit prefixes."""
        analyzer = CommitAnalyzer(git_repository)

        ignored_commits = [
            "doc: update README",
            "admin: update team info",
            "lic: update copyright",
            "clean: remove old files",
            "x: temporary debug"
        ]

        for commit in ignored_commits:
            assert analyzer._classify_commit(commit) == BumpType.NONE

    def test_unlabeled_commit_defaults_to_patch(self, git_repository):
        """Test that unlabeled commits default to patch."""
        analyzer = CommitAnalyzer(git_repository)
        assert analyzer._classify_commit("some random commit") == BumpType.PATCH


class TestCommitAnalysis:
    """Test commit analysis functionality."""

    @patch('semvx.core.commit_analyzer.subprocess.run')
    def test_analyze_major_bump(self, mock_run, git_repository):
        """Test analysis recommends major bump."""
        mock_run.return_value.stdout = "breaking: remove API\nfeat: add feature\nfix: bug\n"
        mock_run.return_value.returncode = 0

        analyzer = CommitAnalyzer(git_repository)
        analysis = analyzer.analyze_commits_since_tag("v1.0.0")

        assert analysis.bump_type == BumpType.MAJOR
        assert len(analysis.major_commits) == 1
        assert len(analysis.minor_commits) == 1
        assert len(analysis.patch_commits) == 1

    @patch('semvx.core.commit_analyzer.subprocess.run')
    def test_analyze_minor_bump(self, mock_run, git_repository):
        """Test analysis recommends minor bump."""
        mock_run.return_value.stdout = "feat: new feature\nfix: bug fix\ndoc: update docs\n"
        mock_run.return_value.returncode = 0

        analyzer = CommitAnalyzer(git_repository)
        analysis = analyzer.analyze_commits_since_tag("v1.0.0")

        assert analysis.bump_type == BumpType.MINOR
        assert len(analysis.minor_commits) == 1
        assert len(analysis.patch_commits) == 1
        assert len(analysis.ignored_commits) == 1

    @patch('semvx.core.commit_analyzer.subprocess.run')
    def test_analyze_patch_bump(self, mock_run, git_repository):
        """Test analysis recommends patch bump."""
        mock_run.return_value.stdout = "fix: bug\ndoc: docs\n"
        mock_run.return_value.returncode = 0

        analyzer = CommitAnalyzer(git_repository)
        analysis = analyzer.analyze_commits_since_tag("v1.0.0")

        assert analysis.bump_type == BumpType.PATCH
        assert len(analysis.patch_commits) == 1

    @patch('semvx.core.commit_analyzer.subprocess.run')
    def test_get_suggested_bump_with_reasoning(self, mock_run, git_repository):
        """Test getting suggested bump with reasoning."""
        mock_run.return_value.stdout = "feat: feature 1\nfeat: feature 2\nfix: bug\n"
        mock_run.return_value.returncode = 0

        analyzer = CommitAnalyzer(git_repository)
        bump_type, reasoning = analyzer.get_suggested_bump("v1.0.0")

        assert bump_type == BumpType.MINOR
        assert "2 feature(s)" in reasoning
        assert "1 fix(es)" in reasoning

    def test_format_analysis_report(self, git_repository):
        """Test formatting analysis report."""
        from semvx.core.commit_analyzer import CommitAnalysis

        analysis = CommitAnalysis(
            bump_type=BumpType.MINOR,
            commit_count=5,
            major_commits=[],
            minor_commits=["feat: feature 1", "feat: feature 2"],
            patch_commits=["fix: bug"],
            dev_commits=[],
            ignored_commits=["doc: update"]
        )

        analyzer = CommitAnalyzer(git_repository)
        report = analyzer.format_analysis_report(analysis)

        assert "MINOR" in report
        assert "Features (2)" in report
        assert "Fixes (1)" in report
