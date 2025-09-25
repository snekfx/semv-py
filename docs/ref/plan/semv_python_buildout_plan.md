# SEMV v3.0.0 Python Buildout Plan - Complete Architecture

### **Project Information**
- **Repository**: https://github.com/snekfx/semv-py
- **Migration Target**: SEMV v2.0.0 (Bash) → SEMV v3.0.0 (Python)
- **Architecture**: Modular Python package with external tool integration
- **Boxy Integration**: Rust-based visual enhancement tool (subprocess calls)

```
semv/
├── __init__.py                  # Package exports and version
├── cli.py                       # Main CLI entry point with Click
├── core/                        # Core business logic
│   ├── __init__.py
│   ├── version.py               # Version parsing & comparison (integrates detection)
│   ├── git.py                   # Git operations (tags, commits, branches)
│   ├── project.py               # Project detection integration (uses detection/)
│   └── config.py                # SEMV configuration & XDG+ environment
├── parsers/                     # Language-specific version read/write operations  
│   ├── __init__.py
│   ├── rust.py                  # Cargo.toml read/write operations
│   ├── javascript.py            # package.json read/write operations
│   ├── python_parser.py         # pyproject.toml/setup.py read/write operations
│   └── bash.py                  # Bash script version comment read/write
├── commands/                    # High-level command implementations
│   ├── __init__.py
│   ├── bump.py                  # Version bumping with commit analysis
│   ├── sync.py                  # Multi-source version synchronization  
│   ├── status.py                # Dashboard and status reporting
│   ├── lifecycle.py             # Install/uninstall/reset operations
│   ├── hooks.py                 # Hook system & workflow automation
│   └── release.py               # Optional release flow system
├── adapters/                    # External tool integration (adapter pattern)
│   ├── __init__.py              # Adapter registry and discovery
│   ├── base.py                  # Abstract adapter interface
│   ├── gitsim.py                # GitSim simulation environment adapter
│   ├── blade.py                 # Blade coordination (JSON output)
│   └── boxy.py                  # Visual output enhancement adapter
├── display/                     # Output formatting and visual theming
│   ├── __init__.py
│   ├── themes.py                # Semantic themes (error, success, warning, info)
│   ├── views.py                 # All output view formatting (consolidated UX)
│   ├── colors.py                # ANSI color management with --no-color support
│   ├── formatter.py             # Output formatting utilities
│   └── logo.py                  # Simple text logo/banner display
├── utils/                       # Shared utilities
│   ├── __init__.py
│   ├── files.py                 # File operations & path management
│   └── validation.py            # Input validation & error handling
└── detection/                   # Our detection system (modules we built)
    ├── __init__.py              # Detection package exports
    ├── core.py                  # Core project detection & semver utilities
    ├── tooling.py               # Standard tools & emerging tools detection
    ├── infrastructure.py        # Gap analysis & infrastructure scoring
    ├── workspace.py             # Workspace/monorepo detection & analysis
    ├── config.py                # .projectrc configuration system
    ├── batch.py                 # Multi-repo processing orchestration
    ├── cache.py                 # XDG+ caching system
    └── export.py                # TSV/JSON export & analysis reporting
```

## **Module Buildout Priority & Timeline**

### **Phase 1: Core Foundation (Week 1-2)**

#### **Week 1: Essential CLI Infrastructure**
1. **`cli.py`** (150 lines)
   - Click-based CLI framework with command routing
   - Global options (debug, quiet, version flags)
   - Command discovery and registration
   - Error handling and exit codes

2. **`core/version.py`** (200 lines)
   - Integration with detection/core.py semver utilities
   - Version parsing, comparison, and normalization
   - SEMV v2.0 label conventions (major:, minor:, patch:, dev:)
   - "Highest version wins" conflict resolution

3. **`core/git.py`** (300 lines)
   - Git repository detection and validation
   - Tag operations (create, list, delete)
   - Commit analysis and message parsing
   - Branch operations and status checking
   - Integration with GitSim adapter

4. **`core/project.py`** (200 lines)
   - Integration with detection/ modules
   - Project context aggregation
   - Version authority determination
   - Multi-language project coordination

#### **Week 2: Configuration & Basic Commands**
5. **`core/config.py`** (250 lines)
   - XDG+ directory structure (`~/.local/etc/fx/semv/`)
   - Environment variable handling
   - Configuration file management
   - Migration from SEMV v2.0.0 settings

