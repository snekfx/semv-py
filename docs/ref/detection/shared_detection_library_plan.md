# Shared Project Detection Library - Design and Implementation Plan

**Target**: Standalone detection module for SEMV and Blade integration  
**Distribution Model**: Source code copying (not package dependency)  
**Size**: 200-300 lines total  
**Languages**: Python 3.8+ compatible

## Core Design Principles

### 1. Zero Dependencies
- Pure Python standard library only
- No external packages or imports beyond `pathlib`, `re`, `json`
- Self-contained functions that can be copied anywhere

### 2. Hierarchical Detection Strategy
- **Manifest files first** (high confidence)
- **Pattern-based detection only as fallback** (prevents false positives)
- **Clear priority ordering** to avoid ambiguous results

### 3. Enhanced Safeguards
- **Generated file exclusion** (`# generated` tag protection)
- **Build system awareness** (route to source files in parts/)
- **Validation and error handling** for malformed files

## Library Structure

### Core Module: `detection_shared.py`

```python
# detection_shared.py - Shared project detection library
# Version: 1.0.0
# Compatible with: SEMV v3.0.0, Blade Next
# Distribution: Copy into target project (not dependency)

from pathlib import Path
from typing import List, Dict, Optional, Tuple
import re
import json
```

## Function Inventory

### 1. Primary Detection Interface

#### `detect_repository_type(repo_path: Path) -> str`
**Purpose**: Determine repository environment type  
**Returns**: `"git"`, `"gitsim"`, or `"none"`  
**Logic**: Check for .gitsim before .git to properly identify simulated environments

#### `detect_project_types(repo_path: Path) -> List[str]`
**Purpose**: Main entry point for hierarchical project detection  
**Logic**: Manifest-first with bash fallback prevention  
**Returns**: Ordered list of detected project types  

#### `get_version_files(repo_path: Path, project_types: List[str]) -> Dict[str, Path]`
**Purpose**: Map project types to their version-containing files  
**Returns**: `{"rust": Path("Cargo.toml"), "javascript": Path("package.json")}`

#### `check_gitsim_availability() -> bool`
**Purpose**: Check if gitsim command is available in PATH  
**Usage**: Validate GitSim environment before attempting operations

#### `validate_project_structure(repo_path: Path) -> Dict[str, bool]`
**Purpose**: Check if detected projects have valid, parseable files  
**Returns**: Validation results per project type

### 2. Manifest Detection Functions

#### `has_rust_manifest(repo_path: Path) -> bool`
**Logic**: Check for `Cargo.toml` with `[package]` section  
**Validation**: Ensure version field exists and is parseable

#### `has_javascript_manifest(repo_path: Path) -> bool`
**Logic**: Check for `package.json` with valid JSON and version field  
**Validation**: JSON parsing and version field validation

#### `has_python_manifest(repo_path: Path) -> bool`
**Logic**: Check for `pyproject.toml` with `[project]` section OR `setup.py` with version  
**Priority**: pyproject.toml preferred over setup.py when both exist

### 3. Enhanced Bash Detection

#### `detect_bash_patterns(repo_path: Path) -> Optional[str]`
**Purpose**: Identify which of 5 bash patterns applies  
**Returns**: Pattern name or None  
**Patterns**:
- `"bashfx-buildsh"` - build.sh + parts/ + build.map
- `"bashfx-simple"` - prefix-name/ folder with name.sh
- `"standalone"` - foldername.sh with version comment
- `"semvrc"` - .semvrc configuration specifying version file
- `"generic"` - .sh files with version comments (excluding generated)

#### `get_bash_project_file(repo_path: Path, pattern: str) -> Optional[Path]`
**Purpose**: Get the actual file containing version info for detected pattern  
**Logic**: Route from generated files to source files when needed

#### `is_generated_file(file_path: Path) -> bool`
**Purpose**: Check if file contains `# generated` tag  
**Usage**: Skip generated files in version detection and writing

### 4. Version Extraction Functions

#### `extract_rust_version(file_path: Path) -> Optional[str]`
**Logic**: Parse TOML `[package]` section, extract version field

#### `extract_javascript_version(file_path: Path) -> Optional[str]`
**Logic**: Parse JSON, extract version field with error handling

#### `extract_python_version(file_path: Path) -> Optional[str]`
**Logic**: Handle both pyproject.toml `[project]` and setup.py patterns

