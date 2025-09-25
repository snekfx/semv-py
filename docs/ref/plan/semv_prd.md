# SEMV Python Rewrite - Product Requirements Document

**Version**: 3.0.0  
**Target Architecture**: Python 3.8+ with Boxy Integration  
**Migration From**: Bash-based SEMV v2.0.0 (4,000+ lines)  
**Expected Size**: 800-1,200 lines Python + modular architecture

## Executive Summary

SEMV (Semantic Version Manager) v2.0.0 has proven successful as a Bash-based tool but has grown to over 4,000 lines in a single monolithic script. The Python rewrite (v3.0.0) addresses critical scalability, maintainability, and performance issues while preserving all existing functionality and enhancing the user experience through Boxy integration.

- Reference Project: `~/repos/code/shell/bashfx/fx-semv` available as `semv -help`

- Publish to Pypi as semv-py installed locally as new `semv`

- Out of scope: support for other lanaguages like Java, C/C++, Go, etc.

## Current State Analysis

### Existing SEMV v2.0.0 Capabilities
- **Multi-language support**: Rust (Cargo.toml), JavaScript (package.json), Python (pyproject.toml), Bash (script comments)
- **Intelligent project detection**: 5 distinct Bash project patterns (BashFX build.sh, simple, standalone, semvrc, generic)
- **Semantic versioning**: Commit-message-based version bumping with SEMV v2.0 label conventions
- **Version synchronization**: "Highest version wins" conflict resolution across all project sources
- **Git integration**: Tag management, branch validation, commit analysis
- **Workflow automation**: Pre-commit hooks, release workflows, auto-sync
- **Build cursor system**: Automated metadata file generation with version info
- **Developer tools**: Inspection, validation, drift detection

### Critical Issues with Current Implementation
1. **Monolithic architecture**: Single 4,000-line script is unmaintainable
2. **Performance bottlenecks**: Bash string parsing for JSON/TOML is inefficient
3. **Limited extensibility**: Adding new project types requires deep bash expertise
4. **Testing complexity**: Bash functions are difficult to unit test in isolation
5. **Error handling**: Complex error propagation through nested bash functions
6. **Data structure limitations**: Bash arrays/strings vs. native data types

## Goals & Objectives

### Primary Goals
1. **Reduce codebase size by 70%**: From 4,000+ lines to 800-1,200 lines
2. **Achieve 10x performance improvement** for file parsing operations
3. **Enable modular architecture** with isolated, testable components
4. **Enhance user experience** through Boxy visual integration
5. **Maintain 100% functional compatibility** with existing workflows

### Secondary Goals
1. **Improve extensibility**: New project types should require <50 lines of code
2. **Enable comprehensive testing**: Unit tests for all core components
3. **Professional visual output**: Leverage Boxy for all status/report commands
4. **Better error messages**: Clear, actionable error reporting with visual emphasis

## Technical Architecture

### Core Design Principles
1. **Single Responsibility**: Each module handles one aspect (parsing, git ops, display)
2. **Dependency Injection**: Modules can be swapped/mocked for testing
3. **Subprocess Hybrid**: Keep git operations as subprocess calls, handle logic in Python
4. **Graceful Degradation**: Boxy integration falls back to plain text when unavailable
5. **Configuration Driven**: Behavior controlled through config files and environment variables