6. **`commands/status.py`** (300 lines)
   - Repository status dashboard
   - Project detection summary
   - Version drift analysis
   - Integration with detection system
   - Basic visual output formatting

### **Phase 2: Language Parsers (Week 2-3)**

#### **Language-Specific Read/Write Operations**
7. **`parsers/rust.py`** (200 lines)
   - Cargo.toml parsing and modification
   - Workspace member handling
   - Version field read/write operations
   - Dependency version management

8. **`parsers/javascript.py`** (200 lines)
   - package.json parsing and modification
   - npm workspace support
   - Version field read/write operations
   - Scripts and dependencies handling

9. **`parsers/python_parser.py`** (250 lines)
   - pyproject.toml and setup.py handling
   - Poetry and standard Python packaging
   - Dynamic version detection
   - Version field read/write operations

10. **`parsers/bash.py`** (200 lines)
    - Bash script version comment parsing
    - All 5 BashFX patterns support
    - Generated file protection
    - Version comment read/write operations

### **Phase 3: Core Commands (Week 3-4)**

#### **Essential SEMV Operations**
11. **`commands/bump.py`** (400 lines)
    - Commit message analysis for version bumping
    - Multi-language version synchronization
    - Git tag creation and management
    - --amend workflow integration
    - Dry-run mode and validation

12. **`commands/sync.py`** (300 lines)
    - Cross-language version synchronization
    - Conflict detection and resolution
    - Authority-based version propagation
    - Validation and verification

13. **`utils/files.py`** (150 lines)
    - Atomic file operations
    - Backup and rollback capabilities
    - Path normalization and validation
    - XDG+ directory management

14. **`utils/validation.py`** (200 lines)
    - Input validation and sanitization
    - Error message generation
    - Type checking and conversion
    - Configuration validation

### **Phase 4: Visual Enhancement & Adapters (Week 4-5)**

#### **Enhanced User Experience**
15. **`adapters/base.py`** (100 lines)
    - Abstract adapter interface
    - Adapter registry and discovery
    - Error handling patterns
    - Common adapter utilities

16. **`adapters/boxy.py`** (200 lines)
    - Boxy subprocess integration (Rust binary via subprocess)
    - Theme-based output rendering through external command
    - Graceful fallback to plain text when Boxy unavailable
    - Performance optimization with command caching

17. **`display/colors.py`** (200 lines)
    - ANSI color code management and terminal detection
    - Color mode handling (auto, always, never)
    - --no-color flag support with environment variable fallback
    - Terminal capability detection and graceful degradation

18. **`display/logo.py`** (150 lines)
    - Custom logo loading from .inf/logo.txt with fallback
    - Built-in fallback SEMV text logo/banner
    - Integration with color system for styled banners
    - View mode awareness (no logo in data mode)

19. **`display/themes.py`** (150 lines)
    - Semantic color themes with ANSI support
    - Error, success, warning, info themes
    - Boxy theme definitions with color fallbacks
    - View mode integration (normal vs data output)

20. **`display/views.py`** (350 lines)
    - Consolidated output formatting with view mode support
    - Data mode: machine-readable output (JSON, plain text)
    - Normal mode: styled output with colors and ASCII art
    - Status dashboard rendering with toilet headers
    - Table and list formatting with color support

21. **`display/formatter.py`** (200 lines)
    - Text formatting utilities with color integration
    - Column alignment and wrapping with ANSI-aware width calculation
    - Unicode handling and terminal width detection
    - View mode switching and output sanitization

### **Phase 5: Advanced Features (Week 5-6)**

#### **Integration & Automation**
20. **`adapters/blade.py`** (150 lines)
    - JSON output formatting for Blade
    - Multi-repository coordination
    - Status and detection result serialization
    - CLI integration points

21. **`adapters/gitsim.py`** (200 lines)
    - GitSim environment detection
    - Simulated repository handling
    - Command routing through GitSim
    - Metadata extraction and validation

22. **`commands/lifecycle.py`** (300 lines)
    - Installation and setup operations
    - Uninstall and cleanup procedures
    - Configuration migration
    - System integration (PATH, hooks)

23. **`commands/hooks.py`** (250 lines)
    - Pre-commit hook installation
    - Git hook management
    - Workflow automation
    - CI/CD integration support

