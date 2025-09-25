# Core Project Detection Technology - Buildout Plan

## Architecture Decision: Unified Adapter Pattern + Helper Library Approach

**Key Insights**:
1. Boxy should follow adapter pattern for consistency
2. **Workspace detection requires manifest indication** (not discovery-based)
3. **Helper library approach**: Optional caching without forcing batch operations
4. **Standard bin tools detection**: build.sh, deploy.sh, test.sh, snap.sh
5. **Dirty directory tracking**: Automated cleanup opportunities

```
# Core detection (always available)
detection_shared.py              # Single-repo detection, no dependencies

# Optional batch helpers (can be used independently)  
batch_detection_helper.py        # Multi-repo crawling and caching
cache_manager.py                 # XDG+ data storage and invalidation

# Adapters (external tool integration)
adapters/
├── __init__.py                  # Adapter registry and discovery
├── base.py                      # Abstract adapter interface  
├── gitsim.py                    # GitSim simulation environment
├── blade.py                     # Blade multi-repo coordination
└── boxy.py                      # Visual output enhancement
```

## Phase 1: Detection Library as First Deliverable (Week 1)

### Day 1-2: Core Detection Infrastructure

**Deliverable 1.1: `detection_shared.py`**
- Version: 1.0.0 (copy-based distribution)
- Zero dependencies (pure standard library)
- Self-contained module for Blade team integration

**Priority Functions:**

1. **Repository Environment Detection**
   ```python
   def detect_repository_type(repo_path: Path) -> str:
       """Returns: 'gitsim', 'git', or 'none' (check .gitsim first!)"""
   
   def check_gitsim_availability() -> bool:
       """Check if gitsim command is in PATH"""
   
   def validate_gitsim_environment(repo_path: Path) -> Dict[str, any]:
       """Complete GitSim status including simulation info"""
   ```

2. **Manifest Detection (High Confidence)**
   ```python
   def has_rust_manifest(repo_path: Path) -> bool:
       """Check Cargo.toml with [package] section"""
   
   def has_javascript_manifest(repo_path: Path) -> bool:
       """Check package.json with valid JSON + version"""
   
   def has_python_manifest(repo_path: Path) -> bool:
       """Check pyproject.toml [project] OR setup.py"""
   ```

3. **Standard Bin Tools Detection**
   ```python
   def detect_standard_tools(repo_path: Path) -> Dict[str, Dict]:
       """Detect standard bin tools: build.sh, deploy.sh, test.sh, snap.sh"""
       standard_tools = ["build.sh", "deploy.sh", "test.sh", "snap.sh"]
       tools = {}
       
       for tool in standard_tools:
           # Check root first, then bin/ directory
           if (repo_path / tool).exists():
               tools[tool] = {"exists": True, "path": f"./{tool}"}
           elif (repo_path / "bin" / tool).exists():
               tools[tool] = {"exists": True, "path": f"./bin/{tool}"}
           else:
               tools[tool] = {"exists": False}
       
       return tools
   
   def detect_script_directories(repo_path: Path) -> Dict[str, any]:
       """Find script directories and root-level scripts"""
       script_dirs = []
       root_scripts = []
       
       # Look for script directories (excluding parts/ which is source code)
       for item in repo_path.iterdir():
           if item.is_dir() and item.name in ["scripts", "tools", "bin"]:
               script_dirs.append(f"./{item.name}")
       
       # Find root-level .sh files (excluding standard tools)
       for script in repo_path.glob("*.sh"):
           if script.name not in ["build.sh", "deploy.sh", "test.sh", "snap.sh"]:
               root_scripts.append(f"./{script.name}")
       
       return {
           "bin_directory": "./bin" if (repo_path / "bin").exists() else None,
           "root_scripts": root_scripts,
           "script_directories": script_dirs
       }
   ```

4. **Dirty Directory Detection**
   ```python
   def detect_dirty_directories(repo_path: Path) -> List[str]:
       """Find gitignore-type directories that could be cleaned up"""
       dirty_patterns = [
           "node_modules", "target", ".venv", "venv", "__pycache__",
           "build", "dist", ".tox", ".pytest_cache", ".coverage"
       ]
       
       found_dirty = []
       for pattern in dirty_patterns:
           if (repo_path / pattern).exists():
               found_dirty.append(f"./{pattern}")
       
       return found_dirty
   ```

### Day 3-4: Integration Interface

**Deliverable 1.2: Primary Detection API**
```python
def get_repository_context(repo_path: Path) -> Dict:
    """Single entry point returning complete repository analysis"""
    return {
        "repository": {"type": "git", "branch": "main", "is_clean": True},
        "projects": [  # PRIMARY INTERFACE - handles workspaces, fallbacks, unknown
            {"type": "rust", "root": "./", "version_file": "Cargo.toml", "version": "1.2.3"},
            {"type": "rust", "root": "./cli", "version_file": "cli/Cargo.toml", "version": "1.2.1"},
            {"type": "javascript", "root": "./web", "version_file": "web/package.json", "version": "2.0.0"}
        ],
        "tools": {
            "standard_bin": {  # Infrastructure gap analysis
                "build.sh": {"exists": True, "path": "./bin/build.sh"},
                "deploy.sh": {"exists": True, "path": "./bin/deploy.sh"},
                "test.sh": {"exists": False},
                "snap.sh": {"exists": True, "path": "./bin/snap.sh"}
            }
        },
        "scripts": {  # General script discovery metadata
            "bin_directory": "./bin",
            "root_scripts": ["./migrate.sh"],
            "script_directories": ["./scripts", "./tools"]
        },
        "workspace": {"is_workspace": True, "type": "cargo", "members": 2},
        "gitsim_status": {"is_gitsim": False, "available": False},
        "validation": {"rust": {"ok": True, "version": "1.2.3"}},
        "meta": {"detector_version": "1.0.0", "detection_time": "2025-09-23T10:30:00Z"}
    }
```

