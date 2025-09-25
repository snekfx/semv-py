# SEMV Concepts - Core Patterns and Implementation Philosophy

**Document Version**: 3.0.0  
**Target**: Technical implementers and contributors  
**Scope**: Fundamental concepts, patterns, and design philosophy behind SEMV

## Overview

SEMV (Semantic Version Manager) bridges the gap between git-based version control and package manager version requirements through intelligent automation. This document explains the core concepts, patterns, and design philosophy that make SEMV effective across multiple programming languages and project structures.

## Core Philosophy

### The Version Synchronization Problem

Most projects maintain version information in multiple places:
- **Git tags** (e.g., `v1.2.3`) for release tracking
- **Package files** (e.g., `Cargo.toml`, `package.json`) for dependency management
- **Build artifacts** (e.g., `.build` files) for deployment metadata
- **Documentation** (e.g., README badges) for user communication

These sources frequently drift out of sync, creating confusion and deployment issues. SEMV solves this through automated synchronization with intelligent conflict resolution.

### The Double-Commit Problem

Traditional version management tools create workflow friction:
```bash
# Problematic workflow
git commit -m "feat: new feature"  # Commit 1: actual changes
semv bump                          # Commit 2: version file updates
```

SEMV's **amend workflow** solves this by integrating version management into the natural development flow:
```bash
# Streamlined workflow  
git commit -m "feat: new feature"
semv bump --amend  # Updates package files AND amends into last commit
```

**Amend Workflow Mechanics:**
1. Analyze commit history to determine version bump
2. Update all detected package files with new version
3. Stage the updated files (`git add`)
4. Amend the staged changes into the previous commit (`git commit --amend --no-edit`)
5. Create git tag pointing to the amended commit
6. Update automatic tag pointers (latest)

This creates a single, atomic commit containing both the feature changes and the version updates.

### The "Source of Truth" Hierarchy

SEMV implements a **"highest version wins"** conflict resolution strategy with the following authority hierarchy:

1. **Manual User Specification** (highest authority)
   - Explicit version provided via command line
   - Direct user intent always takes precedence

2. **Package File Versions** 
   - `Cargo.toml` version field
   - `package.json` version field
   - `pyproject.toml` version field
   - Bash script version comments
   - Considered "authoritative" because they affect builds/distribution

3. **Git Tag History**
   - Latest semantic version tag in repository
   - Historical record of releases

4. **Calculated Versions** (lowest authority)
   - SEMV's analysis of commit history
   - Suggested next version based on commit message patterns

When conflicts exist, all sources are synchronized to the highest semantic version found across any source.

## Semantic Versioning Patterns

### SEMV v2.1 Label Conventions (Enhanced)

SEMV analyzes commit messages to determine appropriate version bumps using **expanded prefix-based classification**:

```
Commit Message Pattern → Version Impact → Example
```

**Major Version Bumps (x.0.0):**
```
major|breaking|api: → Major → "breaking: remove deprecated API"
arch: → Major → "arch: restructure core module system"  
ux: → Major → "ux: complete interface redesign"
```

**Minor Version Bumps (x.y.0):**
```
feat|feature|add|minor: → Minor → "feat: add user authentication"
ref: → Minor → "ref: refactor payment processing"
mrg: → Minor → "mrg: merge feature-branch milestone"
```

**Patch Version Bumps (x.y.z):**
```
fix|patch|bug|hotfix|up: → Patch → "fix: handle null pointer exception"
imp: → Patch → "imp: optimize database query performance"  
qol: → Patch → "qol: improve error message clarity"
stb: → Patch → "stb: mark current state as stable"
```

**Development Builds (x.y.z-dev_N):**
```
dev: → Dev Build → "dev: refactor validation logic"
```

**Ignored Commits (No Version Impact):**
```
x: → Ignore → "x: temporary debugging code"
doc: → Ignore → "doc: update API documentation"
admin: → Ignore → "admin: update team contact info"
lic: → Ignore → "lic: update copyright year"  
clean: → Ignore → "clean: remove obsolete test files"
```

**Enhanced Label Categories:**

**Quality Improvements (Patch Level):**
- `imp:` - Performance improvements, optimizations, enhancements
- `qol:` - Quality of life improvements, better user experience  
- `stb:` - Explicit stable designation, production readiness confirmation

**Architecture Changes (Minor/Major Level):**
- `ref:` - Refactoring that adds maintainability (minor impact)
- `mrg:` - Integration milestones, merge points (minor impact)
- `arch:` - Major architectural changes (major impact)
- `ux:` - Major user experience overhauls (major impact)

