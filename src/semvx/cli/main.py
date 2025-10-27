#!/usr/bin/env python3
"""
SEMVX - Semantic Version Manager CLI
Main entry point for the semvx command.
"""

import os
import subprocess
import sys
from pathlib import Path

from semvx.core.build_info import BuildInfo
from semvx.core.commit_analyzer import CommitAnalyzer
from semvx.core.file_writer import FileWriteError, VersionFileWriter
from semvx.core.git_ops import GitError, GitRepository, GitVersionTagger
from semvx.core.repository_status import RepositoryAnalyzer
from semvx.core.version import SemanticVersion, VersionParseError
from semvx.detection.detector import get_repository_context
from semvx.integrations.boxy import (
    format_status_as_data,
    format_status_for_boxy,
    render_with_boxy,
    should_use_boxy,
)
from semvx.integrations.rolo import format_as_table, is_rolo_available


def main():
    """Main CLI entry point."""
    # Parse global flags
    view_mode = None
    args = []

    for arg in sys.argv[1:]:
        if arg.startswith("--view="):
            view_mode = arg.split("=", 1)[1]
            os.environ["SEMVX_VIEW"] = view_mode
        else:
            args.append(arg)

    # Reconstruct argv without global flags
    sys.argv = [sys.argv[0]] + args

    if len(sys.argv) > 1 and sys.argv[1] in ["--version", "-v"]:
        print("semvx 3.0.0-dev (Python rewrite)")
        return

    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        print_help()
        return

    # Project detection commands
    if len(sys.argv) > 1 and sys.argv[1] == "detect":
        do_detection()
        return

    if len(sys.argv) > 1 and sys.argv[1] == "status":
        do_status()
        return

    # Version management commands
    if len(sys.argv) > 1 and sys.argv[1] == "bump":
        do_bump_command()
        return

    if len(sys.argv) > 1 and sys.argv[1] == "version":
        do_version_command()
        return

    if len(sys.argv) > 1 and sys.argv[1] == "tag":
        do_tag_command()
        return

    if len(sys.argv) > 1 and sys.argv[1] == "tags":
        do_tags_list_command()
        return

    if len(sys.argv) > 1 and sys.argv[1] in ["next", "dry"]:
        do_next_command()
        return

    if len(sys.argv) > 1 and sys.argv[1] == "get":
        do_get_command()
        return

    if len(sys.argv) > 1 and sys.argv[1] == "set":
        do_set_command()
        return

    if len(sys.argv) > 1 and sys.argv[1] == "sync":
        do_sync_command()
        return

    if len(sys.argv) > 1 and sys.argv[1] in ["bc", "build-count"]:
        do_build_count_command()
        return

    if len(sys.argv) > 1 and sys.argv[1] == "build":
        do_build_command()
        return

    if len(sys.argv) > 1 and sys.argv[1] == "fetch":
        do_fetch_command()
        return

    if len(sys.argv) > 1 and sys.argv[1] == "remote":
        do_remote_command()
        return

    if len(sys.argv) > 1 and sys.argv[1] in ["upst", "upstream"]:
        do_upstream_command()
        return

    if len(sys.argv) > 1 and sys.argv[1] == "validate":
        do_validate_command()
        return

    if len(sys.argv) > 1 and sys.argv[1] == "audit":
        do_audit_command()
        return

    if len(sys.argv) > 1 and sys.argv[1] == "pre-commit":
        do_precommit_command()
        return

    # Default help message
    print("semvx 3.0.0-dev - Semantic Version Manager (Python Edition)")
    print("Use 'semvx --help' for usage information.")


