"""
Workspace Detection Module - Monorepo and Multi-Project Structure Analysis
Version: 1.0.0
Last Updated: 2025-09-23
Compatible: SEMV v3.0+, Blade Next v1.0+
Dependencies: detection_core.py

Detects and analyzes workspace structures across multiple project types.
"""

from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple
import re
import json
import subprocess
import os


# ============================================================================
# Workspace Type Detection
# ============================================================================

def detect_workspace_type(repo_path: Path) -> Optional[str]:
    """
    Detect if repository is a workspace/monorepo and determine type.
    
    Workspace types supported:
    - cargo: Rust Cargo workspaces
    - npm: npm/yarn/pnpm workspaces
    - poetry: Python Poetry multi-project
    - git_submodules: Git submodules
    - mixed: Multiple workspace types present
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        Workspace type string if detected, None if single-project repo
    """
    repo_path = Path(repo_path).resolve()
    detected_types = []
    
    # Check for Cargo workspace
    if _is_cargo_workspace(repo_path):
        detected_types.append("cargo")
    
    # Check for npm workspace
    if _is_npm_workspace(repo_path):
        detected_types.append("npm")
    
    # Check for Poetry workspace
    if _is_poetry_workspace(repo_path):
        detected_types.append("poetry")
    
    # Check for Git submodules
    if _has_git_submodules(repo_path):
        detected_types.append("git_submodules")
    
    if len(detected_types) == 0:
        return None
    elif len(detected_types) == 1:
        return detected_types[0]
    else:
        return "mixed"


def _is_cargo_workspace(repo_path: Path) -> bool:
    """Check if repository is a Cargo workspace."""
    cargo_toml = repo_path / "Cargo.toml"
    if not cargo_toml.exists():
        return False
    
    try:
        content = cargo_toml.read_text(encoding='utf-8')
        # Look for [workspace] section
        return '[workspace]' in content and 'members' in content
    except (OSError, UnicodeDecodeError):
        return False


def _is_npm_workspace(repo_path: Path) -> bool:
    """Check if repository is an npm/yarn/pnpm workspace."""
    package_json = repo_path / "package.json"
    if not package_json.exists():
        return False
    
    try:
        content = package_json.read_text(encoding='utf-8')
        data = json.loads(content)
        
        # Check for workspaces field (npm/yarn)
        if 'workspaces' in data:
            return True
        
        # Check for pnpm-workspace.yaml
        if (repo_path / "pnpm-workspace.yaml").exists():
            return True
        
        return False
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return False


def _is_poetry_workspace(repo_path: Path) -> bool:
    """Check if repository is a Poetry multi-project workspace."""
    pyproject_toml = repo_path / "pyproject.toml"
    if not pyproject_toml.exists():
        return False
    
    try:
        content = pyproject_toml.read_text(encoding='utf-8')
        # Look for Poetry workspace indicators
        # Note: Poetry doesn't have official workspace support yet,
        # but we can detect multi-project setups
        has_poetry = '[tool.poetry]' in content
        
        # Check for multiple pyproject.toml files in subdirectories
        if has_poetry:
            subproject_count = len(list(repo_path.glob("*/pyproject.toml")))
            return subproject_count > 0
        
        return False
    except (OSError, UnicodeDecodeError):
        return False


def _has_git_submodules(repo_path: Path) -> bool:
    """Check if repository has Git submodules."""
    gitmodules = repo_path / ".gitmodules"
    return gitmodules.exists()


# ============================================================================
# Workspace Member Enumeration
# ============================================================================

def get_workspace_members(repo_path: Path, workspace_type: str) -> List[Dict[str, Union[str, List]]]:
    """
    Enumerate all workspace members with their project information.
    
    Args:
        repo_path: Path to repository directory
        workspace_type: Type of workspace (from detect_workspace_type)
        
    Returns:
        List of workspace members with project details:
        [
            {
                "name": "cli",
                "path": "./cli",
                "type": "rust",
                "version_file": "cli/Cargo.toml",
                "version": "1.0.0",
                "dependencies": ["common"]
            }
        ]
    """
    repo_path = Path(repo_path).resolve()
    members = []
    
    if workspace_type == "cargo":
        members = _get_cargo_workspace_members(repo_path)
    elif workspace_type == "npm":
        members = _get_npm_workspace_members(repo_path)
    elif workspace_type == "poetry":
        members = _get_poetry_workspace_members(repo_path)
    elif workspace_type == "git_submodules":
        members = _get_git_submodule_members(repo_path)
    elif workspace_type == "mixed":
        # Combine all workspace types
        members.extend(_get_cargo_workspace_members(repo_path))
        members.extend(_get_npm_workspace_members(repo_path))
        members.extend(_get_poetry_workspace_members(repo_path))
        members.extend(_get_git_submodule_members(repo_path))
    
    return members