**Administrative (Ignored):**
- `x:` - Explicit ignore marker for test commits, debugging
- `doc:` - Documentation updates without code changes
- `admin:` - Administrative changes (contacts, metadata)
- `lic:` - License updates, legal changes
- `clean:` - Cleanup commits, removing dead code/files

**Key Enhancement Principles:**
- **Expanded granularity**: More specific categorization of change types
- **Ignore category**: Prevents administrative commits from triggering version bumps
- **Quality focus**: Separate categories for improvements vs. new features
- **Architecture awareness**: Distinguish refactoring from major architectural changes
- **Explicit stable marking**: Allow manual stable designations at patch level

**Key Principles:**
- **Colon suffix required**: Ensures intentional semantic labeling
- **Hierarchical precedence**: Major overrides minor, minor overrides patch
- **Dev notes separate**: Development work doesn't bump release versions
- **Commit accumulation**: Multiple commits since last tag determine final bump

### Version Calculation Algorithm (Enhanced)

```python
def calculate_next_version(current_tag, commit_history):
    changes = analyze_commits_since_with_ignore(current_tag)
    
    # Filter out ignored commits before version calculation
    if changes.has_breaking:
        return bump_major(current_tag)
    elif changes.has_features:
        return bump_minor(current_tag)  
    elif changes.has_fixes:
        return bump_patch(current_tag)
    elif changes.has_dev_notes:
        return add_dev_suffix(current_tag)
    else:
        return current_tag  # No semantic changes (only ignored commits)

def analyze_commits_since_with_ignore(tag):
    """Enhanced commit analysis with ignore category filtering"""
    commits = get_commits_since(tag)
    
    # Separate ignored commits from semantic commits
    semantic_commits = []
    ignored_commits = []
    
    for commit in commits:
        if matches_ignore_pattern(commit.message):
            ignored_commits.append(commit)
        else:
            semantic_commits.append(commit)
    
    # Analyze only semantic commits for version impact
    return analyze_semantic_impact(semantic_commits)
```

### Development vs. Release Versions

SEMV distinguishes between development builds and release versions:

- **Release versions**: `v1.2.3` (clean semantic version)
- **Development builds**: `v1.2.3-dev_5` (includes dev commit count)
- **Build metadata**: `v1.2.3-build_1247` (includes total commit count)

Development versions are used during active development, while release versions are created for stable releases.

## Project Detection Patterns

### Multi-Language Detection Strategy

SEMV supports projects with multiple package managers through **hierarchical detection** with clear priority ordering to prevent false positives:

```python
def detect_project_types():
    detected = []
    
    # Phase 1: Manifest-based detection (high confidence, high priority)
    if exists("Cargo.toml") and has_package_section("Cargo.toml"):
        detected.append("rust")
    if exists("package.json") and has_version_field("package.json"):
        detected.append("javascript") 
    if exists("pyproject.toml") and has_project_section("pyproject.toml"):
        detected.append("python")
        
    # Phase 2: Pattern-based detection (ONLY if no manifest detected)
    if not detected:
        bash_pattern = detect_bash_patterns()
        if bash_pattern:
            detected.append("bash")
            
    return resolve_multi_language_conflicts(detected)
```

**Detection Priority Hierarchy:**
1. **Manifest files** (Cargo.toml, package.json, pyproject.toml) - High confidence
2. **Bash patterns** - Only as fallback when no manifest files found
3. **Conflict resolution** - Handle multiple manifest types in same repository

**Bash Detection Safeguards:**
Bash detection is **explicitly prevented** when higher-priority language manifests exist to avoid:
- False detection in JavaScript projects with bash build scripts
- Incorrect version source selection in Rust projects with shell utilities
- Ambiguous project classification in polyglot repositories

### Bash Project Pattern Recognition

Bash projects lack standardized package files, so SEMV recognizes five distinct patterns:

#### 1. BashFX build.sh Pattern
**Structure**: `build.sh` + `parts/` directory + `build.map` file
**Detection**: Presence of all three components
**Version Location**: First part file listed in `build.map`
**Use Case**: Complex bash applications with modular architecture

```
project/
├── build.sh           # Build orchestration script
├── parts/
│   ├── build.map      # Part assembly instructions  
│   ├── 01_config.sh   # Version comment here
│   ├── 02_utils.sh
│   └── 03_main.sh
└── output.sh          # Generated by build.sh
```

#### 2. BashFX Simple Pattern  
**Structure**: `prefix-name/` directory containing `name.sh`
**Detection**: Directory name contains hyphen, matching script exists
**Version Location**: Main script file header
**Use Case**: Simple bash utilities with clear naming convention