def print_help():
    """Print help message."""
    print(
        """
semvx 3.0.0-dev - Semantic Version Manager (Python Edition)

USAGE:
    semvx [COMMAND] [OPTIONS]

COMMANDS:
    detect              Detect project types and versions in current directory
    status              Show current version status for all projects
    next                Calculate next version based on commit analysis (dry run)
    get [TYPE]          Get version from project files (all|rust|js|python|bash)
    set TYPE VER [FILE] Set version in project files
    sync [FILE]         Synchronize versions across all project files
    bc                  Show current build count (total commits)
    build [FILE]        Generate build info file (default: .build_info)
    fetch               Fetch remote tags
    remote              Show latest remote semver tag
    upst                Compare local vs remote semver (upstream)
    validate            Validate version consistency across files
    audit               Comprehensive repository and version audit
    pre-commit          Pre-commit validation checks
    bump [TYPE]         Bump version (major|minor|patch) with --dry-run support
    version             Display current project versions with details
    tag [VERSION]       Create git tag for version (uses current if omitted)
    tags                List all version tags in repository
    --version, -v       Show version information
    --help, -h          Show this help message

GLOBAL FLAGS:
    --view=MODE         Output format: normal | data
                        - normal: Human-readable with boxy (default)
                        - data: Machine-readable JSON for AI agents

EXAMPLES:
    semvx detect                # Analyze current directory for projects
    semvx status                # Show version status for all detected projects
    semvx status --view=data    # Get status as JSON for AI agents
    semvx next                  # Calculate next version (dry run)
    semvx next --verbose        # Show detailed commit analysis
    semvx get all               # Show all detected version sources
    semvx get python            # Show Python version
    semvx set python 2.1.0      # Set Python version to 2.1.0
    semvx sync                  # Sync all versions to highest found
    semvx bc                    # Show current build count
    semvx build                 # Generate .build_info file
    semvx build build.txt       # Generate custom build file
    semvx fetch                 # Fetch remote tags
    semvx remote                # Show latest remote tag
    semvx upst                  # Compare local vs remote
    semvx validate              # Check version consistency
    semvx audit                 # Full repository audit
    semvx pre-commit            # Run pre-commit checks
    semvx bump patch --dry-run  # Preview patch version bump
    semvx bump minor            # Bump minor version and update files
    semvx version               # Show detailed version information
    semvx tag                   # Create git tag for current version
    semvx tags                  # List all version tags
    semvx --version             # Show semvx version

ENVIRONMENT VARIABLES:
    SEMVX_VIEW          Same as --view flag (normal|data)
    SEMVX_USE_BOXY      Enable/disable boxy (true|false, default: true)

NOTE: This is the Python rewrite of SEMV with namespace separation.
      The original bash semv remains available separately.

For detailed documentation: docs/procs/PROCESS.md
"""
    )


def do_detection():
    """Perform project detection in current directory."""
    try:
        repo_path = Path.cwd()
        context = get_repository_context(repo_path)

        print(f"Repository Analysis: {repo_path}")
        print(f"Repository Type: {context['repository']['type']}")
        print(f"Projects Found: {len(context['projects'])}")

        for i, project in enumerate(context["projects"], 1):
            print(f"  {i}. {project['type']}")
            if project.get("version_file"):
                print(f"     Version File: {project['version_file']}")
            if project.get("version"):
                print(f"     Version: {project['version']}")

        if context["validation"]:
            print("Validation Results:")
            for proj_type, result in context["validation"].items():
                status = "✅ OK" if result.get("ok") else f"❌ {result.get('reason', 'FAIL')}"
                print(f"  {proj_type}: {status}")

    except Exception as e:
        print(f"Error during detection: {e}", file=sys.stderr)
        sys.exit(1)