24. **`commands/release.py`** (400 lines)
    - Optional release system
    - Release branch management
    - Version tagging and publishing
    - Release notes generation

## **Key Integration Points**

### **Detection System Integration**
```python
# adapters/boxy.py
import subprocess
import shutil
from typing import Optional, Dict, Any
from .base import AdapterBase

class BoxyAdapter(AdapterBase):
    """Adapter for Boxy (Rust-based visual output tool)"""
    
    def is_available(self) -> bool:
        """Check if boxy command is available in PATH"""
        return shutil.which("boxy") is not None
    
    def render_themed_output(self, theme: str, title: str, content: str) -> str:
        """Render content using Boxy with specified theme"""
        if not self.is_available():
            return self._fallback_render(title, content)
        
        try:
            cmd = ["boxy", "--theme", theme, "--title", title]
            result = subprocess.run(
                cmd, 
                input=content, 
                text=True, 
                capture_output=True, 
                timeout=5
            )
            return result.stdout if result.returncode == 0 else self._fallback_render(title, content)
        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
            return self._fallback_render(title, content)
    
    def _fallback_render(self, title: str, content: str) -> str:
        """Fallback rendering when Boxy is unavailable"""
        return f"\n=== {title} ===\n{content}\n"
```

### **Detection System Integration**
```python
# core/project.py
from ..detection import get_enhanced_detection_with_config, get_repository_context

def get_project_context(repo_path: Path) -> Dict:
    """SEMV's main project detection using our detection system"""
    return get_enhanced_detection_with_config(repo_path)

def get_version_authority(repo_path: Path) -> str:
    """Determine which project type controls versioning"""
    context = get_repository_context(repo_path)
    projects = context.get("projects", [])
    
    # Apply SEMV authority rules
    if len(projects) == 1:
        return projects[0]["type"]
    
    # Prefer manifest files over bash
    manifest_types = [p["type"] for p in projects if p["type"] in ["rust", "javascript", "python"]]
    if manifest_types:
        return manifest_types[0]
    
    return projects[0]["type"] if projects else "unknown"
```

### **Boxy Integration (Rust Tool)**
```python
# cli.py  
import click
from pathlib import Path
from .commands import bump, sync, status, lifecycle
from .core.config import load_semv_config
from .display.themes import setup_theme

@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.option('--debug', '-d', is_flag=True, help='Enable debug output')
@click.option('--quiet', '-q', is_flag=True, help='Quiet mode (errors only)')
@click.option('--version', '-v', is_flag=True, help='Show version and exit')
@click.pass_context
def cli(ctx, debug, quiet, version):
    """SEMV - Semantic Version Manager v3.0.0"""
    if version:
        click.echo("SEMV v3.0.0")
        return
    
    # Setup context
    ctx.ensure_object(dict)
    ctx.obj['debug'] = debug
    ctx.obj['quiet'] = quiet
    ctx.obj['config'] = load_semv_config()
    
    # Setup theming
    setup_theme(debug=debug, quiet=quiet)

# Register commands
cli.add_command(bump.bump)
cli.add_command(sync.sync) 
cli.add_command(status.status)
cli.add_command(lifecycle.install)
cli.add_command(lifecycle.uninstall)

if __name__ == '__main__':
    cli()
```

### **CLI Framework Integration**
```python
# adapters/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class AdapterBase(ABC):
    """Abstract interface for all external tool adapters"""
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if external tool is available and working"""
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get current status/info from external tool"""
        pass
    
    @abstractmethod  
    def handle_error(self, error: Exception) -> Optional[Dict]:
        """Graceful error handling with fallback behavior"""
        pass

# adapters/__init__.py
from .base import AdapterBase
from .boxy import BoxyAdapter
from .gitsim import GitSimAdapter
from .blade import BladeAdapter

# Registry for adapter discovery
AVAILABLE_ADAPTERS = {
    "boxy": BoxyAdapter,
    "gitsim": GitSimAdapter,
    "blade": BladeAdapter
}

def get_adapter(name: str) -> Optional[AdapterBase]:
    """Get adapter instance by name"""
    adapter_class = AVAILABLE_ADAPTERS.get(name)
    if adapter_class:
        adapter = adapter_class()
        return adapter if adapter.is_available() else None
    return None
```

### **Adapter Pattern Implementation**