```
semv-tool/
├── tool.sh            # Version comment in header
├── README.md
└── tests/
```

#### 3. Standalone Pattern
**Structure**: Script named after containing directory
**Detection**: `foldername.sh` exists where folder is `foldername/`
**Version Location**: Script header comments
**Use Case**: Single-purpose bash scripts

```
backup/
├── backup.sh          # Version comment in header
└── config/
```

#### 4. Legacy semvrc Pattern
**Structure**: `.semvrc` configuration file specifying version file
**Detection**: `.semvrc` exists with `BASH_VERSION_FILE` variable
**Version Location**: File specified in configuration
**Use Case**: Legacy SEMV installations with custom configuration

```
project/
├── .semvrc            # BASH_VERSION_FILE="src/main.sh"
├── src/
│   └── main.sh        # Version comment here
└── lib/
```

#### 5. Generic Pattern (Enhanced Detection)
**Structure**: Any `.sh` file with version comments, excluding generated files
**Detection**: Search for `# semv-version:` or `# version:` headers with build.sh exclusion
**Version Location**: Comment header in discoverable script (non-generated only)
**Use Case**: Ad-hoc bash scripts with version metadata
**Build.sh Protection**: Skip files with `# generated` tags to avoid immutable version info

```bash
# Enhanced generic pattern detection
detect_bash_generic_pattern() {
    find . -name "*.sh" -type f | while read script; do
        # Skip generated files (build.sh output)
        if grep -q "^# generated" "$script" 2>/dev/null; then
            continue  # Skip to avoid immutable version data
        fi
        
        # Look for version comments in non-generated files
        if grep -q -E "^[[:space:]]*#[[:space:]]*(semv-version|version):" "$script"; then
            echo "$script"
            return 0
        fi
    done
}
```

**Generated File Handling:**
When a bash file contains `# generated` tag (typically from build.sh), SEMV:
1. **Skips the generated file** for version detection and updates
2. **Searches for source files** in parts/ directory (01_*.sh, 02_*.sh, etc.)
3. **Uses earliest part file** for version information (typically 01_config.sh or 00_header.sh)
4. **Preserves build system integrity** by not modifying generated artifacts

### Pattern Priority and Conflict Resolution

When multiple patterns match, SEMV uses this priority order:
1. **semvrc configuration** (explicit user intent)
2. **BashFX build.sh** (structured project)
3. **BashFX simple** (conventional naming)
4. **Standalone** (directory-based naming)
5. **Generic** (fallback search)

## Version Synchronization Architecture

### The Sync Process

Version synchronization follows a careful orchestration to prevent data loss:

```python
def synchronize_versions():
    # 1. Discovery Phase
    project_types = detect_project_types()
    current_versions = gather_all_versions(project_types)
    
    # 2. Analysis Phase  
    conflicts = detect_version_conflicts(current_versions)
    target_version = resolve_conflicts(current_versions)
    
    # 3. Planning Phase
    sync_plan = create_sync_plan(current_versions, target_version)
    
    # 4. Execution Phase (atomic)
    try:
        execute_sync_plan(sync_plan)
        create_sync_tag(target_version)
        commit_success()
    except SyncError:
        rollback_changes()
        raise
```

### Conflict Resolution Strategies

#### Case 1: Package Ahead of Git
**Scenario**: `package.json` shows `1.2.5`, git tags show `v1.2.3`
**Resolution**: Create git tag `v1.2.5`, update other package files to `1.2.5`
**Rationale**: Package file represents current development state

#### Case 2: Git Ahead of Package  
**Scenario**: Git tags show `v1.2.5`, `package.json` shows `1.2.3`
**Resolution**: Update package files to `1.2.5`
**Rationale**: Git tag represents official release

#### Case 3: SEMV Calculated Higher
**Scenario**: All sources show `1.2.3`, SEMV calculates `1.2.4` from commits
**Resolution**: Bump all sources to `1.2.4`, create git tag
**Rationale**: Commit history indicates unreleased changes

#### Case 4: Multi-Source Conflicts
**Scenario**: `Cargo.toml` shows `1.2.5`, `package.json` shows `1.2.3`, git shows `v1.2.4`
**Resolution**: Update all to `1.2.5` (highest version)
**Rationale**: Highest version wins policy prevents regression

### Atomic Operations

All sync operations are atomic - either all version sources are updated successfully, or none are changed. This prevents partial sync states that could cause confusion.

```python
class AtomicSync:
    def __init__(self):
        self.backup_state = None
        self.operations = []
    
    def __enter__(self):
        self.backup_state = capture_current_state()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            restore_state(self.backup_state)
        return False
```