def do_status():
    """Show comprehensive repository status (dashboard view)."""
    try:
        repo_path = Path.cwd()

        # Check if it's a git repository
        try:
            analyzer = RepositoryAnalyzer(repo_path)
            status = analyzer.get_status()
        except GitError:
            print("❌ Not a git repository")
            sys.exit(1)

        # Convert status to dictionary for formatting
        status_data = {
            "user": status.user,
            "repo_name": status.repo_name,
            "current_branch": status.current_branch,
            "main_branch": status.main_branch,
            "changed_files": status.changed_files,
            "local_build": status.local_build,
            "remote_build": status.remote_build,
            "days_since_last": status.days_since_last,
            "last_commit_msg": status.last_commit_msg,
            "last_tag": status.last_tag,
            "release_tag": status.release_tag,
            "current_version": status.current_version,
            "next_version": status.next_version,
            "package_version": status.package_version,
            "pending_actions": status.pending_actions,
        }

        # Check view mode
        view_mode = os.environ.get("SEMVX_VIEW", "normal")

        if view_mode == "data":
            # Machine-readable output for AI agents
            print(format_status_as_data(status_data))
        elif should_use_boxy():
            # Use boxy for enhanced visual output
            content = format_status_for_boxy(status_data)
            boxed = render_with_boxy(content, theme="info")
            print(boxed)
        else:
            # Fallback to plain text (for compatibility)
            content = format_status_for_boxy(status_data)
            print(content)

    except Exception as e:
        print(f"❌ Error getting status: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


def do_bump_command():
    """Bump version for detected projects."""
    # Parse arguments
    bump_type = "patch"  # default
    dry_run = False

    for arg in sys.argv[2:]:
        if arg in ["major", "minor", "patch"]:
            bump_type = arg
        elif arg in ["--dry-run", "-n"]:
            dry_run = True
        elif arg in ["--help", "-h"]:
            print_bump_help()
            return

    try:
        repo_path = Path.cwd()
        context = get_repository_context(repo_path)

        if not context["projects"]:
            print("❌ No projects detected in current directory.")
            print("Run 'semvx detect' to see what can be detected.")
            sys.exit(1)

        print(f"🔧 Bumping {bump_type} version{' (DRY RUN)' if dry_run else ''}...")
        print("=" * 60)

        for project in context["projects"]:
            proj_type = project["type"]
            current_version = project.get("version", "v0.0.0")

            try:
                # Parse current version
                sem_ver = SemanticVersion.parse(current_version)

                # Bump version
                if bump_type == "major":
                    new_ver = sem_ver.bump_major()
                elif bump_type == "minor":
                    new_ver = sem_ver.bump_minor()
                else:  # patch
                    new_ver = sem_ver.bump_patch()

                # Display change
                print(f"\n📦 {proj_type.upper()} Project:")
                print(f"   Current:  {sem_ver}")
                print(f"   New:      {new_ver}")

                version_file = project.get("version_file", "N/A")
                print(f"   File:     {version_file}")

                if not dry_run:
                    # Actually write the file
                    try:
                        file_path = repo_path / version_file
                        success, message = VersionFileWriter.update_version_in_file(
                            file_path, new_ver, backup=True
                        )
                        if success:
                            print(f"   Status:   ✅ {message}")
                        else:
                            print(f"   Status:   ⚠️  {message}")
                    except FileWriteError as fe:
                        print(f"   Status:   ❌ Error: {fe}")
                else:
                    print("   Status:   ✅ Dry run - no changes made")

            except VersionParseError as e:
                print(f"\n❌ {proj_type.upper()}: Failed to parse version '{current_version}'")
                print(f"   Error: {e}")

        print("\n" + "=" * 60)
        if dry_run:
            print("✅ Dry run complete - no files were modified")
        else:
            print("✅ Version bump complete!")
            print("💡 Tip: Use --dry-run to preview changes before applying")

    except Exception as e:
        print(f"❌ Error during version bump: {e}", file=sys.stderr)
        sys.exit(1)


def print_bump_help():
    """Print help for bump command."""
    print(
        """
semvx bump - Bump semantic version

USAGE:
    semvx bump [TYPE] [OPTIONS]

TYPES:
    major               Bump major version (X.0.0)
    minor               Bump minor version (x.Y.0)
    patch               Bump patch version (x.y.Z) [default]

OPTIONS:
    --dry-run, -n       Preview changes without modifying files
    --help, -h          Show this help message

EXAMPLES:
    semvx bump                  # Bump patch version (1.2.3 → 1.2.4)
    semvx bump minor            # Bump minor version (1.2.3 → 1.3.0)
    semvx bump major --dry-run  # Preview major bump (1.2.3 → 2.0.0)

NOTE: Currently supports version calculation. File writing coming soon.
"""
    )


def do_version_command():
    """Display current version information."""
    try:
        repo_path = Path.cwd()
        context = get_repository_context(repo_path)

        if not context["projects"]:
            print("No projects detected in current directory.")
            return

        print("📋 Project Versions")
        print("=" * 60)

        for project in context["projects"]:
            proj_type = project["type"]
            version = project.get("version", "N/A")
            version_file = project.get("version_file", "N/A")

            print(f"\n{proj_type.upper()}:")
            print(f"  Version: {version}")
            print(f"  File:    {version_file}")

            # Try to parse and show details
            if version != "N/A":
                try:
                    sem_ver = SemanticVersion.parse(version)
                    print(f"  Parsed:  {sem_ver.major}.{sem_ver.minor}.{sem_ver.patch}")
                    if sem_ver.prerelease:
                        print(f"  Pre-release: {sem_ver.prerelease}")
                    if sem_ver.build_metadata:
                        print(f"  Build: {sem_ver.build_metadata}")
                except VersionParseError:
                    print("  ⚠️  Invalid semantic version format")

        print("\n" + "=" * 60)

    except Exception as e:
        print(f"Error getting version info: {e}", file=sys.stderr)
        sys.exit(1)


def do_tag_command():
    """Create a git tag for the current version."""
    # Parse arguments
    force = False
    tag_version = None

    for arg in sys.argv[2:]:
        if arg in ["--force", "-f"]:
            force = True
        elif arg in ["--help", "-h"]:
            print_tag_help()
            return
        elif not arg.startswith("-"):
            tag_version = arg

    try:
        repo_path = Path.cwd()

        # Initialize git repository
        try:
            git_repo = GitRepository(repo_path)
        except GitError as e:
            print(f"❌ Not a git repository: {repo_path}")
            print(f"   Error: {e}")
            sys.exit(1)

        # Get project context
        context = get_repository_context(repo_path)

        if not context["projects"]:
            print("❌ No projects detected in current directory.")
            sys.exit(1)

        # Determine version to tag
        if tag_version:
            # User specified version
            try:
                version = SemanticVersion.parse(tag_version)
            except VersionParseError as e:
                print(f"❌ Invalid version format: {tag_version}")
                print(f"   Error: {e}")
                sys.exit(1)
        else:
            # Use current project version
            project = context["projects"][0]
            current_version = project.get("version", "v0.0.0")
            try:
                version = SemanticVersion.parse(current_version)
            except VersionParseError:
                print(f"❌ Cannot parse current version: {current_version}")
                sys.exit(1)

        # Create the tag
        print(f"🏷️  Creating git tag for version {version}...")

        success, message = GitVersionTagger.create_version_tag(
            git_repo, version, prefix="v", message=f"Release {version}", force=force
        )

        if success:
            print(f"✅ {message}")
            print(f"   Tag: v{version}")
            print(f"   Branch: {git_repo.get_current_branch()}")
        else:
            print(f"❌ {message}")
            if "already exists" in message and not force:
                print("   💡 Use --force to overwrite existing tag")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error creating tag: {e}", file=sys.stderr)
        sys.exit(1)


def print_tag_help():
    """Print help for tag command."""
    print(
        """
semvx tag - Create git tag for version

USAGE:
    semvx tag [VERSION] [OPTIONS]

ARGUMENTS:
    VERSION             Optional version to tag (uses current project version if omitted)

OPTIONS:
    --force, -f         Force tag creation (overwrite existing)
    --help, -h          Show this help message

EXAMPLES:
    semvx tag                   # Tag current project version
    semvx tag 1.2.3             # Tag specific version
    semvx tag 2.0.0 --force     # Force create tag (overwrite)

NOTE: Creates annotated git tags with format 'vX.Y.Z'
"""
    )


def do_tags_list_command():
    """List all version tags in the repository."""
    try:
        repo_path = Path.cwd()

        try:
            git_repo = GitRepository(repo_path)
        except GitError:
            print("❌ Not a git repository")
            sys.exit(1)

        print("🏷️  Version Tags")
        print("=" * 60)

        version_tags = GitVersionTagger.get_version_tags(git_repo)

        if not version_tags:
            print("No version tags found.")
            print("\n💡 Create a tag with: semvx tag")
        else:
            for tag in sorted(version_tags, reverse=True):
                print(f"  {tag}")
            print(f"\nTotal: {len(version_tags)} version tag(s)")

        print("=" * 60)

    except Exception as e:
        print(f"❌ Error listing tags: {e}", file=sys.stderr)
        sys.exit(1)


def do_build_count_command():
    """Show current build count (total commits)."""
    try:
        repo_path = Path.cwd()

        # Initialize git repository
        try:
            git_repo = GitRepository(repo_path)
        except GitError:
            print("❌ Not a git repository")
            sys.exit(1)

        try:
            # Get build count and commit info
            build_count = BuildInfo.get_build_count(repo_path)
            commit_hash = BuildInfo.get_commit_hash(repo_path, short=True)

            print("🔧 Build Information")
            print("=" * 60)
            print(f"Build Count: {build_count}")
            print(f"Commit:      {commit_hash}")

            # Show build count since last tag if available
            latest_tag = git_repo.get_latest_tag()
            if latest_tag:
                try:
                    count_since_tag = BuildInfo.get_build_count(repo_path, since_tag=latest_tag)
                    print(f"Since {latest_tag}: {count_since_tag} commit(s)")
                except GitError:
                    pass

            print("=" * 60)

        except GitError as e:
            print(f"❌ Error getting build count: {e}")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def do_build_command():
    """Generate build information file."""
    try:
        repo_path = Path.cwd()

        # Initialize git repository
        try:
            git_repo = GitRepository(repo_path)
        except GitError:
            print("❌ Not a git repository")
            sys.exit(1)

        # Get output filename
        output_file = ".build_info"
        if len(sys.argv) > 2:
            output_file = sys.argv[2]

        # Get current version from repository context
        context = get_repository_context(repo_path)
        version = "unknown"

        # Try to get version from projects or git tags
        if context["projects"]:
            # Use first project version
            version = context["projects"][0].get("version", "unknown")

        if version == "unknown" or version == "N/A":
            # Fall back to git tag
            latest_tag = git_repo.get_latest_tag()
            if latest_tag:
                version = latest_tag

        try:
            # Generate build file
            output_path = BuildInfo.generate_build_file(
                repo_path, version=version, output_file=output_file
            )

            print("🔧 Build File Generated")
            print("=" * 60)
            print(f"File:    {output_path}")
            print(f"Version: {version}")

            # Show build count
            build_count = BuildInfo.get_build_count(repo_path)
            commit_hash = BuildInfo.get_commit_hash(repo_path, short=True)
            print(f"Build:   {build_count}")
            print(f"Commit:  {commit_hash}")
            print("=" * 60)

        except GitError as e:
            print(f"❌ Error generating build file: {e}")
            sys.exit(1)
        except OSError as e:
            print(f"❌ Error writing build file: {e}")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def do_fetch_command():
    """Fetch remote tags."""
    try:
        repo_path = Path.cwd()

        # Initialize git repository
        try:
            git_repo = GitRepository(repo_path)
        except GitError:
            print("❌ Not a git repository")
            sys.exit(1)

        # Check if remote exists
        if not git_repo.has_remote():
            print("❌ No remote repository configured")
            sys.exit(1)

        # Fetch tags
        print("🔄 Fetching remote tags...")
        success, message = git_repo.fetch_tags()

        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def do_remote_command():
    """Show latest remote semver tag."""
    try:
        repo_path = Path.cwd()

        # Initialize git repository
        try:
            git_repo = GitRepository(repo_path)
        except GitError:
            print("❌ Not a git repository")
            sys.exit(1)

        # Check if remote exists
        if not git_repo.has_remote():
            print("❌ No remote repository configured")
            sys.exit(1)

        try:
            remote_tag = git_repo.get_remote_latest_tag()

            print("🌐 Remote Version Information")
            print("=" * 60)

            if remote_tag:
                print(f"Latest Remote Tag: {remote_tag}")

                # Compare with local
                local_tag = git_repo.get_latest_tag()
                if local_tag:
                    print(f"Latest Local Tag:  {local_tag}")

                    status, message = git_repo.compare_with_remote(local_tag, remote_tag)

                    if status == "ahead":
                        print(f"\n✅ {message}")
                    elif status == "behind":
                        print(f"\n⚠️  {message}")
                    elif status == "equal":
                        print(f"\n✅ {message}")
                    else:
                        print(f"\n❓ {message}")
                else:
                    print("Latest Local Tag:  (none)")
                    print("\n⚠️  No local tags found")
            else:
                print("Latest Remote Tag: (none)")
                print("\n❓ No remote tags found")

            print("=" * 60)

        except GitError as e:
            print(f"❌ Error getting remote tags: {e}")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def do_upstream_command():
    """Compare local vs remote semver."""
    try:
        repo_path = Path.cwd()

        # Initialize git repository
        try:
            git_repo = GitRepository(repo_path)
        except GitError:
            print("❌ Not a git repository")
            sys.exit(1)

        # Check if remote exists
        if not git_repo.has_remote():
            print("❌ No remote repository configured")
            sys.exit(1)

        try:
            local_tag = git_repo.get_latest_tag()
            remote_tag = git_repo.get_remote_latest_tag()

            print("🔄 Upstream Comparison")
            print("=" * 60)
            print(f"Local:  {local_tag if local_tag else '(none)'}")
            print(f"Remote: {remote_tag if remote_tag else '(none)'}")
            print("=" * 60)

            if not local_tag and not remote_tag:
                print("❓ No tags found locally or remotely")
            elif not local_tag:
                print("⚠️  No local tags - remote is ahead")
            elif not remote_tag:
                print("✅ No remote tags - local is ahead")
            else:
                status, message = git_repo.compare_with_remote(local_tag, remote_tag)

                if status == "ahead":
                    print(f"✅ {message}")
                    print("\n💡 You can push your tags with: git push --tags")
                elif status == "behind":
                    print(f"⚠️  {message}")
                    print("\n💡 You can fetch tags with: semvx fetch")
                elif status == "equal":
                    print(f"✅ {message}")
                else:
                    print(f"❓ {message}")

        except GitError as e:
            print(f"❌ Error comparing with remote: {e}")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def do_validate_command():
    """Validate version consistency across files."""
    try:
        repo_path = Path.cwd()
        context = get_repository_context(repo_path)

        print("🔍 Version Validation")
        print("=" * 60)

        if not context["projects"]:
            print("❌ No projects detected")
            sys.exit(1)

        # Collect all versions
        versions = {}
        for project in context["projects"]:
            proj_type = project["type"]
            version = project.get("version", "N/A")
            version_file = project.get("version_file", "N/A")

            if version != "N/A":
                if version not in versions:
                    versions[version] = []
                versions[version].append((proj_type, version_file))

        # Check git tag
        try:
            git_repo = GitRepository(repo_path)
            latest_tag = git_repo.get_latest_tag()
            if latest_tag:
                print(f"Git Tag: {latest_tag}")
                if latest_tag not in versions:
                    versions[latest_tag] = [("git", "tags")]
        except GitError:
            latest_tag = None

        # Report findings
        if len(versions) == 0:
            print("\n❌ No versions found")
            sys.exit(1)
        elif len(versions) == 1:
            version = list(versions.keys())[0]
            print(f"\n✅ All versions consistent: {version}")
            print("\nSources:")
            for proj_type, file in versions[version]:
                print(f"  - {proj_type}: {file}")
        else:
            print(f"\n⚠️  Version drift detected! Found {len(versions)} different versions:")
            for version, sources in sorted(versions.items()):
                print(f"\n  {version}:")
                for proj_type, file in sources:
                    print(f"    - {proj_type}: {file}")
            print("\n💡 Run 'semvx sync' to synchronize versions")
            sys.exit(1)

        print("=" * 60)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def do_audit_command():
    """Comprehensive repository and version audit."""
    try:
        repo_path = Path.cwd()

        print("📊 Repository Audit")
        print("=" * 60)

        # Git repository info
        git_data = []
        try:
            git_repo = GitRepository(repo_path)

            branch = git_repo.get_current_branch()
            latest_tag = git_repo.get_latest_tag() or "(none)"
            build_count = BuildInfo.get_build_count(repo_path)
            commit_hash = BuildInfo.get_commit_hash(repo_path, short=True)

            git_data.append(["Branch", branch])
            git_data.append(["Latest Tag", latest_tag])
            git_data.append(["Build Count", str(build_count)])
            git_data.append(["Commit", commit_hash])

            # Remote info
            if git_repo.has_remote():
                try:
                    remote_tag = git_repo.get_remote_latest_tag()
                    if remote_tag:
                        git_data.append(["Remote Tag", remote_tag])
                        if latest_tag != "(none)":
                            status, _ = git_repo.compare_with_remote(latest_tag, remote_tag)
                            git_data.append(["Status", status])
                except GitError:
                    git_data.append(["Remote Tag", "(error fetching)"])
            else:
                git_data.append(["Remote", "(none configured)"])

        except GitError as e:
            print(f"\n⚠️  Not a git repository: {e}")
            git_data = []

        # Display git info as table
        if git_data:
            print("\n🌿 Git Information:")
            if is_rolo_available():
                table = format_as_table(git_data, border="none", align="left,left")
                # Indent the table
                print("\n".join(f"  {line}" for line in table.split("\n")))
            else:
                for key, value in git_data:
                    print(f"  {key}: {value}")

        # Project detection
        context = get_repository_context(repo_path)

        print(f"\n📦 Projects Detected: {len(context['projects'])}")

        if context["projects"] and is_rolo_available():
            # Format projects as table
            project_data = []
            for project in context["projects"]:
                proj_type = project["type"].upper()
                version = project.get("version", "N/A")
                version_file = project.get("version_file", "N/A")
                project_data.append([proj_type, version, version_file])

            table = format_as_table(
                project_data,
                headers=["Type", "Version", "File"],
                border="ascii",
                align="left,left,left",
            )
            print()
            print(table)
        else:
            for project in context["projects"]:
                proj_type = project["type"]
                version = project.get("version", "N/A")
                version_file = project.get("version_file", "N/A")

                print(f"\n  {proj_type.upper()}:")
                print(f"    Version: {version}")
                print(f"    File: {version_file}")

        # Version consistency check
        versions = set()
        for project in context["projects"]:
            version = project.get("version")
            if version and version != "N/A":
                versions.add(version)

        print("\n🔍 Version Analysis:")
        if len(versions) == 0:
            print("  Status: ⚠️  No versions found")
        elif len(versions) == 1:
            print(f"  Status: ✅ Consistent ({list(versions)[0]})")
        else:
            print(f"  Status: ⚠️  Drift detected ({len(versions)} different versions)")

        # Commit analysis
        try:
            if latest_tag and latest_tag != "(none)":
                analyzer = CommitAnalyzer(repo_path)
                bump_type, reasoning = analyzer.get_suggested_bump(latest_tag)

                print("\n📋 Commit Analysis:")
                print(f"  Suggested Bump: {bump_type.value.upper()}")
                print(f"  Reason: {reasoning}")
        except Exception:
            pass

        print("\n" + "=" * 60)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def do_precommit_command():
    """Pre-commit validation checks."""
    try:
        repo_path = Path.cwd()

        print("🔒 Pre-Commit Validation")
        print("=" * 60)

        issues = []
        warnings = []

        # Check 1: Git repository
        try:
            git_repo = GitRepository(repo_path)
        except GitError:
            issues.append("Not a git repository")
            print("\n❌ Not a git repository")
            print("=" * 60)
            sys.exit(1)

        # Check 2: Version consistency
        context = get_repository_context(repo_path)

        if not context["projects"]:
            warnings.append("No projects detected")
        else:
            versions = set()
            for project in context["projects"]:
                version = project.get("version")
                if version and version != "N/A":
                    versions.add(version)

            if len(versions) > 1:
                issues.append(f"Version drift: {len(versions)} different versions found")
            elif len(versions) == 1:
                print(f"\n✅ Version consistency: {list(versions)[0]}")

        # Check 3: Git tag vs project version
        latest_tag = git_repo.get_latest_tag()
        if latest_tag and context["projects"]:
            project_version = context["projects"][0].get("version", "N/A")
            if project_version != "N/A" and project_version != latest_tag:
                # Parse and compare
                try:
                    tag_ver = SemanticVersion.parse(latest_tag)
                    proj_ver = SemanticVersion.parse(project_version)

                    if proj_ver > tag_ver:
                        print(f"✅ Project version ahead of tag: {project_version} > {latest_tag}")
                    elif proj_ver == tag_ver:
                        print(f"✅ Project version matches tag: {project_version}")
                    else:
                        warnings.append(
                            f"Project version behind tag: {project_version} < {latest_tag}"
                        )
                except VersionParseError:
                    warnings.append(
                        f"Version mismatch: project={project_version}, tag={latest_tag}"
                    )

        # Check 4: Uncommitted changes (optional warning)
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            if result.stdout.strip():
                changes = len(result.stdout.strip().split("\n"))
                print(f"\n📝 Uncommitted changes: {changes} file(s)")
        except subprocess.CalledProcessError:
            pass

        # Summary
        print("\n" + "=" * 60)

        if issues:
            print(f"\n❌ {len(issues)} issue(s) found:")
            for issue in issues:
                print(f"  - {issue}")
            print("\n💡 Fix these issues before committing")
            sys.exit(1)
        elif warnings:
            print(f"\n⚠️  {len(warnings)} warning(s):")
            for warning in warnings:
                print(f"  - {warning}")
            print("\n✅ Pre-commit checks passed (with warnings)")
        else:
            print("\n✅ All pre-commit checks passed!")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