def _get_cargo_workspace_members(repo_path: Path) -> List[Dict]:
    """Get Cargo workspace members."""
    cargo_toml = repo_path / "Cargo.toml"
    if not cargo_toml.exists():
        return []
    
    try:
        content = cargo_toml.read_text(encoding='utf-8')
        members = []
        
        # Parse workspace members (simple regex approach)
        # Format: members = ["cli", "server", "common"]
        members_match = re.search(r'members\s*=\s*\[(.*?)\]', content, re.DOTALL)
        if not members_match:
            return []
        
        members_str = members_match.group(1)
        # Extract quoted member names
        member_names = re.findall(r'["\']([^"\']+)["\']', members_str)
        
        for member_name in member_names:
            member_path = repo_path / member_name
            if member_path.exists() and (member_path / "Cargo.toml").exists():
                member_info = _analyze_cargo_member(repo_path, member_name, member_path)
                if member_info:
                    members.append(member_info)
        
        return members
    
    except (OSError, UnicodeDecodeError):
        return []


def _get_npm_workspace_members(repo_path: Path) -> List[Dict]:
    """Get npm/yarn/pnpm workspace members."""
    package_json = repo_path / "package.json"
    members = []
    
    # Check npm/yarn workspaces in package.json
    if package_json.exists():
        try:
            content = package_json.read_text(encoding='utf-8')
            data = json.loads(content)
            workspaces = data.get('workspaces', [])
            
            # Handle both array and object format
            if isinstance(workspaces, dict):
                workspaces = workspaces.get('packages', [])
            
            for workspace_pattern in workspaces:
                members.extend(_resolve_npm_workspace_pattern(repo_path, workspace_pattern))
        
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            pass
    
    # Check pnpm-workspace.yaml
    pnpm_workspace = repo_path / "pnpm-workspace.yaml"
    if pnpm_workspace.exists():
        try:
            content = pnpm_workspace.read_text(encoding='utf-8')
            # Simple YAML parsing for packages list
            packages_match = re.search(r'packages:\s*\n((?:\s*-.*\n)*)', content)
            if packages_match:
                packages_text = packages_match.group(1)
                patterns = re.findall(r'-\s*["\']?([^"\'\n]+)["\']?', packages_text)
                for pattern in patterns:
                    members.extend(_resolve_npm_workspace_pattern(repo_path, pattern))
        
        except (OSError, UnicodeDecodeError):
            pass
    
    return members


def _get_poetry_workspace_members(repo_path: Path) -> List[Dict]:
    """Get Poetry workspace members (multi-project detection)."""
    members = []
    
    # Find all pyproject.toml files in subdirectories
    for pyproject_path in repo_path.glob("*/pyproject.toml"):
        if pyproject_path.parent != repo_path:  # Skip root pyproject.toml
            try:
                content = pyproject_path.read_text(encoding='utf-8')
                if '[tool.poetry]' in content:
                    member_info = _analyze_poetry_member(repo_path, pyproject_path)
                    if member_info:
                        members.append(member_info)
            except (OSError, UnicodeDecodeError):
                continue
    
    return members


def _get_git_submodule_members(repo_path: Path) -> List[Dict]:
    """Get Git submodule information."""
    gitmodules = repo_path / ".gitmodules"
    if not gitmodules.exists():
        return []
    
    members = []
    try:
        content = gitmodules.read_text(encoding='utf-8')
        
        # Parse .gitmodules format
        # [submodule "name"]
        #     path = path/to/submodule
        #     url = https://github.com/user/repo.git
        
        submodule_blocks = re.findall(
            r'\[submodule\s+"([^"]+)"\]\s*\n(?:\s*\w+\s*=\s*[^\n]+\s*\n)*',
            content
        )
        
        for block in re.finditer(
            r'\[submodule\s+"([^"]+)"\]\s*\n((?:\s*\w+\s*=\s*[^\n]+\s*\n)*)',
            content
        ):
            submodule_name = block.group(1)
            submodule_config = block.group(2)
            
            path_match = re.search(r'path\s*=\s*([^\n]+)', submodule_config)
            url_match = re.search(r'url\s*=\s*([^\n]+)', submodule_config)
            
            if path_match:
                submodule_path = path_match.group(1).strip()
                submodule_url = url_match.group(1).strip() if url_match else None
                
                member_info = {
                    "name": submodule_name,
                    "path": f"./{submodule_path}",
                    "type": "git_submodule",
                    "version_file": None,
                    "version": None,
                    "url": submodule_url,
                    "dependencies": []
                }
                
                # Try to detect project type in submodule
                submodule_full_path = repo_path / submodule_path
                if submodule_full_path.exists():
                    try:
                        from detection_core import detect_projects
                        submodule_projects = detect_projects(submodule_full_path)
                        if submodule_projects:
                            # Use first detected project type
                            first_project = submodule_projects[0]
                            member_info["type"] = first_project["type"]
                            member_info["version_file"] = f"{submodule_path}/{first_project['version_file']}"
                            member_info["version"] = first_project["version"]
                    except ImportError:
                        pass
                
                members.append(member_info)
    
    except (OSError, UnicodeDecodeError):
        pass
    
    return members


