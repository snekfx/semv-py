# Code Snippets for Codex Review

## Current CLI Implementation (Working)

```python
# src/semvx/cli/main.py - key excerpt
def main():
    """Main CLI entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "detect":
        do_detection()
        return

    if len(sys.argv) > 1 and sys.argv[1] == "status":
        do_status()
        return

    # Version management commands (stubs for now)
    if len(sys.argv) > 1 and sys.argv[1] in ["bump", "version"]:
        do_version_command()  # STUB - needs implementation
        return
```

## Detection Module API (Shared)

```python
# Key functions from src/semvx/detection/detector.py
def get_repository_context(repo_path: Path) -> Dict[str, Any]:
    """Main entry point - returns full repository analysis"""

def normalize_semver(version: str) -> str:
    """Normalize version to vX.Y.Z format"""

def compare_semver(version1: str, version2: str) -> int:
    """Compare semantic versions (-1, 0, 1)"""

def get_highest_version(versions: List[str]) -> Optional[str]:
    """Find highest version from list"""

def detect_projects(repo_path: Path) -> List[Dict[str, Union[str, None]]]:
    """Detect all projects in repository"""
```

## Proposed SemanticVersion Class Structure

```python
# src/semvx/core/version.py (TO BE IMPLEMENTED)
from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class SemanticVersion:
    """Represents a semantic version with full parsing support."""
    major: int
    minor: int
    patch: int
    prerelease: Optional[str] = None
    build_metadata: Optional[str] = None

    @classmethod
    def parse(cls, version_string: str) -> 'SemanticVersion':
        """Parse a version string into SemanticVersion."""
        # TODO: Implementation needed
        pass

    def bump_major(self) -> 'SemanticVersion':
        """Return new version with major increment."""
        # TODO: Implementation needed
        pass

    def bump_minor(self) -> 'SemanticVersion':
        """Return new version with minor increment."""
        # TODO: Implementation needed
        pass

    def bump_patch(self) -> 'SemanticVersion':
        """Return new version with patch increment."""
        # TODO: Implementation needed
        pass

    def __str__(self) -> str:
        """Format as semantic version string."""
        # TODO: Implementation needed
        pass
```

## Test Coverage Gaps

Current test failures (4):
1. `test_get_highest_version` - Returns None instead of "v0.0.0" for empty list
2. `test_git_repository_detection` - Missing 'root' key in repository context
3. `test_multi_project_detection` - Not detecting all project types in subdirectories
4. `test_empty_directory` - Returns 'none' instead of 'directory' for type

## Performance Baseline

Original Bash script performance (docs/ref/plan/semv.sh):
- 4,000 lines of code
- Sequential processing of projects
- Multiple subprocess calls for git operations
- No caching of detection results

Target Python performance:
- <1,200 lines of code (70% reduction)
- 10x speed improvement
- Minimize subprocess calls
- Cache detection results where appropriate

## Integration Points

### Boxy Workflow Integration
```python
# Future integration needed
def integrate_with_boxy():
    """Hook into Boxy workflow system."""
    # TODO: Implement Boxy adapter
    pass
```

### GitSim Support
```python
# Future integration needed
def detect_gitsim_environment():
    """Check if running in GitSim."""
    # TODO: Implement GitSim detection
    pass
```

## Questions for Architecture

1. **Module Structure**:
   ```
   src/semvx/
   ├── cli/          # Command-line interface
   ├── core/         # Core version logic (TO BUILD)
   ├── detection/    # Project detection (SHARED)
   ├── git/          # Git operations (TO BUILD)
   ├── parsers/      # Language-specific parsers (TO BUILD)
   └── adapters/     # Boxy, GitSim, Blade (TO BUILD)
   ```
   Is this structure optimal?

2. **Dependency Injection Pattern**:
   Should we use dependency injection for git operations to support GitSim?
   ```python
   class VersionManager:
       def __init__(self, git_backend=None):
           self.git = git_backend or GitBackend()
   ```

3. **Error Handling**:
   Should we use exceptions or Result types?
   ```python
   # Option A: Exceptions
   def parse_version(s: str) -> SemanticVersion:
       if invalid:
           raise VersionParseError(s)

   # Option B: Result type
   def parse_version(s: str) -> Result[SemanticVersion, str]:
       if invalid:
           return Err(f"Invalid version: {s}")
   ```

4. **Async Considerations**:
   Worth using async for parallel project processing?
   ```python
   async def detect_all_projects(repo_path: Path):
       tasks = [
           detect_python_async(repo_path),
           detect_rust_async(repo_path),
           detect_javascript_async(repo_path),
       ]
       return await asyncio.gather(*tasks)
   ```

## Size Tracking

Current line counts:
- `src/semvx/cli/main.py`: 169 lines
- `src/semvx/detection/detector.py`: 1098 lines (shared, not counted)
- `src/semvx/__init__.py`: 17 lines
- **Total (excluding shared)**: ~186 lines

Budget remaining for 1,200 line target: ~1,014 lines
- Core module: ~300 lines estimated
- Git operations: ~200 lines estimated
- Parsers: ~300 lines estimated
- Adapters: ~200 lines estimated
- **Total estimated**: ~1,186 lines (within target!)

## Key Decisions Made

1. **Namespace**: Using 'semvx' to avoid conflicts
2. **Detection Module**: Shared as source copy, not dependency
3. **Testing**: pytest with fallback runner
4. **Development**: Makefile + pyenv support
5. **Python Version**: 3.8+ minimum, testing with 3.13.3

## Pending Decisions

1. Version representation (dataclass vs class vs namedtuple)
2. Error handling strategy (exceptions vs result types)
3. Caching strategy for detection results
4. Plugin architecture for language parsers
5. Async vs sync for parallel operations