## Git Integration Patterns

### Tag Management Philosophy

SEMV treats git tags as the **historical record** of releases, not necessarily the current development state. This philosophy influences several design decisions:

- **Annotated tags preferred**: Include metadata about who/when/why
- **Semantic versioning strict**: Only `vX.Y.Z` format tags are considered
- **Tag immutability**: Once pushed, tags should not be moved or deleted
- **Branch validation**: Version operations restricted to main/master branches

### Automatic Tag Pointers

SEMV maintains several automatic tag pointers for different use cases:

- **latest**: Always points to most recent version bump (automatic, no gates)
  - Updated on every `semv bump` operation
  - Useful for CI/CD systems that need "current development version"
  - Independent of release system - works in simple mode
  
- **stable**: Manually managed pointer for "ready for production" versions
  - Updated only when explicitly requested: `semv stable`
  - Independent of release system adoption
  - Represents user's assessment of production readiness
  
- **release-system-v1**: Special marker indicating formal release tracking adoption
  - Created by `semv release init` 
  - Serves as feature gate for advanced release commands
  - Historical marker showing when formal releases began

**Tag Independence Principle:**
Each tag pointer serves a distinct purpose and can be managed independently:
- `latest` tracks development progress automatically
- `stable` tracks production readiness manually  
- Release markers track process adoption optionally

### Progressive Release Adoption

SEMV implements a **progressive enhancement** model for release management:

```bash
# Phase 1: Simple version management (always available)
semv bump --amend   # Core workflow
semv stable         # Manual stable marking

# Phase 2: Formal release tracking (opt-in)
semv release init   # Creates release-system marker
semv publish        # Now unlocked with full workflow
```

The release adoption marker serves as a **feature gate** - release commands are always discoverable but show helpful guidance until the repository adopts formal release tracking.

### Commit Analysis Engine

SEMV analyzes commit messages to understand the **intent** behind changes:

```python
def analyze_commit_impact(commit_message):
    """
    Determine semantic impact of a commit based on message prefix
    """
    if matches_pattern(commit_message, BREAKING_PATTERNS):
        return CommitImpact.BREAKING
    elif matches_pattern(commit_message, FEATURE_PATTERNS):
        return CommitImpact.FEATURE  
    elif matches_pattern(commit_message, FIX_PATTERNS):
        return CommitImpact.FIX
    elif matches_pattern(commit_message, DEV_PATTERNS):
        return CommitImpact.DEV
    else:
        return CommitImpact.NONE
```

**Key Insights:**
- **Intent over content**: Focus on declared intent rather than code analysis
- **Accumulative impact**: Multiple commits contribute to final version bump
- **Developer responsibility**: Developers must properly label their commits

### Branch Protection Model

Version bumps are restricted to main/master branches to prevent:
- **Accidental releases** from feature branches
- **Version conflicts** between parallel development streams
- **Tag pollution** from experimental work

## Build Cursor System

### Metadata Generation Philosophy

The build cursor system generates `.build` files containing comprehensive metadata about the current repository state. This serves several purposes:

- **Deployment tracking**: Know exactly what version is deployed where
- **Build reproducibility**: Capture exact state for debugging
- **Version coordination**: Synchronize across multiple deployment targets
- **Audit trails**: Historical record of what was built when

### Build Information Schema

```bash
# Generated .build file format
DEV_VERS=v1.2.3          # Current semantic version
DEV_BUILD=1247           # Total commit count + floor
DEV_BRANCH=main          # Current branch
DEV_DATE=08/15/25        # Build date
DEV_SEMVER=v1.2.4-dev_2  # Next calculated version
SYNC_SOURCE=cargo        # Authority source for sync
SYNC_VERSION=1.2.3       # Version from authority source
SYNC_DATE=2025-08-15T10:30:00Z  # Sync timestamp
```

### Build Number Algorithm

Build numbers provide monotonically increasing identifiers:

```python
BUILD_FLOOR = 1000  # Minimum build number
build_number = commit_count + BUILD_FLOOR
```

This ensures:
- **Uniqueness**: Every commit gets a unique build number
- **Monotonicity**: Build numbers always increase
- **Floor protection**: Avoid confusion with small integers

## Error Handling Philosophy

### Graceful Degradation

SEMV follows a graceful degradation philosophy - when components fail, the system continues operating with reduced functionality rather than failing completely:

- **Boxy unavailable**: Fall back to plain text output
- **Git repository invalid**: Continue with file-only operations  
- **Package file malformed**: Skip that source, continue with others
- **Network unavailable**: Use local data only