# ============================================================================
# Member Analysis Functions
# ============================================================================

def _resolve_npm_workspace_pattern(repo_path: Path, pattern: str) -> List[Dict]:
    """Resolve npm workspace glob patterns to actual packages."""
    import glob
    members = []
    
    # Convert workspace pattern to glob pattern
    if '*' in pattern:
        # Handle glob patterns like "packages/*"
        glob_pattern = str(repo_path / pattern / "package.json")
        package_files = glob.glob(glob_pattern)
    else:
        # Direct package path
        package_file = repo_path / pattern / "package.json"
        package_files = [str(package_file)] if package_file.exists() else []
    
    for package_file_str in package_files:
        package_file = Path(package_file_str)
        if package_file.exists():
            member_info = _analyze_npm_member(repo_path, package_file)
            if member_info:
                members.append(member_info)
    
    return members


def _analyze_cargo_member(repo_path: Path, member_name: str, member_path: Path) -> Optional[Dict]:
    """Analyze individual Cargo workspace member."""
    cargo_toml = member_path / "Cargo.toml"
    if not cargo_toml.exists():
        return None
    
    try:
        content = cargo_toml.read_text(encoding='utf-8')
        
        # Extract package name and version
        name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
        version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        
        # Extract dependencies
        dependencies = _extract_cargo_dependencies(content)
        
        relative_path = f"./{member_path.relative_to(repo_path)}"
        
        return {
            "name": name_match.group(1) if name_match else member_name,
            "path": relative_path,
            "type": "rust",
            "version_file": f"{relative_path}/Cargo.toml",
            "version": version_match.group(1) if version_match else None,
            "dependencies": dependencies
        }
    
    except (OSError, UnicodeDecodeError):
        return None


def _analyze_npm_member(repo_path: Path, package_file: Path) -> Optional[Dict]:
    """Analyze individual npm workspace member."""
    try:
        content = package_file.read_text(encoding='utf-8')
        data = json.loads(content)
        
        member_path = package_file.parent
        relative_path = f"./{member_path.relative_to(repo_path)}"
        
        # Extract dependencies
        dependencies = []
        for dep_type in ['dependencies', 'devDependencies', 'peerDependencies']:
            if dep_type in data:
                dependencies.extend(data[dep_type].keys())
        
        return {
            "name": data.get('name', member_path.name),
            "path": relative_path,
            "type": "javascript",
            "version_file": f"{relative_path}/package.json",
            "version": data.get('version'),
            "dependencies": dependencies
        }
    
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None


def _analyze_poetry_member(repo_path: Path, pyproject_path: Path) -> Optional[Dict]:
    """Analyze individual Poetry project member."""
    try:
        content = pyproject_path.read_text(encoding='utf-8')
        
        member_path = pyproject_path.parent
        relative_path = f"./{member_path.relative_to(repo_path)}"
        
        # Extract name and version from [tool.poetry] section
        name_match = re.search(r'\[tool\.poetry\].*?name\s*=\s*["\']([^"\']+)["\']', content, re.DOTALL)
        version_match = re.search(r'\[tool\.poetry\].*?version\s*=\s*["\']([^"\']+)["\']', content, re.DOTALL)
        
        # Extract dependencies
        dependencies = _extract_poetry_dependencies(content)
        
        return {
            "name": name_match.group(1) if name_match else member_path.name,
            "path": relative_path,
            "type": "python",
            "version_file": f"{relative_path}/pyproject.toml",
            "version": version_match.group(1) if version_match else None,
            "dependencies": dependencies
        }
    
    except (OSError, UnicodeDecodeError):
        return None


