# Detection Strategy & Patterns

**Document**: Core detection strategy for SEMV and Blade integration  
**Version**: 1.0.0  
**Last Updated**: 2025-09-23  
**Distribution**: Copy-based, zero dependencies

## Executive Summary

This document defines the comprehensive detection strategy for project types, tooling, workspaces, and repository metadata across the SEMV/Blade ecosystem. The approach prioritizes **configuration-driven detection** with **verification helpers** and **pragmatic data storage** using JSON for rich metadata and TSV for quick repository listings.

## Core Architecture Principles

### 1. Module-Based Organization
- **Core modules**: Independent, focused functionality
- **Zero circular dependencies**: Clear dependency hierarchy  
- **Configuration-driven**: `.projectrc` hints reduce expensive detection
- **Helper library approach**: Optional batch processing without forced dependencies

### 2. Data Storage Strategy
- **JSON**: Rich metadata per repository for querying and analysis
- **TSV**: Simple repository listing for quick eyeball inspection
- **XDG+ compliant**: `~/.local/data/repos/` for cache storage
- **Queryable interface**: JSON structure optimized for programmatic access

### 3. Detection Hierarchy
1. **Configuration hints** (`.projectrc` file) - highest priority
2. **Manifest files** (Cargo.toml, package.json, etc.) - high confidence
3. **Pattern matching** (bash scripts, directory structures) - fallback
4. **Verification helpers** - validate hints against reality

## Core Module Breakdown

### Module 1: `detection_core.py`
**Purpose**: Foundation detection for all basic project types  
**Dependencies**: None (pure standard library)  
**Scope**: Essential detection that everything else builds upon

**Functions**:
- `detect_repository_type(repo_path: Path) -> str` - git, gitsim, none
- `detect_projects(repo_path: Path) -> List[Dict]` - returns projects array with roots + version files
- `detect_bash_tools(repo_path: Path) -> Dict` - runs alongside project detection, not instead of
- `validate_project_structure(repo_path: Path) -> Dict[str, bool]`
- `normalize_semver(version: str) -> str` - normalize to vX.Y.Z format
- `compare_semver(version1: str, version2: str) -> int` - -1, 0, 1 comparison

**Project Detection Patterns**:
```python
# Priority 1: Manifest files (high confidence)
# Rust: Cargo.toml with [package] section
# JavaScript: package.json with valid JSON + version field  
# Python: pyproject.toml [project] OR setup.py with version

# Priority 2: BashFX patterns (structured bash projects)
# bashfx-buildsh: build.sh + parts/ + build.map
# bashfx-simple: prefix-name/ directory with name.sh
# standalone: foldername.sh with version comment
# semvrc: .semvrc config file specifying version file

# Priority 3: Simple bash fallback (when no manifest/BashFX found)
# generic: any .sh file with # semv-version: or # version: comment

# Priority 4: Unknown project type (git repo, no detectable patterns)
# unknown: .git directory exists but no project patterns found
```

### Module 2: `tooling_detection.py`
**Purpose**: Standard and emerging tool detection  
**Dependencies**: `detection_core.py`  
**Scope**: Development tooling and infrastructure gaps

**Standard Bin Tools** (must be in `./bin/`):
- `build.sh` - Build automation
- `deploy.sh` - Deployment automation  
- `test.sh` - Testing automation
- `snap.sh` - Benchmarking automation

**Emerging Tools**:
- `Makefile`/`makefile` - Build system detection
- Python scripts in `./bin/` directory
- Custom script directories (`./scripts`, `./tools`)

**Functions**:
- `detect_standard_tools(repo_path: Path) -> Dict[str, Dict]`
- `detect_script_directories(repo_path: Path) -> Dict[str, any]`  
- `detect_dirty_directories(repo_path: Path) -> List[str]`
- `detect_emerging_tools(repo_path: Path) -> Dict[str, any]`

### Module 3: `workspace_detection.py` 
**Purpose**: Monorepo and workspace structure detection  
**Dependencies**: `detection_core.py`, `projectrc_config.py`  
**Scope**: Complex multi-project repository structures

**Workspace Types**:
- **Cargo workspaces**: `[workspace]` section in root Cargo.toml
- **npm workspaces**: `workspaces` field in package.json
- **Poetry workspaces**: Multi-project poetry configurations
- **Git submodules**: `.gitmodules` file detection

**Functions**:
- `detect_workspace_type(repo_path: Path) -> Optional[str]`
- `get_workspace_members(repo_path: Path, workspace_type: str) -> List[Dict]`
- `detect_git_submodules(repo_path: Path) -> List[Dict]`
- `validate_workspace_structure(repo_path: Path) -> Dict[str, bool]`

