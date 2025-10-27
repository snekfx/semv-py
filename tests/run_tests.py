#!/usr/bin/env python3
"""
Simple test runner for SEMVX tests without requiring pytest installation.
This validates our test structure and basic functionality.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def run_basic_tests():
    """Run basic tests to validate functionality."""
    print("Running SEMVX Basic Tests")
    print("=" * 60)

    # Test imports
    print("\n1. Testing imports...")
    try:
        from semvx.detection.detector import (
            compare_semver,
            get_highest_version,
            get_repository_context,
            normalize_semver,
        )

        print("   ✅ Detection module imports successful")
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        return False

    try:
        from semvx.cli.main import main  # noqa: F401

        print("   ✅ CLI module imports successful")
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        return False

    # Test semver functions
    print("\n2. Testing semver utilities...")
    test_cases = [
        (normalize_semver("1.2.3"), "v1.2.3", "normalize without v prefix"),
        (normalize_semver("v1.2.3"), "v1.2.3", "normalize with v prefix"),
        (normalize_semver("1.2"), "v1.2.0", "normalize incomplete version"),
        (compare_semver("1.2.3", "1.2.4"), -1, "compare lower version"),
        (compare_semver("2.0.0", "1.9.9"), 1, "compare higher version"),
        (compare_semver("1.2.3", "1.2.3"), 0, "compare equal versions"),
    ]

    all_passed = True
    for actual, expected, description in test_cases:
        if actual == expected:
            print(f"   ✅ {description}: {actual}")
        else:
            print(f"   ❌ {description}: expected {expected}, got {actual}")
            all_passed = False

    # Test version selection
    print("\n3. Testing version selection...")
    versions = ["1.2.3", "2.0.0", "1.9.9", "2.0.1"]
    highest = get_highest_version(versions)
    if highest == "v2.0.1":
        print(f"   ✅ Highest version: {highest}")
    else:
        print(f"   ❌ Expected v2.0.1, got {highest}")
        all_passed = False

    # Test repository context
    print("\n4. Testing repository context detection...")
    try:
        repo_path = Path.cwd()
        context = get_repository_context(repo_path)
        print(f"   ✅ Repository type: {context['repository']['type']}")
        print(f"   ✅ Projects found: {len(context['projects'])}")
        for project in context["projects"]:
            print(f"      - {project['type']}: {project.get('version', 'N/A')}")
    except Exception as e:
        print(f"   ❌ Context detection failed: {e}")
        all_passed = False

    # Test CLI help
    print("\n5. Testing CLI functionality...")
    from io import StringIO
    from unittest.mock import patch

    # Test help output
    with patch("sys.stdout", new=StringIO()) as fake_out:
        with patch.object(sys, "argv", ["semvx", "--help"]):
            try:
                main()
                output = fake_out.getvalue()
                if "USAGE:" in output and "COMMANDS:" in output:
                    print("   ✅ Help command works")
                else:
                    print("   ❌ Help output incomplete")
                    all_passed = False
            except SystemExit:
                pass  # --help causes exit, that's ok

    # Test version output
    with patch("sys.stdout", new=StringIO()) as fake_out:
        with patch.object(sys, "argv", ["semvx", "--version"]):
            main()
            output = fake_out.getvalue()
            if "3.0.0-dev" in output:
                print("   ✅ Version command works")
            else:
                print("   ❌ Version output incorrect")
                all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All basic tests passed!")
        return True
    else:
        print("❌ Some tests failed. Check output above.")
        return False


if __name__ == "__main__":
    success = run_basic_tests()
    sys.exit(0 if success else 1)