def _extract_cargo_dependencies(content: str) -> List[str]:
    """Extract dependency names from Cargo.toml content."""
    dependencies = []
    
    # Find [dependencies] section
    deps_match = re.search(r'\[dependencies\](.*?)(?:\[.*?\]|$)', content, re.DOTALL)
    if deps_match:
        deps_section = deps_match.group(1)
        # Extract dependency names (simple approach)
        dep_matches = re.findall(r'^([a-zA-Z0-9_-]+)\s*=', deps_section, re.MULTILINE)
        dependencies.extend(dep_matches)
    
    return dependencies


def _extract_poetry_dependencies(content: str) -> List[str]:
    """Extract dependency names from Poetry pyproject.toml content."""
    dependencies = []
    
    # Find [tool.poetry.dependencies] section
    deps_match = re.search(r'\[tool\.poetry\.dependencies\](.*?)(?:\[.*?\]|$)', content, re.DOTALL)
    if deps_match:
        deps_section = deps_match.group(1)
        # Extract dependency names
        dep_matches = re.findall(r'^([a-zA-Z0-9_-]+)\s*=', deps_section, re.MULTILINE)
        dependencies.extend(dep_matches)
    
    return dependencies


# ============================================================================
# Workspace Analysis and Validation
# ============================================================================

def analyze_workspace_structure(repo_path: Path) -> Dict[str, Union[str, int, List, Dict]]:
    """
    Comprehensive workspace structure analysis.
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        Complete workspace analysis including dependency mapping
    """
    repo_path = Path(repo_path).resolve()
    
    workspace_type = detect_workspace_type(repo_path)
    if not workspace_type:
        return {
            "is_workspace": False,
            "type": None,
            "member_count": 0,
            "members": [],
            "dependency_graph": {},
            "analysis": {}
        }
    
    members = get_workspace_members(repo_path, workspace_type)
    dependency_graph = _build_dependency_graph(members)
    analysis = _analyze_workspace_health(members, dependency_graph)
    
    return {
        "is_workspace": True,
        "type": workspace_type,
        "member_count": len(members),
        "members": members,
        "dependency_graph": dependency_graph,
        "analysis": analysis
    }


def _build_dependency_graph(members: List[Dict]) -> Dict[str, List[str]]:
    """Build internal dependency graph between workspace members."""
    member_names = {member["name"] for member in members}
    dependency_graph = {}
    
    for member in members:
        member_name = member["name"]
        member_deps = member.get("dependencies", [])
        
        # Find internal dependencies (dependencies that are other workspace members)
        internal_deps = [dep for dep in member_deps if dep in member_names]
        dependency_graph[member_name] = internal_deps
    
    return dependency_graph


def _analyze_workspace_health(members: List[Dict], dependency_graph: Dict) -> Dict:
    """Analyze workspace health and identify potential issues."""
    analysis = {
        "total_members": len(members),
        "project_types": {},
        "version_consistency": {},
        "dependency_issues": [],
        "circular_dependencies": [],
        "isolated_members": []
    }
    
    # Count project types
    for member in members:
        project_type = member["type"]
        analysis["project_types"][project_type] = analysis["project_types"].get(project_type, 0) + 1
    
    # Check version consistency
    versions_by_name = {}
    for member in members:
        name = member["name"]
        version = member.get("version")
        if version:
            if name in versions_by_name and versions_by_name[name] != version:
                analysis["version_consistency"][name] = {
                    "inconsistent": True,
                    "versions": [versions_by_name[name], version]
                }
            else:
                versions_by_name[name] = version
    
    # Find circular dependencies
    analysis["circular_dependencies"] = _find_circular_dependencies(dependency_graph)
    
    # Find isolated members (no internal dependencies and no dependents)
    all_deps = set()
    for deps in dependency_graph.values():
        all_deps.update(deps)
    
    for member_name, deps in dependency_graph.items():
        if not deps and member_name not in all_deps:
            analysis["isolated_members"].append(member_name)
    
    return analysis


def _find_circular_dependencies(dependency_graph: Dict[str, List[str]]) -> List[List[str]]:
    """Find circular dependencies in the workspace."""
    def dfs(node: str, path: List[str], visited: set) -> List[List[str]]:
        if node in path:
            # Found cycle
            cycle_start = path.index(node)
            return [path[cycle_start:] + [node]]
        
        if node in visited:
            return []
        
        visited.add(node)
        cycles = []
        
        for dep in dependency_graph.get(node, []):
            cycles.extend(dfs(dep, path + [node], visited.copy()))
        
        return cycles
    
    all_cycles = []
    visited_global = set()
    
    for node in dependency_graph:
        if node not in visited_global:
            cycles = dfs(node, [], set())
            all_cycles.extend(cycles)
            visited_global.add(node)
    
    return all_cycles