### Module 4: `projectrc_config.py`
**Purpose**: Configuration-driven detection and verification  
**Dependencies**: None  
**Scope**: User-defined hints and overrides with validation

**Configuration Schema** (`.projectrc`):
```json
{
  "hints": {
    "submodules": ["./vendor/lib1", "./external/tool2"],
    "custom_scripts": ["./scripts/migrate.sh", "./tools/backup.py"],
    "workspace_members": ["./api", "./cli", "./web"],
    "ignore_directories": ["./legacy", "./archived"]
  },
  "overrides": {
    "project_types": ["rust", "bash"],
    "version_authority": "rust",
    "disable_detection": ["python"]
  },
  "metadata": {
    "team": "platform", 
    "primary_language": "rust",
    "deployment_target": "production",
    "maintenance_status": "active"
  }
}
```

**Functions**:
- `load_projectrc(repo_path: Path) -> Optional[Dict]`
- `verify_hints(repo_path: Path, hints: Dict) -> Dict[str, bool]`
- `apply_overrides(detection_result: Dict, overrides: Dict) -> Dict`
- `validate_projectrc_schema(config: Dict) -> List[str]`

### Module 5: `batch_helpers.py`
**Purpose**: Multi-repository processing and caching  
**Dependencies**: All other modules  
**Scope**: Performance optimization and bulk operations

**Functions**:
- `crawl_repositories(root_path: Path, filters: Dict) -> List[Path]`
- `batch_detect_repositories(repo_paths: List[Path]) -> Dict[str, Dict]`
- `cache_detection_results(results: Dict, cache_path: Path) -> None`
- `load_cached_results(cache_path: Path, max_age: int) -> Dict[str, Dict]`

## Data Storage Schema

### JSON Metadata Schema
**File**: `~/.local/data/repos/{repo_hash}/metadata.json`

```json
{
  "repository": {
    "path": "/absolute/path/to/repo",
    "type": "git",
    "branch": "main",
    "last_commit": "abc123...",
    "is_clean": true
  },
  "detection": {
    "project_types": ["rust", "javascript"],
    "projects": [
      {
        "type": "rust",
        "root": "./",
        "version_file": "Cargo.toml",
        "version": "1.2.3"
      },
      {
        "type": "javascript", 
        "root": "./web",
        "version_file": "web/package.json",
        "version": "1.2.1"
      }
    ],
    "tools": {
      "build.sh": {"exists": true, "path": "./bin/build.sh"},
      "deploy.sh": {"exists": true, "path": "./bin/deploy.sh"},
      "test.sh": {"exists": false},
      "snap.sh": {"exists": true, "path": "./bin/snap.sh"},
      "makefile": {"exists": true, "path": "./Makefile"}
    },
    "scripts": {
      "bin_directory": "./bin",
      "root_scripts": ["./migrate.sh"],
      "script_directories": ["./scripts", "./tools"]
    },
    "workspace": {
      "is_workspace": false,
      "type": null,
      "members": []
    },
    "submodules": [],
    "dirty_directories": ["./node_modules", "./target"]
  },
  "configuration": {
    "has_projectrc": true,
    "hints_verified": true,
    "overrides_applied": ["version_authority"],
    "metadata": {
      "team": "platform",
      "primary_language": "rust"
    }
  },
  "validation": {
    "rust": {"ok": true, "version": "1.2.3"},
    "javascript": {"ok": true, "version": "1.2.1"}
  },
  "gitsim": {
    "is_gitsim": false,
    "available": false,
    "simulation_info": null
  },
  "meta": {
    "detector_version": "1.0.0",
    "detection_time": "2025-09-23T10:30:00Z",
    "detection_duration_ms": 45
  }
}
```

### TSV Summary Schema  
**File**: `~/.local/data/repos/repository_index.tsv`

```tsv
repo_path	repo_name	project_types	primary_version	has_build	has_deploy	has_test	has_snap	is_workspace	team	status
/path/to/myapp	myapp	rust,javascript	1.2.3	true	true	false	true	false	platform	active
/path/to/tooling	tooling	bash	1.0.0	true	false	true	false	false	infra	active
/path/to/workspace	workspace	rust	2.1.0	true	true	true	true	true	backend	active
```

## Detection Priority Rules

### Detection Fallback Hierarchy

**Primary Detection** (authoritative project types):
1. **Manifest files**: Cargo.toml, package.json, pyproject.toml
2. **BashFX patterns**: build.sh + parts/, prefix-name/ structures  
3. **Simple bash detection**: .sh files with version comments (fallback only)
4. **Unknown project**: Git repository but no detectable project patterns