#### `extract_bash_version(file_path: Path) -> Optional[str]`
**Logic**: Find version comments, exclude lines with code artifacts ($ or ")

### 6. GitSim Environment Detection

#### `detect_repository_type(repo_path: Path) -> str`
**Purpose**: Determine repository environment type for command routing  
**Logic**: Check .gitsim before .git (GitSim takes precedence)  
**Returns**: Repository type string

#### `check_gitsim_availability() -> bool`  
**Purpose**: Verify gitsim command exists in PATH  
**Usage**: Validate GitSim environment before operations

#### `is_gitsim_repo(repo_path: Path) -> bool`
**Purpose**: Quick check for GitSim simulated environment  
**Logic**: Check for .gitsim directory existence

#### `get_gitsim_metadata(repo_path: Path) -> Optional[Dict[str, any]]`
**Purpose**: Extract GitSim simulation metadata if available  
**Returns**: Simulation state, user info, project metadata

#### `validate_version_format(version: str) -> bool`
**Purpose**: Check if string is valid semantic version  
**Logic**: Basic semver regex validation

#### `find_bash_source_file(repo_path: Path, generated_file: Path) -> Optional[Path]`
**Purpose**: Route from generated .sh file to source file in parts/  
**Logic**: Check build.map, find earliest part file with version

#### `get_project_metadata(repo_path: Path) -> Dict[str, any]`
**Purpose**: Extract additional project metadata for both tools  
**Returns**: Repository info, file counts, last modified dates

## Enhanced Detection Logic

### Repository Environment Detection

```python
def detect_repository_type(repo_path: Path) -> str:
    """Determine repository environment for command routing"""
    if (repo_path / ".gitsim").exists():
        return "gitsim"  # GitSim takes precedence over real git
    elif (repo_path / ".git").exists():
        return "git"
    else:
        return "none"

def check_gitsim_availability() -> bool:
    """Check if gitsim command is available in PATH"""
    import shutil
    return shutil.which("gitsim") is not None

def validate_gitsim_environment(repo_path: Path) -> Dict[str, any]:
    """Validate GitSim environment and provide guidance"""
    result = {
        "is_gitsim": (repo_path / ".gitsim").exists(),
        "gitsim_available": check_gitsim_availability(),
        "status": "unknown"
    }
    
    if result["is_gitsim"] and result["gitsim_available"]:
        result["status"] = "ready"
    elif result["is_gitsim"] and not result["gitsim_available"]:
        result["status"] = "missing_command"
        result["message"] = "GitSim project detected but 'gitsim' command not found in PATH"
    else:
        result["status"] = "not_gitsim"
    
    return result
```

### Enhanced Hierarchical Detection

```python
def detect_project_types(repo_path: Path) -> List[str]:
    """Enhanced detection with GitSim awareness"""
    detected = []
    
    # Repository environment check (affects all subsequent operations)
    repo_type = detect_repository_type(repo_path)
    
    # Phase 1: High-confidence manifest detection
    manifest_types = []
    if has_rust_manifest(repo_path):
        manifest_types.append("rust")
    if has_javascript_manifest(repo_path):
        manifest_types.append("javascript")
    if has_python_manifest(repo_path):
        manifest_types.append("python")
    
    # Phase 2: Only check bash if NO manifests found
    if manifest_types:
        detected = manifest_types
    else:
        bash_pattern = detect_bash_patterns(repo_path)
        if bash_pattern:
            detected = ["bash"]
    
    return detected

def get_repository_context(repo_path: Path) -> Dict[str, any]:
    """Complete repository analysis for both SEMV and Blade"""
    return {
        "repository_type": detect_repository_type(repo_path),
        "project_types": detect_project_types(repo_path),
        "version_files": get_version_files(repo_path, detect_project_types(repo_path)),
        "gitsim_status": validate_gitsim_environment(repo_path),
        "validation": validate_project_structure(repo_path)
    }
```

### Build System Protection

```python
def detect_bash_patterns(repo_path: Path) -> Optional[str]:
    """Bash detection with generated file exclusion"""
    
    # Pattern 1: BashFX build.sh (with parts/ routing)
    if (repo_path / "build.sh").exists() and (repo_path / "parts").exists():
        return "bashfx-buildsh"
    
    # Pattern 5: Generic (with generated file exclusion)
    for script in repo_path.glob("*.sh"):
        if is_generated_file(script):
            continue  # Skip generated files
        if has_version_comment(script):
            return "generic"
            
    return None
```

## Integration Patterns

### SEMV Integration

```python
# semv/core_module.py  
# Copy detection_shared.py functions directly into core module

def enhanced_repository_detection():
    repo_path = Path.cwd()
    context = get_repository_context(repo_path)
    
    # Route git operations based on repository type
    if context["repository_type"] == "gitsim":
        if not context["gitsim_status"]["gitsim_available"]:
            raise GitSimNotAvailableError("GitSim project detected but command not available")
        return GitSimOperations(repo_path)
    elif context["repository_type"] == "git":
        return GitOperations(repo_path)
    else:
        raise NoRepositoryError("No git or gitsim repository detected")
```

### Blade Integration

```python
# blade/analysis/detection.py  
# Copy detection_shared.py as standalone module

def analyze_repository(repo_path):
    context = get_repository_context(repo_path)
    
    # Blade can handle all repository types for analysis
    analysis = RepositoryAnalysis(
        repo_type=context["repository_type"],
        project_types=context["project_types"], 
        version_files=context["version_files"],
        validation=context["validation"]
    )
    
    # Add GitSim-specific metadata if applicable
    if context["repository_type"] == "gitsim":
        analysis.simulation_info = context["gitsim_status"]
    
    return analysis
```

## Error Handling Strategy

### Graceful Degradation
- **File not found**: Return empty results, don't crash
- **Parse errors**: Log warning, continue with other detection
- **Permission errors**: Skip inaccessible files gracefully

### Validation Levels
- **Basic**: File exists and is readable
- **Structural**: File has expected format (valid JSON, TOML sections)
- **Semantic**: Version field exists and is valid semver

## Testing Strategy

### Test Categories
1. **Unit tests**: Each detection function with valid/invalid inputs
2. **Integration tests**: Full detection workflow on real project examples  
3. **Regression tests**: Ensure bash detection doesn't trigger on manifest projects
4. **Edge case tests**: Generated files, malformed files, permission issues

### Test Repository Examples
- **rust-only**: Simple Cargo.toml project
- **javascript-only**: Simple package.json project
- **mixed-manifest**: Rust + JavaScript in same repo
- **bashfx-buildsh**: build.sh + parts/ structure
- **bash-with-generated**: Generated .sh file, should route to parts/
- **no-project**: Repository with no detectable project type

## Distribution and Maintenance

### Copy-Based Distribution
1. **Canonical source**: Maintain in SEMV repository
2. **Version tagging**: Clear version comments in file header
3. **Copy instructions**: Document when/how to sync changes
4. **Change notifications**: Alert both teams when detection logic updates

### Versioning Strategy
```python
# detection_shared.py header
"""
Shared Project Detection Library
Version: 1.2.0
Last Updated: 2025-01-15
Compatible: SEMV v3.0+, Blade Next v1.0+
Changes: Added enhanced bash pattern detection with generated file exclusion
"""
```

### Synchronization Process
1. **Changes made in SEMV**: Update canonical version
2. **Version bump**: Increment version number and update header
3. **Notification**: Inform Blade team of changes
4. **Copy update**: Blade team copies updated version
5. **Testing**: Both teams test with updated detection

## Performance Considerations

### File System Efficiency
- **Minimize file reads**: Cache file existence checks
- **Lazy evaluation**: Only parse files when needed
- **Early termination**: Stop detection once manifest found

### Memory Efficiency  
- **Stream parsing**: Don't load entire files into memory
- **Minimal data structures**: Return only essential information
- **No global state**: Pure functions for thread safety

## Future Extensions

### Additional Language Support
The library is designed for easy extension:

```python
def has_go_manifest(repo_path: Path) -> bool:
    """Future: Go module detection"""
    return (repo_path / "go.mod").exists()

def has_java_manifest(repo_path: Path) -> bool:
    """Future: Maven/Gradle detection"""  
    return ((repo_path / "pom.xml").exists() or 
            (repo_path / "build.gradle").exists())
```

### Enhanced Metadata
- Repository age and activity metrics
- Build system detection (not just project types)
- Dependency complexity scoring
- Version consistency analysis

## Success Criteria

### Functional Requirements
- **100% consistency**: Both tools get identical detection results
- **Performance**: <50ms detection time for typical repositories
- **Reliability**: Graceful handling of all error conditions
- **Maintainability**: Clear, documented, testable code

### Integration Success
- **SEMV adoption**: Detection logic integrated into CORE_MODULE
- **Blade adoption**: Detection used for multi-repo analysis
- **Zero coupling**: Neither tool depends on the other
- **Version synchronization**: Clear process for updates

This shared detection library provides the consistency Blade needs while maintaining the architectural independence both tools require. The copy-based distribution ensures no external dependencies while enabling coordinated evolution of detection logic.