# ============================================================================
# Integration Functions
# ============================================================================

def get_enhanced_projects_with_workspace(repo_path: Path) -> List[Dict]:
    """
    Get enhanced project list with workspace member information.
    
    Integrates workspace detection with core project detection to provide
    a complete view of all projects in a repository.
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        Enhanced project list including workspace members
    """
    repo_path = Path(repo_path).resolve()
    
    try:
        from detection_core import detect_projects
        base_projects = detect_projects(repo_path)
    except ImportError:
        base_projects = []
    
    workspace_analysis = analyze_workspace_structure(repo_path)
    
    if not workspace_analysis["is_workspace"]:
        return base_projects
    
    # Merge base projects with workspace members
    enhanced_projects = []
    
    # Add root-level projects (if any)
    for project in base_projects:
        if project["root"] == "./":
            enhanced_projects.append({
                **project,
                "workspace_role": "root",
                "workspace_type": workspace_analysis["type"]
            })
    
    # Add workspace members
    for member in workspace_analysis["members"]:
        enhanced_projects.append({
            **member,
            "workspace_role": "member",
            "workspace_type": workspace_analysis["type"]
        })
    
    return enhanced_projects


def validate_workspace_structure(repo_path: Path) -> Dict[str, Union[bool, str, List]]:
    """
    Validate workspace structure and identify issues.
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        Validation results with issues and recommendations
    """
    repo_path = Path(repo_path).resolve()
    workspace_analysis = analyze_workspace_structure(repo_path)
    
    if not workspace_analysis["is_workspace"]:
        return {"is_valid": True, "issues": [], "recommendations": []}
    
    issues = []
    recommendations = []
    
    # Check for version inconsistencies
    version_issues = workspace_analysis["analysis"].get("version_consistency", {})
    for name, issue_info in version_issues.items():
        if issue_info.get("inconsistent"):
            issues.append(f"Version inconsistency in {name}: {issue_info['versions']}")
            recommendations.append(f"Synchronize version for {name} across workspace")
    
    # Check for circular dependencies
    circular_deps = workspace_analysis["analysis"].get("circular_dependencies", [])
    for cycle in circular_deps:
        issues.append(f"Circular dependency: {' -> '.join(cycle)}")
        recommendations.append(f"Break circular dependency in {cycle[0]}")
    
    # Check for isolated members
    isolated = workspace_analysis["analysis"].get("isolated_members", [])
    if isolated:
        issues.append(f"Isolated workspace members: {isolated}")
        recommendations.append("Consider if isolated members belong in workspace")
    
    return {
        "is_valid": len(issues) == 0,
        "issues": issues,
        "recommendations": recommendations,
        "workspace_health_score": _calculate_workspace_health_score(workspace_analysis)
    }


def _calculate_workspace_health_score(workspace_analysis: Dict) -> float:
    """Calculate workspace health score (0-100)."""
    if not workspace_analysis["is_workspace"]:
        return 100.0
    
    score = 100.0
    analysis = workspace_analysis["analysis"]
    
    # Deduct for version inconsistencies
    version_issues = len(analysis.get("version_consistency", {}))
    score -= version_issues * 10
    
    # Deduct for circular dependencies
    circular_deps = len(analysis.get("circular_dependencies", []))
    score -= circular_deps * 20
    
    # Deduct for isolated members
    isolated_count = len(analysis.get("isolated_members", []))
    total_members = analysis.get("total_members", 1)
    isolation_ratio = isolated_count / total_members
    score -= isolation_ratio * 30
    
    return max(score, 0.0)


# ============================================================================
# Convenience Functions
# ============================================================================

def get_workspace_summary(repo_path: Path) -> Dict:
    """
    Get concise workspace summary for quick overview.
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        Concise workspace summary
    """
    workspace_analysis = analyze_workspace_structure(repo_path)
    
    if not workspace_analysis["is_workspace"]:
        return {
            "is_workspace": False,
            "summary": "Single-project repository"
        }
    
    analysis = workspace_analysis["analysis"]
    member_count = workspace_analysis["member_count"]
    workspace_type = workspace_analysis["type"]
    
    project_types = list(analysis["project_types"].keys())
    health_score = _calculate_workspace_health_score(workspace_analysis)
    
    summary_parts = [
        f"{member_count} members",
        f"{workspace_type} workspace",
        f"Languages: {', '.join(project_types)}",
        f"Health: {health_score:.0f}%"
    ]
    
    return {
        "is_workspace": True,
        "type": workspace_type,
        "member_count": member_count,
        "health_score": health_score,
        "summary": " | ".join(summary_parts)
    }