### Module Structure
```
semv/
├── core/               # Core business logic
│   ├── version.py      # Version parsing, comparison, validation
│   ├── git.py         # Git operations (tags, commits, branches)
│   ├── project.py     # Project type detection and classification
│   └── config.py      # Configuration management and environment
├── parsers/           # Language-specific version extraction/writing
│   ├── rust.py        # Cargo.toml TOML parsing
│   ├── javascript.py  # package.json JSON parsing
│   ├── python_parser.py  # pyproject.toml/setup.py handling
│   └── bash.py        # Bash script comment parsing (5 patterns)
├── commands/          # High-level command implementations
│   ├── bump.py        # Version bumping with commit analysis
│   ├── sync.py        # Multi-source version synchronization
│   ├── status.py      # Dashboard and status reporting
│   ├── lifecycle.py   # Install/uninstall/reset operations
│   ├── hooks.py       # Hook system and workflow automation
│   └── release.py     # Optional release flow system
├── adapters/          # External integration layer (NEW)
│   ├── __init__.py    # Adapter registry and discovery
│   ├── base.py        # Abstract adapter interface
│   ├── gitsim.py      # GitSim simulation environment adapter
│   └── blade.py       # Blade multi-repo management adapter
│   ├── display.py     # Boxy integration wrapper with fallback
│   ├── themes.py      # Semantic themes (error, success, warning, info)
│   ├── views.py       # All output view formatting (consolidated UX)
│   └── formatter.py   # Output formatting utilities
├── utils/            # Shared utilities
│   ├── files.py       # File operations and path management
│   └── validation.py  # Input validation and error handling
└── cli.py            # Main CLI entry point with argument parsing
```

### Data Flow Architecture
1. **CLI Layer**: Argument parsing and command routing
2. **Command Layer**: Business logic orchestration
3. **Core Layer**: Domain-specific operations (version, git, project)
4. **Parser Layer**: Language-specific file handling
5. **UI Layer**: Output formatting and display
6. **Storage Layer**: Configuration and state management

## Functional Requirements

### FR1: Multi-Language Project Support
- **Rust**: Parse/write Cargo.toml `[package]` section version field
- **JavaScript**: Parse/write package.json `version` field with JSON validation
- **Python**: Parse/write pyproject.toml `[project]` section OR setup.py version parameter
- **Bash**: Parse/write version comments in 5 distinct patterns:
  - BashFX build.sh: parts/ directory with build.map, version in first part file
  - BashFX simple: prefix-name/ folder with name.sh file containing version
  - Standalone: foldername.sh file with version comment
  - semvrc: Legacy .semvrc configuration pointing to version file
  - Generic: Any .sh file with `# semv-version:` or `# version:` comments

### FR2: Intelligent Project Detection
- **Multi-language detection**: Handle projects with multiple package files (e.g., Rust + JavaScript)
- **Bash pattern recognition**: Automatically detect which of the 5 bash patterns applies
- **Conflict resolution**: Implement "highest version wins" policy across all detected sources
- **Validation**: Verify project structure integrity and version consistency

### FR3: Semantic Versioning Operations
- **Commit analysis**: Parse commit messages using enhanced SEMV v2.1 label conventions:
  - **Major (5 labels)**: `major|breaking|api|arch|ux:` → Major version bump (x.0.0)
  - **Minor (6 labels)**: `feat|feature|add|minor|ref|mrg:` → Minor version bump (x.y.0)
  - **Patch (8 labels)**: `fix|patch|bug|hotfix|up|imp|qol|stb:` → Patch version bump (x.y.z)
  - **Dev (1 label)**: `dev:` → Development build suffix
  - **Ignore (5 labels)**: `x|doc|admin|lic|clean:` → No version impact, excluded from bump calculation
- **Version calculation**: Determine next version based on commit history since last tag with ignore filtering
- **Git tag management**: Create annotated tags with proper messaging
- **Branch validation**: Ensure version operations only occur on main/master branches

### FR4: Version Synchronization System
- **Conflict detection**: Identify mismatches between package files and git tags
- **Automatic resolution**: Sync all sources to highest semantic version found
- **Manual override**: Allow explicit version specification for sync operations
- **Validation**: Verify all sources are aligned after sync operations

### FR5: Developer Workflow Integration
- **Dashboard**: Comprehensive repository status with version information
- **Pre-commit validation**: Ensure version consistency before commits
- **Build metadata**: Generate build cursor files with version/commit information
- **Hook system**: Execute custom scripts on version bump events

