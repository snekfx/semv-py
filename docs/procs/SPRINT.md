# Current Sprint - Critical Fixes & Core Module

## Sprint Goal
Fix critical regressions identified by Codex, then implement core version management.

## Active Tasks (Priority Order - China & Codex Aligned)

### 🚨 P1 - CRITICAL FIXES (Must complete first)
- [ ] **REG-DET-01**: Fix get_highest_version fallback - 1 SP
  - Return "v0.0.0" for empty lists (not None)
  - Location: src/semvx/detection/detector.py:143
  - Unblocks 1 failing test
- [ ] **REG-DET-02**: Add 'root' field to repository context - 1 SP
  - Add missing field to context dict
  - Fix type="directory" (not "none") for plain dirs
  - Unblocks 2 failing tests

### 🔥 P2 - CORE MODULE (After fixes)
- [ ] **CORE-VER-01**: Implement immutable SemanticVersion - 3 SP
  - Use @dataclass with functools.total_ordering
  - Immutable pattern per Codex guidance
  - Foundation for all version operations
- [ ] **REG-DET-03**: Recursive project discovery - 3 SP
  - Walk subdirectories for nested projects
  - Add bounded recursion with ignores
  - Unblocks 1 failing test
- [ ] **CORE-VER-02**: Version parsing with validation - 2 SP
  - Parse semantic version strings
  - Raise VersionParseError on invalid
  - Support pre-release and build metadata

### 🎯 HIGH PRIORITY - Git Integration
- [ ] **CORE-04**: Implement git repository interface - 6 SP
  - Repository detection and validation
  - Branch and tag operations
  - Commit analysis for version bumping
- [ ] **CORE-05**: Create tag management system - 4 SP
  - Semantic version tag creation
  - Tag validation and conflict resolution
  - Remote tag synchronization

### 📋 MEDIUM PRIORITY - Testing & Fixes
- [ ] **TEST-01**: Fix failing detection tests - 2 SP
  - Update tests to match actual API
  - Ensure 100% test coverage for core module
- [ ] **TEST-02**: Add integration tests for version operations - 3 SP
  - Test version bumping scenarios
  - Test git tag operations
  - Test multi-project synchronization

## Completed This Sprint
- ✅ **ARCH-01**: Python project structure created
- ✅ **ARCH-02**: Detection module integrated (shared source)
- ✅ **ARCH-03**: CLI interface complete with detect/status commands
- ✅ **ARCH-05**: Testing infrastructure with pytest, fixtures, CI/CD
- ✅ **ARCH-06**: Testing patterns and fallback runner
- ✅ **Local Development**: Makefile, setup script, DEVELOPMENT.md

## Sprint Metrics
- **Committed Story Points**: 9 (Meta Process completion)
- **Completed Story Points**: 4 (initial setup)
- **Sprint Duration**: 1 session
- **Focus Area**: Foundation & Meta Process

## Blockers & Dependencies
- **None identified** - Clear path for completion

## Definition of Done
- [ ] All Meta Process v2 phases implemented
- [ ] Documentation validation passing
- [ ] Fresh agent can onboard in <5 minutes
- [ ] All process documents current and linked
- [ ] Changes merged to main branch

## Next Sprint Preview
After Meta Process completion, next sprint will focus on:
1. Core module architecture design
2. Python project setup and tooling
3. Initial module implementation (version parsing)