### User-Friendly Error Messages

Error messages follow a structured format:
1. **What went wrong**: Clear statement of the problem
2. **Why it happened**: Context about the cause
3. **How to fix it**: Actionable steps for resolution

```python
class SemvError(Exception):
    def __init__(self, what, why, how_to_fix):
        self.what = what
        self.why = why  
        self.how_to_fix = how_to_fix
        super().__init__(f"{what}: {why}. {how_to_fix}")
```

### Validation Strategy

Input validation occurs at multiple layers:
- **CLI arguments**: Validate before processing
- **File contents**: Validate before parsing
- **Git operations**: Validate repository state
- **Version formats**: Validate semantic version compliance

## Performance Patterns

### Lazy Loading

SEMV uses lazy loading to avoid unnecessary work:
- **Project detection**: Only scan when needed
- **File parsing**: Only parse files that will be used
- **Git operations**: Cache results within single command execution
- **Boxy rendering**: Only invoke when output is needed

### Caching Strategy

Within a single command execution, SEMV caches:
- **Git repository information**: Branch, tags, commit counts
- **File parsing results**: Avoid re-parsing same files
- **Project detection results**: Avoid re-scanning directory structure

**Note**: No persistent caching across command invocations to ensure fresh data.

### Subprocess Optimization

Git operations use optimized subprocess patterns:
- **Batch operations**: Combine multiple git queries when possible
- **Error handling**: Graceful handling of git operation failures
- **Output parsing**: Efficient parsing of git command output

## Extension Patterns

### Adding New Project Types

Adding support for a new project type requires implementing the parser interface:

```python
class ProjectParser:
    def detect(self, project_path: Path) -> bool:
        """Return True if this project type is detected"""
        pass
        
    def extract_version(self, project_path: Path) -> Optional[str]:
        """Extract current version from project files"""
        pass
        
    def write_version(self, project_path: Path, version: str) -> bool:
        """Write new version to project files"""
        pass
```

### Hook System Architecture

The hook system provides extensibility points for custom automation:

```python
class HookSystem:
    def register_hook(self, event: HookEvent, callback: Callable):
        """Register callback for specific events"""
        pass
        
    def execute_hooks(self, event: HookEvent, context: dict):
        """Execute all registered hooks for event"""
        pass
```

**Supported Hook Events:**
- `pre_version_bump`: Before version calculation
- `post_version_bump`: After successful version bump
- `pre_sync`: Before version synchronization
- `post_sync`: After successful synchronization

## Testing Patterns

### Test Data Philosophy

SEMV testing uses real-world project examples rather than synthetic test data:
- **Actual Cargo.toml files** from Rust projects
- **Real package.json files** from JavaScript projects
- **Authentic bash scripts** with various patterns
- **Historical git repositories** with complex tag histories

### Test Organization

Tests are organized by **concern** rather than by **module**:
- **Version parsing tests**: All version format edge cases
- **Project detection tests**: All project type combinations
- **Sync operation tests**: All conflict resolution scenarios
- **Git integration tests**: All repository state variations

### Regression Prevention

Critical functionality is protected by **characterization tests** that capture the exact behavior of the Bash implementation and ensure the Python implementation matches exactly.

## Integration Patterns

### CI/CD Integration

SEMV is designed for seamless CI/CD integration:

```bash
# Pre-commit validation
semv validate || exit 1

# Automatic version bumping
semv bump --auto --no-cursor

# Deployment metadata
semv build --build-dir ./dist/
```

### IDE Integration

SEMV supports IDE integration through:
- **JSON output mode**: Machine-readable output for tooling
- **Exit codes**: Standard success/failure indicators
- **File watching**: Detect when version files change

### External Tool Integration

SEMV integrates with external tools through:
- **Environment variables**: Configuration and state sharing
- **Standard streams**: Pipe-friendly input/output
- **Exit codes**: Shell scripting integration

## Security Considerations

### File System Safety

SEMV follows secure file handling practices:
- **Atomic writes**: Use temporary files with atomic rename
- **Permission respect**: Don't modify file permissions
- **Backup creation**: Always backup before modification
- **Path validation**: Prevent directory traversal attacks

### Git Repository Safety

Git operations are performed safely:
- **Read-only by default**: Only modify when explicitly requested
- **Branch validation**: Prevent accidental operations on wrong branches
- **Remote safety**: Never force-push or delete remote tags
- **Commit verification**: Validate commit signatures when available

This document captures the essential patterns and concepts that make SEMV effective. Understanding these patterns is crucial for successful implementation, extension, and maintenance of the system.