#!/usr/bin/env python3
"""
SEMVX - Semantic Version Manager CLI
Main entry point for the semvx command.
"""

import sys
from pathlib import Path
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from semvx.detection.detector import get_repository_context


def main():
    """Main CLI entry point."""
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

    # Version management commands (stubs for now)
    if len(sys.argv) > 1 and sys.argv[1] in ["bump", "version"]:
        do_version_command()
        return

    if len(sys.argv) > 1 and sys.argv[1] == "tag":
        do_tag_command()
        return

    # Default help message
    print("semvx 3.0.0-dev - Semantic Version Manager (Python Edition)")
    print("Use 'semvx --help' for usage information.")


def print_help():
    """Print help message."""
    print("""
semvx 3.0.0-dev - Semantic Version Manager (Python Edition)

USAGE:
    semvx [COMMAND] [OPTIONS]

COMMANDS:
    detect              Detect project types and versions in current directory
    status              Show current version status for all projects
    bump [TYPE]         Bump version (major|minor|patch) - COMING SOON
    version             Display current project versions - COMING SOON
    tag                 Create version tags in git - COMING SOON
    --version, -v       Show version information
    --help, -h          Show this help message

EXAMPLES:
    semvx detect        # Analyze current directory for projects
    semvx status        # Show version status for all detected projects
    semvx bump minor    # Bump minor version (when implemented)
    semvx tag           # Create git tags (when implemented)
    semvx --version     # Show semvx version

NOTE: This is the Python rewrite of SEMV with namespace separation.
      The original bash semv remains available separately.

For detailed documentation: docs/procs/PROCESS.md
""")


def do_detection():
    """Perform project detection in current directory."""
    try:
        repo_path = Path.cwd()
        context = get_repository_context(repo_path)

        print(f"Repository Analysis: {repo_path}")
        print(f"Repository Type: {context['repository']['type']}")
        print(f"Projects Found: {len(context['projects'])}")

        for i, project in enumerate(context['projects'], 1):
            print(f"  {i}. {project['type']}")
            if project.get('version_file'):
                print(f"     Version File: {project['version_file']}")
            if project.get('version'):
                print(f"     Version: {project['version']}")

        if context['validation']:
            print("Validation Results:")
            for proj_type, result in context['validation'].items():
                status = "✅ OK" if result.get('ok') else f"❌ {result.get('reason', 'FAIL')}"
                print(f"  {proj_type}: {status}")

    except Exception as e:
        print(f"Error during detection: {e}", file=sys.stderr)
        sys.exit(1)


def do_status():
    """Show current version status for all projects."""
    try:
        repo_path = Path.cwd()
        context = get_repository_context(repo_path)

        print(f"🔍 Version Status for {repo_path}")
        print("=" * 60)

        if not context['projects']:
            print("No projects detected in current directory.")
            return

        for project in context['projects']:
            proj_type = project['type']
            version = project.get('version', 'N/A')
            version_file = project.get('version_file', 'N/A')

            # Status emoji based on version availability
            status_icon = "✅" if version != 'N/A' else "❓"

            print(f"\n{status_icon} {proj_type.upper()} Project:")
            print(f"   Version:      {version}")
            print(f"   Version File: {version_file}")

            # Additional metadata if available
            if project.get('name'):
                print(f"   Name:         {project['name']}")

        print("\n" + "=" * 60)
        print(f"Total projects found: {len(context['projects'])}")

    except Exception as e:
        print(f"Error getting status: {e}", file=sys.stderr)
        sys.exit(1)


def do_version_command():
    """Stub for version management commands."""
    command = sys.argv[1]
    if len(sys.argv) > 2:
        subcommand = sys.argv[2]
        print(f"semvx {command} {subcommand}: This feature is coming soon!")
    else:
        print(f"semvx {command}: This feature is coming soon!")
    print("Version management will include:")
    print("  - Semantic version bumping (major, minor, patch)")
    print("  - Pre-release version handling")
    print("  - Multi-project synchronization")
    print("\nFor now, use 'semvx detect' or 'semvx status' to analyze projects.")


def do_tag_command():
    """Stub for tag management commands."""
    print("semvx tag: This feature is coming soon!")
    print("Tag management will include:")
    print("  - Creating semantic version tags")
    print("  - Pushing tags to remote repositories")
    print("  - Tag validation and conflict resolution")
    print("\nFor now, use 'semvx detect' or 'semvx status' to analyze projects.")


if __name__ == "__main__":
    main()