### FR6: Enhanced Workflow Features
- **Amend workflow**: Update package files and amend into last commit with `--amend` flag to eliminate double-commit problem
- **Latest tag management**: Automatic floating pointer to most recent version, updated on every bump
- **Stable tag management**: Manual stable version pointer for production-ready releases
- **Enhanced readiness assessment**: `semv can` reports both basic SEMV capabilities and release flow readiness

### FR7: Optional Release Flow System  
- **Release adoption marker**: Special git tag (`release-system-v1`) indicating formal release tracking adoption
- **Progressive enhancement**: Release commands always visible but gated with helpful guidance until initialized
- **Command gating strategy**: Helpful bumper messages instead of hiding advanced commands
- **Publish workflow**: Comprehensive publication process with validation and artifact generation
- **Release system initialization**: `semv release init` creates adoption marker and unlocks advanced features

## Non-Functional Requirements

### NFR1: Performance
- **JSON/TOML parsing**: <10ms for typical package files (vs. 100ms+ in Bash)
- **Git operations**: Maintain current performance (already subprocess-based)
- **Startup time**: <200ms total startup time including Python interpreter
- **Memory usage**: <50MB peak memory usage for typical repositories

### NFR2: Maintainability
- **Code coverage**: Minimum 85% unit test coverage for all core modules
- **Cyclomatic complexity**: Maximum 10 per function
- **Module coupling**: Loose coupling between parsers and core logic
- **Documentation**: Comprehensive docstrings and type hints throughout

### NFR3: Usability
- **Command compatibility**: 100% command-line compatibility with SEMV v2.0.0
- **Visual enhancement**: Professional output through Boxy integration
- **Error reporting**: Clear, actionable error messages with visual emphasis
- **Progressive disclosure**: Basic operations simple, advanced features discoverable

### NFR4: Reliability
- **Error handling**: Graceful degradation when dependencies unavailable
- **Data validation**: Comprehensive input validation for all operations
- **Atomic operations**: Version updates are atomic (all succeed or all rollback)
- **Backup/recovery**: Ability to restore previous state on operation failure

### FR8: External Tool Integration
- **Adapter architecture**: Plugin system for external tool integration with standardized interface
- **GitSim integration**: Native support for GitSim simulated repository environments
- **Blade integration**: Simplified multi-repository coordination via JSON output (CLI-only, no library API)
- **Cross-cutting concerns**: Standardized logging, metrics, and error handling across integrations

### FR9: JSON Output Support (Limited Scope)
- **Status/dashboard JSON**: `--json` flag for `semv status` and `semv info` commands
- **Blade-specific format**: `--json-blade` flag providing Blade-compatible output structure
- **Simple data model**: Basic repository information without complex state modeling
- **CLI-focused**: JSON output only, not full library API surface

### Workflow Integration
- **Amend workflow**: `semv bump --amend` updates package files and amends them into the last commit, eliminating the double-commit problem
- **Progressive release adoption**: Release commands always visible but gated with helpful guidance until formal release tracking is initialized
- **Consolidated output views**: All text output formatting centralized in `views.py` for consistent UX iteration

### Enhanced Status Reporting
- **Comprehensive readiness**: `semv can` reports both basic SEMV capabilities and release flow readiness
- **Tag awareness**: `semv status` shows all available tag pointers (latest, stable, release markers) without overwhelming when absent
- **Release system indicators**: Clear visual distinction between simple mode and release-aware mode

### Visual Output with Boxy Integration
All status, dashboard, and report commands will use Boxy for professional visual output:

- **Status Dashboard**: Repository information in themed boxes
- **Version Reports**: Comparison tables with semantic coloring
- **Error Messages**: Prominent error boxes with actionable guidance
- **Success Confirmations**: Green success boxes for completed operations
- **Conflict Resolution**: Warning-themed boxes highlighting version drift

### Semantic Theming
- **Error Theme**: Red boxes with ❌ icons for failures and critical issues
- **Success Theme**: Green boxes with ✅ icons for completed operations
- **Warning Theme**: Orange boxes with ⚠️ icons for conflicts and drift
- **Info Theme**: Blue boxes with ℹ️ icons for status and information
- **Critical Theme**: Double-border boxes for important confirmations