**SemVer Utilities** (zero-dependency regex):
```python
def normalize_semver(version: str) -> str:
    """Normalize version to vX.Y.Z format, handle v prefix and pre-release"""
    # "1.2.3" -> "v1.2.3"
    # "v1.2.3-alpha.1+meta" -> "v1.2.3"
    
def compare_semver(version1: str, version2: str) -> int:
    """Compare semantic versions (-1, 0, 1)"""
    # Enables "highest version wins" logic
```

### Day 5: Testing and Validation

**Deliverable 1.3: Test Suite**
```python
# tests/test_detection_shared.py
class TestRepositoryDetection:
    def test_gitsim_vs_git_priority(self):
        """Ensure .gitsim detected before .git"""
    
    def test_manifest_hierarchy(self):
        """Manifest detection prevents bash fallback"""
    
    def test_bash_pattern_accuracy(self):
        """All 5 bash patterns correctly identified"""
    
    def test_generated_file_exclusion(self):
        """Generated files properly excluded from detection"""
    
    def test_gitsim_integration(self):
        """GitSim environments properly detected and handled"""
```

**Test Repository Examples:**
```
test_repos/
├── rust-only/           # Simple Cargo.toml
├── javascript-only/     # Simple package.json  
├── python-only/         # pyproject.toml
├── mixed-manifest/      # Rust + JavaScript
├── bashfx-buildsh/      # build.sh + parts/ structure
├── bash-generated/      # Generated .sh file -> route to parts/
├── gitsim-repo/         # GitSim simulated environment
└── no-project/          # No detectable project
```

## Week 1 Success Criteria

### Functional Requirements
- ✅ **100% detection accuracy** vs. existing Bash implementation
- ✅ **GitSim environment support** with proper command routing
- ✅ **Generated file protection** prevents version corruption
- ✅ **Performance target**: <50ms detection time for typical repos
- ✅ **Zero dependencies**: Pure standard library

### Integration Requirements
- ✅ **Copy-ready**: Self-contained module for Blade integration
- ✅ **Version tracking**: Clear version headers for synchronization
- ✅ **Documentation**: Complete API documentation and usage examples
- ✅ **Test coverage**: 90%+ coverage with real-world test cases

## Coordination with Blade Team

### Week 1 Delivery Schedule
- **Day 1-2**: Core detection functions ready for review
- **Day 3**: Integration API finalized with Blade team feedback
- **Day 4**: GitSim integration tested and validated
- **Day 5**: Complete module ready for Blade team copy + integration

### Communication Protocol
1. **Daily standups**: Share detection function progress
2. **Mid-week review**: Blade team validates API design
3. **End-of-week delivery**: Complete `detection_shared.py` module
4. **Integration testing**: Both teams test with real repositories

## Phase 2: Adapter Architecture Foundation (Week 2)

### Day 6-7: Abstract Adapter Interface
```python
# adapters/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class AdapterBase(ABC):
    """Abstract interface for all external tool adapters"""
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if external tool is available"""
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get current status/info from external tool"""
    
    @abstractmethod  
    def handle_error(self, error: Exception) -> Optional[Dict]:
        """Graceful error handling with fallback"""
```

### Day 8-10: Concrete Adapter Implementations
```python
# adapters/gitsim.py
class GitSimAdapter(AdapterBase):
    def is_available(self) -> bool:
        return check_gitsim_availability()
    
    def get_simulation_info(self, repo_path: Path) -> Dict:
        """GitSim-specific simulation metadata"""

# adapters/boxy.py  
class BoxyAdapter(AdapterBase):
    def is_available(self) -> bool:
        return shutil.which("boxy") is not None
    
    def render_themed_output(self, theme: str, content: str) -> str:
        """Enhanced visual output with fallback"""

# adapters/blade.py
class BladeAdapter(AdapterBase):
    def get_multi_repo_context(self, repos: List[Path]) -> Dict:
        """Multi-repository coordination support"""
```

## GitSim-Specific Considerations

### Detection Priority
1. Check for `.gitsim` directory first (before `.git`)
2. Validate `gitsim` command availability
3. Extract simulation metadata if available
4. Route git operations through GitSim when appropriate

### Integration Points
```python
def get_gitsim_simulation_metadata(repo_path: Path) -> Dict:
    """Extract GitSim simulation information"""
    return {
        "simulation_active": True,
        "base_branch": get_simulated_base_branch(),
        "simulated_commits": count_simulated_commits(),
        "simulation_config": parse_gitsim_config()
    }
```

### Error Handling
- Graceful degradation when GitSim unavailable
- Clear error messages for GitSim-specific issues
- Fallback to standard git operations when appropriate

## Distribution and Maintenance

### Copy-Based Distribution Strategy
1. **Canonical source**: Maintain in SEMV repository
2. **Version tracking**: Clear version comments in file header
3. **Synchronization process**: Documented update workflow
4. **Change notifications**: Alert both teams when detection logic updates

### Version Management
```python
# detection_shared.py header
"""
Shared Project Detection Library
Version: 1.0.0
Last Updated: 2025-09-23
Compatible: SEMV v3.0+, Blade Next v1.0+
Changes: Initial implementation with GitSim integration
"""
```