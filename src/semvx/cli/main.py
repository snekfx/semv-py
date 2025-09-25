#!/usr/bin/env python3
"""
SEMVX - Semantic Version Manager CLI
Main entry point for the semvx command.
"""

import sys
from pathlib import Path
from semvx.detection.detector import get_repository_context


def main():
    """Main CLI entry point."""
    if len(sys.argv) > 1 and sys.argv[1] in ["--version", "-v"]:
        print("semvx 3.0.0-dev (Python rewrite)")
        return

    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        print_help()
        return

    if len(sys.argv) > 1 and sys.argv[1] == "detect":
        do_detection()
        return

    print("semvx 3.0.0-dev - Semantic Version Manager (Python Edition)")
    print("Basic CLI stub - full functionality coming soon!")
    print("Use 'semvx --help' for usage information.")


def print_help():
    """Print help message."""
    print("""
semvx 3.0.0-dev - Semantic Version Manager (Python Edition)

USAGE:
    semvx [COMMAND] [OPTIONS]

COMMANDS:
    detect              Detect project types and versions in current directory
    --version, -v       Show version information
    --help, -h          Show this help message

EXAMPLES:
    semvx detect        # Analyze current directory for projects
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


if __name__ == "__main__":
    main()