### Fallback Strategy
When Boxy is unavailable:
- Preserve all functional behavior
- Use simple text output with ASCII formatting
- Maintain color coding through ANSI escape sequences
- Provide clear indication when visual enhancements are disabled

## Migration Strategy

### Phase 1: Core Infrastructure (Week 1-2)
- Set up Python project structure with proper packaging
- Implement core version parsing and comparison logic
- Create Boxy integration wrapper with fallback
- Establish testing framework and CI/CD pipeline

### Phase 2: Parser Implementation (Week 2-3)
- Implement all language-specific parsers (Rust, JS, Python, Bash)
- Create comprehensive test suite for parser accuracy
- Validate against existing SEMV v2.0.0 test cases
- Handle edge cases and malformed files gracefully

### Phase 3: Command Implementation (Week 3-4)
- Port all high-level commands (bump, sync, status, etc.)
- Implement git integration layer
- Create comprehensive dashboard with Boxy theming
- Add workflow automation features

### Phase 4: Testing & Validation (Week 4-5)
- Comprehensive testing against real-world repositories
- Performance benchmarking vs. Bash implementation
- User acceptance testing with existing SEMV users
- Documentation and migration guide creation

### Phase 5: Production Deployment (Week 5-6)
- Package distribution via pip/PyPI
- Migration tooling for existing installations
- Rollback procedures and compatibility shims
- User training and adoption support

## Risk Assessment

### High Risk
- **Breaking changes**: Subtle behavioral differences between Bash and Python implementations
- **Performance regression**: Python startup time vs. Bash script execution
- **Dependency management**: Managing Python package dependencies vs. Bash self-contained script

### Medium Risk  
- **Boxy integration complexity**: Subprocess overhead and error handling
- **Testing completeness**: Ensuring 100% functional compatibility
- **User adoption**: Convincing users to migrate from working Bash solution

### Low Risk
- **Development velocity**: Python development should be significantly faster
- **Maintainability**: Modular architecture reduces long-term maintenance burden
- **Extensibility**: Adding new features becomes much simpler

## Success Metrics

### Technical Metrics
- **Code reduction**: Achieve 70% reduction in total lines of code
- **Performance improvement**: 10x faster for file parsing operations
- **Test coverage**: Achieve 85%+ unit test coverage
- **Bug reduction**: 50% reduction in reported issues within 3 months

### User Experience Metrics
- **Visual appeal**: 90% user satisfaction with Boxy-enhanced output
- **Error clarity**: 80% reduction in user confusion from error messages
- **Feature adoption**: 70% of users adopt new visual features within 6 months
- **Migration success**: 90% successful migration from v2.0.0 without issues

## Appendix

### SEMV v2.0 Label Conventions
The commit message prefixes that determine version bumps:
- **Major**: `major:`, `breaking:`, `api:` - Breaking changes requiring major version bump
- **Minor**: `feat:`, `feature:`, `add:`, `minor:` - New features requiring minor version bump  
- **Patch**: `fix:`, `patch:`, `bug:`, `hotfix:`, `up:` - Bug fixes requiring patch version bump
- **Dev**: `dev:` - Development notes, adds dev build suffix

### Bash Project Pattern Details
1. **BashFX build.sh**: build.sh script + parts/ directory + build.map file listing parts
2. **BashFX simple**: Directory named prefix-name/ containing name.sh main script
3. **Standalone**: Single script named after containing directory (foldername.sh)
4. **semvrc**: Legacy .semvrc configuration file specifying BASH_VERSION_FILE path
5. **Generic**: Any .sh file containing `# semv-version:` or `# version:` comment headers

### Version Sync Resolution Algorithm
The "highest version wins" conflict resolution follows this priority:
1. Manual user specification (highest priority)
2. Package file versions (Cargo.toml, package.json, etc.)
3. Git tag history (latest semantic version tag)
4. Build cursor information (lowest priority)

All sources are updated to match the highest semantic version found across any source.
