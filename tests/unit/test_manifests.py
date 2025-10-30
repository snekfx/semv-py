"""
Tests for the manifests detection module.
"""

from semvx.detection.manifests import (
    detect_bash_patterns,
    extract_bash_version,
    extract_javascript_version,
    extract_python_version,
    extract_rust_version,
    has_javascript_manifest,
    has_python_manifest,
    has_rust_manifest,
    has_version_comment,
    is_generated_file,
)


class TestManifestDetection:
    """Test language-specific manifest detection."""

    def test_has_rust_manifest_valid(self, tmp_path):
        """Test detection of valid Cargo.toml."""
        cargo_toml = tmp_path / "Cargo.toml"
        cargo_toml.write_text("[package]\nname = 'test'\nversion = '1.0.0'")
        assert has_rust_manifest(tmp_path) is True

    def test_has_rust_manifest_missing(self, tmp_path):
        """Test detection when Cargo.toml is missing."""
        assert has_rust_manifest(tmp_path) is False

    def test_has_javascript_manifest_valid(self, tmp_path):
        """Test detection of valid package.json."""
        package_json = tmp_path / "package.json"
        package_json.write_text('{"name": "test", "version": "1.0.0"}')
        assert has_javascript_manifest(tmp_path) is True

    def test_has_javascript_manifest_no_version(self, tmp_path):
        """Test detection when package.json has no version."""
        package_json = tmp_path / "package.json"
        package_json.write_text('{"name": "test"}')
        assert has_javascript_manifest(tmp_path) is False

    def test_has_python_manifest_pyproject(self, tmp_path):
        """Test detection of pyproject.toml."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'\nversion = '1.0.0'")
        assert has_python_manifest(tmp_path) is True

    def test_has_python_manifest_setup_py(self, tmp_path):
        """Test detection of setup.py."""
        setup_py = tmp_path / "setup.py"
        setup_py.write_text("setup(name='test', version='1.0.0')")
        assert has_python_manifest(tmp_path) is True

    def test_has_python_manifest_missing(self, tmp_path):
        """Test detection when no Python manifests exist."""
        assert has_python_manifest(tmp_path) is False


class TestBashPatternDetection:
    """Test bash project pattern detection."""

    def test_detect_bash_pattern_bashfx_buildsh(self, tmp_path):
        """Test detection of BashFX build.sh pattern."""
        (tmp_path / "build.sh").write_text("#!/bin/bash\necho 'build'")
        (tmp_path / "parts").mkdir()
        assert detect_bash_patterns(tmp_path) == "bashfx-buildsh"

    def test_detect_bash_pattern_standalone(self, tmp_path):
        """Test detection of standalone pattern."""
        script = tmp_path / f"{tmp_path.name}.sh"
        script.write_text("#!/bin/bash\n# version: 1.0.0\necho 'test'")
        assert detect_bash_patterns(tmp_path) == "standalone"

    def test_detect_bash_pattern_generic(self, tmp_path):
        """Test detection of generic pattern."""
        script = tmp_path / "script.sh"
        script.write_text("#!/bin/bash\n# version: 1.0.0\necho 'test'")
        assert detect_bash_patterns(tmp_path) == "generic"

    def test_detect_bash_pattern_none(self, tmp_path):
        """Test when no bash pattern is detected."""
        assert detect_bash_patterns(tmp_path) is None

    def test_has_version_comment_found(self, tmp_path):
        """Test version comment detection."""
        script = tmp_path / "test.sh"
        script.write_text("#!/bin/bash\n# version: 1.0.0\necho 'test'")
        assert has_version_comment(script) is True

    def test_has_version_comment_not_found(self, tmp_path):
        """Test when version comment is missing."""
        script = tmp_path / "test.sh"
        script.write_text("#!/bin/bash\necho 'test'")
        assert has_version_comment(script) is False

    def test_is_generated_file_true(self, tmp_path):
        """Test detection of generated files."""
        script = tmp_path / "generated.sh"
        script.write_text("#!/bin/bash\n# generated\necho 'test'")
        assert is_generated_file(script) is True

    def test_is_generated_file_false(self, tmp_path):
        """Test when file is not generated."""
        script = tmp_path / "manual.sh"
        script.write_text("#!/bin/bash\necho 'test'")
        assert is_generated_file(script) is False


class TestVersionExtraction:
    """Test version extraction from manifest files."""

    def test_extract_rust_version(self, tmp_path):
        """Test extraction from Cargo.toml."""
        cargo_toml = tmp_path / "Cargo.toml"
        cargo_toml.write_text('[package]\nname = "test"\nversion = "1.2.3"')
        assert extract_rust_version(cargo_toml) == "1.2.3"

    def test_extract_javascript_version(self, tmp_path):
        """Test extraction from package.json."""
        package_json = tmp_path / "package.json"
        package_json.write_text('{"name": "test", "version": "1.2.3"}')
        assert extract_javascript_version(package_json) == "1.2.3"

    def test_extract_python_version_pyproject(self, tmp_path):
        """Test extraction from pyproject.toml."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "test"\nversion = "1.2.3"')
        assert extract_python_version(pyproject) == "1.2.3"

    def test_extract_python_version_setup_py(self, tmp_path):
        """Test extraction from setup.py."""
        setup_py = tmp_path / "setup.py"
        setup_py.write_text("setup(name='test', version='1.2.3')")
        assert extract_python_version(setup_py) == "1.2.3"

    def test_extract_bash_version(self, tmp_path):
        """Test extraction from bash script."""
        script = tmp_path / "test.sh"
        script.write_text("#!/bin/bash\n# version: 1.2.3\necho 'test'")
        assert extract_bash_version(script) == "1.2.3"

    def test_extract_version_invalid_file(self, tmp_path):
        """Test extraction from non-existent file."""
        assert extract_rust_version(tmp_path / "missing.toml") is None