**Fallback Rules**:
- If NO manifest files AND NO BashFX patterns → try simple bash detection
- Simple bash: any .sh file with `# semv-version:` or `# version:` comments
- If NO projects detected but `.git` exists → mark as `"unknown"` project type
- Unknown projects still get tools/scripts detection for gap analysis

**Example Results**:
```json
// Repo with manifests - no bash fallback needed
{"projects": [{"type": "rust", "root": "./", "version_file": "Cargo.toml"}]}

// Repo with no manifests, has .sh with version comment - bash fallback
{"projects": [{"type": "bash", "root": "./", "version_file": "script.sh"}]}

// Git repo with no detectable projects - unknown type
{"projects": [{"type": "unknown", "root": "./", "version_file": null}]}

// Non-git directory - no projects
{"projects": []}
```

### 2. Workspace Project Enumeration
- **Root project**: Detected at repository root if manifest exists
- **Workspace members**: Enumerated from workspace configuration (Cargo.toml [workspace], package.json workspaces)
- **Individual projects**: Each member gets separate entry in projects[] array
- **Relative paths**: All paths relative to repository root for consistent addressing

### 3. GitSim Environment Handling
- Check `.gitsim` before `.git` directory
- Validate `gitsim` command availability
- Route git operations through GitSim when appropriate
- Graceful fallback to standard git when GitSim unavailable

## Performance Considerations

### Caching Strategy
- **File-based caching**: JSON metadata per repository
- **Invalidation triggers**: File modification times, git commit changes
- **Batch processing**: Amortize filesystem costs across multiple repos
- **Lazy evaluation**: Only detect what's requested

### Token Economy Optimization
- **Minimize file reads**: Cache existence checks and file contents
- **Batch API calls**: Group expensive operations (git commands, file parsing)
- **Early termination**: Stop detection when sufficient information found
- **Configurable depth**: Allow limiting detection scope for performance

## Error Handling Strategy

### Graceful Degradation
- **File not found**: Return empty results, log warning
- **Parse errors**: Skip malformed files, continue with other detection
- **Permission errors**: Skip inaccessible files gracefully
- **External tool unavailable**: Disable dependent features, continue core detection

### Validation Levels
- **Basic**: File exists and is readable
- **Structural**: File has expected format (valid JSON/TOML)
- **Semantic**: Required fields exist and are valid
- **Cross-validation**: Hints match reality, workspace members exist

## Integration Patterns

### SEMV Integration
```python
# Single repository detection
from detection_core import get_repository_context
context = get_repository_context(Path.cwd())

# Optional configuration enhancement
from projectrc_config import load_projectrc, apply_overrides
config = load_projectrc(Path.cwd())
if config and config.get('overrides'):
    context = apply_overrides(context, config['overrides'])
```

### Blade Integration  
```python
# Multi-repository batch processing
from batch_helpers import crawl_repositories, batch_detect_repositories
repos = crawl_repositories(Path("/workspace"), {"exclude_archived": True})
results = batch_detect_repositories(repos)

# TSV export for quick analysis
export_repository_index(results, Path("~/.local/data/repos/repository_index.tsv"))
```

## Future Extensions

### Additional Language Support
- **Go**: `go.mod` detection
- **Java**: Maven (`pom.xml`) and Gradle (`build.gradle`) detection
- **C/C++**: CMake (`CMakeLists.txt`) detection
- **Docker**: `Dockerfile` and `docker-compose.yml` detection

### Enhanced Tooling Detection
- **CI/CD**: `.github/workflows`, `.gitlab-ci.yml`, `Jenkinsfile`
- **Documentation**: `README.md`, `docs/` directories, documentation generators
- **Security**: Security scanning tools, dependency audit configurations
- **Quality**: Code formatting, linting, and analysis tool configurations

### Workspace Extensions
- **Dependency analysis**: Cross-project dependency mapping
- **Version consistency**: Detect version drift across workspace members  
- **Build orchestration**: Detect build order and dependency chains
- **Release coordination**: Multi-project release planning and validation

## Success Criteria

### Functional Requirements
- **100% detection accuracy**: Match existing Bash implementation behavior
- **Performance target**: <50ms detection time for typical repositories
- **Zero dependencies**: Pure Python standard library implementation
- **Configuration flexibility**: Support for complex repository structures via `.projectrc`

### Integration Success
- **SEMV adoption**: Core detection integrated into SEMV v3.0.0 Python rewrite
- **Blade adoption**: Batch helpers used for multi-repository analysis
- **Data consistency**: Both tools operate on identical detection results
- **Extensibility**: New detection patterns easily added via module system

This detection strategy provides a comprehensive foundation for repository analysis while maintaining architectural flexibility and performance efficiency.