### **pyproject.toml**
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "semv-py"
version = "3.0.0"
description = "SEMV - Semantic Version Manager for multi-language version synchronization"
readme = "README.md"
license = {text = "MIT"}
authors = [{name = "SnekFX", email = "snekfx@example.com"}]
keywords = ["semver", "versioning", "git", "automation", "rust", "javascript", "python", "bash"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Version Control",
    "Topic :: Software Development :: Build Tools",
    "Environment :: Console"
]
requires-python = ">=3.8"
dependencies = [
    "click>=8.0.0,<9.0.0",
    "packaging>=21.0,<25.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0,<8.0.0",
    "pytest-cov>=4.0.0,<5.0.0",
    "pytest-mock>=3.10.0,<4.0.0",
    "black>=23.0.0,<24.0.0",
    "mypy>=1.0.0,<2.0.0",
    "flake8>=6.0.0,<7.0.0",
    "build>=0.10.0",      # For python -m build
    "twine>=4.0.0"        # For PyPI uploads
]
boxy = []  # Boxy is a separate Rust tool, installed independently

[project.urls]
Homepage = "https://github.com/snekfx/semv-py"
Documentation = "https://github.com/snekfx/semv-py/blob/main/README.md"
Repository = "https://github.com/snekfx/semv-py.git"
Issues = "https://github.com/snekfx/semv-py/issues"

[project.scripts]
semv = "semv.cli:cli"

[tool.setuptools.packages.find]
where = ["."]
include = ["semv*"]
exclude = ["tests*", "docs*", "examples*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--verbose",
    "--cov=semv",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-fail-under=85"
]

[tool.black]
line-length = 88
target-version = ["py38"]
include = '\.pyi?$'

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

## **Main Package Exports**

### **semv/__init__.py**
```python
"""
SEMV - Semantic Version Manager v3.0.0

Multi-language semantic version synchronization with Git integration.
"""

__version__ = "3.0.0"
__author__ = "SEMV Team"

# Core functionality exports
from .core.version import normalize_version, compare_versions, get_highest_version
from .core.project import get_project_context, get_version_authority
from .core.git import get_git_status, create_version_tag, get_latest_tag

# Command exports for programmatic use
from .commands.bump import bump_version
from .commands.sync import sync_versions  
from .commands.status import get_repository_status

# Detection system exports
from .detection import (
    get_repository_context,
    batch_detect_repositories,
    export_repository_index
)

# Utility exports
from .utils.validation import validate_version_format
from .utils.files import backup_file, restore_file

__all__ = [
    "__version__",
    "normalize_version", "compare_versions", "get_highest_version",
    "get_project_context", "get_version_authority",
    "get_git_status", "create_version_tag", "get_latest_tag",
    "bump_version", "sync_versions", "get_repository_status",
    "get_repository_context", "batch_detect_repositories", "export_repository_index",
    "validate_version_format", "backup_file", "restore_file"
]
```

## **Development Workflow**

### **Testing Strategy**
- **Unit tests**: Each module with 85%+ coverage
- **Integration tests**: Full command workflows
- **Compatibility tests**: Against SEMV v2.0.0 behavior
- **Performance tests**: Benchmarks vs. Bash implementation

### **Code Quality**
- **Type hints**: Full typing throughout codebase
- **Linting**: Black + Flake8 + MyPy
- **Documentation**: Comprehensive docstrings
- **Error handling**: Graceful degradation patterns

### **Release Process**
- **Semantic versioning**: Following SEMV's own conventions
- **PyPI distribution**: Automated releases via CI/CD
- **Migration tools**: Smooth transition from v2.0.0
- **Backward compatibility**: 100% command-line compatibility

## **Success Metrics**

### **Technical Goals**
- **70% code reduction**: From 4,000+ lines Bash to 800-1,200 lines Python
- **10x performance**: File parsing operations improvement
- **85%+ test coverage**: Comprehensive test suite
- **<200ms startup**: Including Python interpreter overhead

### **User Experience Goals**  
- **100% compatibility**: All existing SEMV commands work identically
- **Visual enhancement**: Professional output via Boxy integration
- **90% migration success**: Automated migration from v2.0.0
- **Enhanced workflows**: Amend integration and consolidated views

This buildout plan provides a comprehensive roadmap for migrating SEMV from a 4,000+ line Bash monolith to a modular, maintainable Python architecture while preserving full functionality and enhancing the user experience.