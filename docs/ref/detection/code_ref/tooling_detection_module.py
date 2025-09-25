"""
Tooling Detection Module - Standard Tools and Infrastructure Analysis
Version: 1.0.0
Last Updated: 2025-09-23
Compatible: SEMV v3.0+, Blade Next v1.0+
Dependencies: detection_core.py

Detects standard bin tools, emerging tools, script metadata, and infrastructure gaps.
"""

from pathlib import Path
from typing import List, Dict, Optional, Union, Set
import re
import os
import stat


# ============================================================================
# Standard Bin Tools Detection (Infrastructure Requirements)
# ============================================================================

def detect_standard_bin_tools(repo_path: Path) -> Dict[str, Dict[str, Union[bool, str]]]:
    """
    Detect standard bin tools for infrastructure gap analysis.
    
    Standard tools that MUST be in ./bin/ directory:
    - build.sh: Build automation
    - deploy.sh: Deployment automation  
    - test.sh: Testing automation
    - snap.sh: Benchmarking automation
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        Dictionary of tool status with execution permissions:
        {
            "build.sh": {"exists": True, "path": "./bin/build.sh", "executable": True},
            "deploy.sh": {"exists": False},
            "test.sh": {"exists": True, "path": "./bin/test.sh", "executable": False},
            "snap.sh": {"exists": False}
        }
    """
    repo_path = Path(repo_path).resolve()
    standard_tools = ["build.sh", "deploy.sh", "test.sh", "snap.sh"]
    tools = {}
    
    for tool in standard_tools:
        # Standard tools MUST be in ./bin/ directory
        bin_path = repo_path / "bin" / tool
        if bin_path.exists() and bin_path.is_file():
            # Check if file is executable
            try:
                is_executable = os.access(bin_path, os.X_OK)
            except OSError:
                is_executable = False
            
            tools[tool] = {
                "exists": True, 
                "path": f"./bin/{tool}",
                "executable": is_executable
            }
        else:
            tools[tool] = {"exists": False}
    
    return tools


def analyze_standard_tools_coverage(tools_status: Dict) -> Dict[str, Union[int, float, List[str]]]:
    """
    Analyze standard tools coverage for infrastructure assessment.
    
    Args:
        tools_status: Result from detect_standard_bin_tools()
        
    Returns:
        Coverage analysis:
        {
            "total_tools": 4,
            "tools_present": 2,
            "coverage_percentage": 50.0,
            "missing_tools": ["deploy.sh", "snap.sh"],
            "non_executable": ["test.sh"]
        }
    """
    total_tools = len(tools_status)
    tools_present = sum(1 for tool in tools_status.values() if tool.get("exists", False))
    coverage_percentage = (tools_present / total_tools * 100) if total_tools > 0 else 0.0
    
    missing_tools = [
        tool_name for tool_name, status in tools_status.items() 
        if not status.get("exists", False)
    ]
    
    non_executable = [
        tool_name for tool_name, status in tools_status.items()
        if status.get("exists", False) and not status.get("executable", False)
    ]
    
    return {
        "total_tools": total_tools,
        "tools_present": tools_present,
        "coverage_percentage": coverage_percentage,
        "missing_tools": missing_tools,
        "non_executable": non_executable
    }


# ============================================================================
# Emerging Tools Detection (Modern Development Patterns)
# ============================================================================

def detect_emerging_tools(repo_path: Path) -> Dict[str, Union[bool, List[str], Dict]]:
    """
    Detect emerging development tools and modern patterns.
    
    Current emerging patterns:
    - Build systems: Makefile, CMakeLists.txt, meson.build
    - Task runners: Taskfile.yml, Justfile
    - Python automation: Scripts in ./bin/
    - Container tools: Dockerfile, docker-compose.yml
    - CI/CD: GitHub Actions, GitLab CI
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        Dictionary of emerging tool detection results
    """
    repo_path = Path(repo_path).resolve()
    emerging = {}
    
    # Build systems
    build_systems = _detect_build_systems(repo_path)
    emerging["build_systems"] = build_systems
    
    # Task runners
    task_runners = _detect_task_runners(repo_path)
    emerging["task_runners"] = task_runners
    
    # Python automation scripts
    python_scripts = _detect_python_scripts(repo_path)
    emerging["python_scripts"] = python_scripts
    
    # Container tools
    container_tools = _detect_container_tools(repo_path)
    emerging["container_tools"] = container_tools
    
    # CI/CD systems
    cicd_systems = _detect_cicd_systems(repo_path)
    emerging["cicd_systems"] = cicd_systems
    
    return emerging


def _detect_build_systems(repo_path: Path) -> Dict[str, Union[bool, str]]:
    """Detect various build system files."""
    build_files = {
        "makefile": ["Makefile", "makefile", "GNUmakefile"],
        "cmake": ["CMakeLists.txt"],
        "meson": ["meson.build"],
        "ninja": ["build.ninja"],
        "bazel": ["BUILD", "BUILD.bazel", "WORKSPACE"]
    }
    
    detected = {}
    for system_name, file_patterns in build_files.items():
        found = False
        found_path = None
        
        for pattern in file_patterns:
            file_path = repo_path / pattern
            if file_path.exists():
                found = True
                found_path = f"./{pattern}"
                break
        
        if found:
            detected[system_name] = {"exists": True, "path": found_path}
        else:
            detected[system_name] = {"exists": False}
    
    return detected


def _detect_task_runners(repo_path: Path) -> Dict[str, Union[bool, str]]:
    """Detect task runner configurations."""
    task_files = {
        "taskfile": ["Taskfile.yml", "Taskfile.yaml"],
        "justfile": ["Justfile", "justfile"],
        "invoke": ["tasks.py"],
        "npm_scripts": ["package.json"]  # Will check for scripts section
    }
    
    detected = {}
    for runner_name, file_patterns in task_files.items():
        found = False
        found_path = None
        
        for pattern in file_patterns:
            file_path = repo_path / pattern
            if file_path.exists():
                # Special handling for npm scripts
                if runner_name == "npm_scripts":
                    if _has_npm_scripts(file_path):
                        found = True
                        found_path = f"./{pattern}"
                else:
                    found = True
                    found_path = f"./{pattern}"
                break
        
        if found:
            detected[runner_name] = {"exists": True, "path": found_path}
        else:
            detected[runner_name] = {"exists": False}
    
    return detected


def _detect_python_scripts(repo_path: Path) -> List[str]:
    """Find Python automation scripts in bin directory."""
    bin_dir = repo_path / "bin"
    python_scripts = []
    
    if bin_dir.exists() and bin_dir.is_dir():
        for script in bin_dir.glob("*.py"):
            if script.is_file():
                python_scripts.append(f"./bin/{script.name}")
    
    return python_scripts


def _detect_container_tools(repo_path: Path) -> Dict[str, Union[bool, str]]:
    """Detect containerization tools."""
    container_files = {
        "dockerfile": ["Dockerfile", "dockerfile", "Dockerfile.dev"],
        "docker_compose": ["docker-compose.yml", "docker-compose.yaml", "compose.yml"],
        "podman": ["Containerfile"],
        "k8s": ["k8s", "kubernetes"],  # Directory check
        "helm": ["Chart.yaml", "values.yaml"]
    }
    
    detected = {}
    for tool_name, patterns in container_files.items():
        found = False
        found_path = None
        
        for pattern in patterns:
            path = repo_path / pattern
            if path.exists():
                if tool_name == "k8s":
                    # Check for k8s directory
                    if path.is_dir():
                        found = True
                        found_path = f"./{pattern}/"
                else:
                    found = True
                    found_path = f"./{pattern}"
                break
        
        if found:
            detected[tool_name] = {"exists": True, "path": found_path}
        else:
            detected[tool_name] = {"exists": False}
    
    return detected


def _detect_cicd_systems(repo_path: Path) -> Dict[str, Union[bool, str, List[str]]]:
    """Detect CI/CD system configurations."""
    cicd_patterns = {
        "github_actions": ".github/workflows",
        "gitlab_ci": [".gitlab-ci.yml", ".gitlab-ci.yaml"],
        "jenkins": ["Jenkinsfile", "jenkins.yaml"],
        "travis": [".travis.yml"],
        "circleci": [".circleci/config.yml"],
        "azure_pipelines": ["azure-pipelines.yml", ".azure/pipelines"]
    }
    
    detected = {}
    for system_name, patterns in cicd_patterns.items():
        found = False
        found_paths = []
        
        if system_name == "github_actions":
            # Special handling for GitHub Actions (directory with workflow files)
            workflows_dir = repo_path / patterns
            if workflows_dir.exists() and workflows_dir.is_dir():
                workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
                if workflow_files:
                    found = True
                    found_paths = [f"./.github/workflows/{f.name}" for f in workflow_files]
        else:
            # Check for specific files
            if isinstance(patterns, str):
                patterns = [patterns]
            
            for pattern in patterns:
                path = repo_path / pattern
                if path.exists():
                    found = True
                    if path.is_dir():
                        found_paths.append(f"./{pattern}/")
                    else:
                        found_paths.append(f"./{pattern}")
        
        if found:
            detected[system_name] = {
                "exists": True, 
                "paths": found_paths if len(found_paths) > 1 else found_paths[0] if found_paths else None
            }
        else:
            detected[system_name] = {"exists": False}
    
    return detected


def _has_npm_scripts(package_json_path: Path) -> bool:
    """Check if package.json has a scripts section."""
    try:
        import json
        content = package_json_path.read_text(encoding='utf-8')
        data = json.loads(content)
        scripts = data.get('scripts', {})
        return isinstance(scripts, dict) and len(scripts) > 0
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return False


# ============================================================================
# Script Discovery and Metadata
# ============================================================================

def detect_script_metadata(repo_path: Path) -> Dict[str, Union[str, List[str], None]]:
    """
    Detect general script directories and files for discovery metadata.
    
    Finds:
    - bin/ directory existence and contents
    - Root-level scripts (excluding standard tools and generated files)
    - Script directories (./scripts, ./tools, etc.)
    - Script file analysis (shebang detection, permissions)
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        Dictionary of comprehensive script metadata
    """
    repo_path = Path(repo_path).resolve()
    
    # Analyze bin directory
    bin_analysis = _analyze_bin_directory(repo_path)
    
    # Find root-level scripts
    root_scripts = _find_root_scripts(repo_path)
    
    # Find script directories
    script_directories = _find_script_directories(repo_path)
    
    # Analyze script types and patterns
    script_analysis = _analyze_script_patterns(repo_path, root_scripts, script_directories)
    
    return {
        "bin_directory": bin_analysis,
        "root_scripts": root_scripts,
        "script_directories": script_directories,
        "script_analysis": script_analysis
    }


def _analyze_bin_directory(repo_path: Path) -> Optional[Dict]:
    """Analyze bin directory contents and structure."""
    bin_dir = repo_path / "bin"
    if not bin_dir.exists() or not bin_dir.is_dir():
        return None
    
    scripts = []
    script_types = {"shell": 0, "python": 0, "other": 0}
    
    for item in bin_dir.iterdir():
        if item.is_file():
            script_info = {
                "name": item.name,
                "path": f"./bin/{item.name}",
                "executable": os.access(item, os.X_OK),
                "type": _detect_script_type(item)
            }
            scripts.append(script_info)
            script_types[script_info["type"]] += 1
    
    return {
        "path": "./bin",
        "script_count": len(scripts),
        "scripts": scripts,
        "script_types": script_types
    }


def _find_root_scripts(repo_path: Path) -> List[Dict[str, Union[str, bool]]]:
    """Find and analyze root-level scripts."""
    # Exclude standard tools and common non-script files
    excluded_files = {
        "build.sh", "deploy.sh", "test.sh", "snap.sh",  # Standard tools
        "README.md", "LICENSE", "CHANGELOG.md"  # Documentation
    }
    
    root_scripts = []
    
    # Look for executable scripts in root
    for item in repo_path.iterdir():
        if (item.is_file() and 
            item.name not in excluded_files and 
            _is_script_file(item)):
            
            # Skip generated files
            try:
                from detection_core import is_generated_file
                if is_generated_file(item):
                    continue
            except ImportError:
                # Fallback if detection_core not available
                if _is_generated_file_fallback(item):
                    continue
            
            script_info = {
                "name": item.name,
                "path": f"./{item.name}",
                "executable": os.access(item, os.X_OK),
                "type": _detect_script_type(item)
            }
            root_scripts.append(script_info)
    
    return root_scripts


def _find_script_directories(repo_path: Path) -> List[Dict[str, Union[str, int]]]:
    """Find directories containing scripts."""
    script_dir_candidates = ["scripts", "tools", "util", "utils", "automation"]
    script_directories = []
    
    for item in repo_path.iterdir():
        if (item.is_dir() and 
            item.name in script_dir_candidates):
            
            script_count = len([f for f in item.iterdir() 
                              if f.is_file() and _is_script_file(f)])
            
            if script_count > 0:
                script_directories.append({
                    "name": item.name,
                    "path": f"./{item.name}",
                    "script_count": script_count
                })
    
    return script_directories


def _analyze_script_patterns(repo_path: Path, root_scripts: List, script_dirs: List) -> Dict:
    """Analyze overall script patterns and organization."""
    total_scripts = len(root_scripts) + sum(d["script_count"] for d in script_dirs)
    
    # Count script types across all locations
    type_counts = {"shell": 0, "python": 0, "other": 0}
    for script in root_scripts:
        type_counts[script["type"]] += 1
    
    # Check for common script organization patterns
    has_organized_scripts = len(script_dirs) > 0
    has_bin_directory = (repo_path / "bin").exists()
    
    organization_pattern = "none"
    if has_bin_directory and has_organized_scripts:
        organization_pattern = "well_organized"
    elif has_bin_directory:
        organization_pattern = "bin_only"
    elif has_organized_scripts:
        organization_pattern = "directories_only"
    elif len(root_scripts) > 0:
        organization_pattern = "root_scattered"
    
    return {
        "total_scripts": total_scripts,
        "script_types": type_counts,
        "organization_pattern": organization_pattern,
        "has_bin_directory": has_bin_directory,
        "has_script_directories": has_organized_scripts
    }


def _is_script_file(file_path: Path) -> bool:
    """Check if file appears to be a script."""
    # Check by extension
    script_extensions = {".sh", ".bash", ".py", ".pl", ".rb", ".js", ".ts"}
    if file_path.suffix.lower() in script_extensions:
        return True
    
    # Check by shebang
    try:
        with file_path.open('rb') as f:
            first_line = f.readline(100)  # Read first 100 bytes
            if first_line.startswith(b'#!'):
                return True
    except (OSError, UnicodeDecodeError):
        pass
    
    return False


def _detect_script_type(file_path: Path) -> str:
    """Detect script type by extension and shebang."""
    # Check by extension first
    ext = file_path.suffix.lower()
    if ext in {".sh", ".bash"}:
        return "shell"
    elif ext in {".py"}:
        return "python"
    elif ext in {".pl"}:
        return "perl"
    elif ext in {".rb"}:
        return "ruby"
    elif ext in {".js", ".ts"}:
        return "javascript"
    
    # Check by shebang
    try:
        with file_path.open('r', encoding='utf-8') as f:
            first_line = f.readline().lower()
            if 'python' in first_line:
                return "python"
            elif any(shell in first_line for shell in ['bash', 'sh', 'zsh']):
                return "shell"
    except (OSError, UnicodeDecodeError):
        pass
    
    return "other"


def _is_generated_file_fallback(file_path: Path) -> bool:
    """Fallback generated file check if detection_core not available."""
    try:
        with file_path.open('r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i > 10:  # Only check first 10 lines
                    break
                if '# generated' in line.lower():
                    return True
        return False
    except (OSError, UnicodeDecodeError):
        return False


# ============================================================================
# Infrastructure Gap Analysis
# ============================================================================

def detect_dirty_directories(repo_path: Path) -> List[Dict[str, Union[str, int]]]:
    """
    Find build artifacts and dependency directories for cleanup analysis.
    
    Detects common directories that should be in .gitignore:
    - Build artifacts: build/, dist/, target/
    - Dependencies: node_modules/, .venv/, vendor/
    - Caches: __pycache__/, .pytest_cache/, .tox/
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        List of dirty directories with size information
    """
    repo_path = Path(repo_path).resolve()
    
    dirty_patterns = {
        # Build artifacts
        "build": ["build", "dist", "out", ".next", ".nuxt"],
        "target": ["target"],  # Rust
        "coverage": [".coverage", ".nyc_output", "coverage"],
        
        # Dependencies
        "node_modules": ["node_modules"],
        "python_venv": [".venv", "venv", ".virtualenv"],
        "vendor": ["vendor"],  # Go, PHP
        
        # Caches and temporary
        "python_cache": ["__pycache__", ".pytest_cache", ".tox", ".mypy_cache"],
        "misc_cache": [".cache", ".tmp", "tmp"]
    }
    
    found_dirty = []
    
    for category, patterns in dirty_patterns.items():
        for pattern in patterns:
            dir_path = repo_path / pattern
            if dir_path.exists() and dir_path.is_dir():
                try:
                    # Calculate directory size (approximate)
                    size_mb = _calculate_directory_size(dir_path)
                    found_dirty.append({
                        "name": pattern,
                        "path": f"./{pattern}",
                        "category": category,
                        "size_mb": size_mb
                    })
                except OSError:
                    found_dirty.append({
                        "name": pattern,
                        "path": f"./{pattern}",
                        "category": category,
                        "size_mb": 0
                    })
    
    return found_dirty


def _calculate_directory_size(directory: Path) -> float:
    """Calculate approximate directory size in MB."""
    total_size = 0
    try:
        for item in directory.rglob('*'):
            if item.is_file():
                total_size += item.stat().st_size
    except (OSError, PermissionError):
        pass
    
    return round(total_size / (1024 * 1024), 2)  # Convert to MB


def analyze_infrastructure_gaps(repo_path: Path) -> Dict[str, Union[float, List[str], Dict]]:
    """
    Comprehensive infrastructure gap analysis.
    
    Analyzes:
    - Standard tool coverage
    - Modern tooling adoption
    - Script organization quality
    - Cleanup opportunities
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        Infrastructure assessment report
    """
    # Get all detection results
    standard_tools = detect_standard_bin_tools(repo_path)
    tools_coverage = analyze_standard_tools_coverage(standard_tools)
    emerging_tools = detect_emerging_tools(repo_path)
    script_metadata = detect_script_metadata(repo_path)
    dirty_dirs = detect_dirty_directories(repo_path)
    
    # Calculate overall infrastructure score
    infrastructure_score = _calculate_infrastructure_score(
        tools_coverage, emerging_tools, script_metadata
    )
    
    # Generate recommendations
    recommendations = _generate_infrastructure_recommendations(
        tools_coverage, emerging_tools, script_metadata, dirty_dirs
    )
    
    return {
        "infrastructure_score": infrastructure_score,
        "standard_tools_coverage": tools_coverage["coverage_percentage"],
        "missing_standard_tools": tools_coverage["missing_tools"],
        "emerging_tools_count": _count_emerging_tools(emerging_tools),
        "script_organization": script_metadata.get("script_analysis", {}).get("organization_pattern", "none"),
        "cleanup_opportunities": len(dirty_dirs),
        "cleanup_size_mb": sum(d["size_mb"] for d in dirty_dirs),
        "recommendations": recommendations
    }


def _calculate_infrastructure_score(tools_coverage: Dict, emerging_tools: Dict, script_metadata: Dict) -> float:
    """Calculate overall infrastructure maturity score (0-100)."""
    score = 0.0
    
    # Standard tools coverage (40% of score)
    score += tools_coverage["coverage_percentage"] * 0.4
    
    # Emerging tools adoption (30% of score)
    emerging_count = _count_emerging_tools(emerging_tools)
    emerging_score = min(emerging_count * 10, 30)  # Max 30 points for emerging tools
    score += emerging_score
    
    # Script organization (30% of score)
    organization = script_metadata.get("script_analysis", {}).get("organization_pattern", "none")
    org_scores = {
        "well_organized": 30,
        "bin_only": 20,
        "directories_only": 15,
        "root_scattered": 5,
        "none": 0
    }
    score += org_scores.get(organization, 0)
    
    return round(min(score, 100.0), 1)


def _count_emerging_tools(emerging_tools: Dict) -> int:
    """Count how many emerging tools are present."""
    count = 0
    for category in emerging_tools.values():
        if isinstance(category, dict):
            for tool_info in category.values():
                if isinstance(tool_info, dict) and tool_info.get("exists", False):
                    count += 1
        elif isinstance(category, list):
            count += len(category)
    
    return count


def _generate_infrastructure_recommendations(tools_coverage: Dict, emerging_tools: Dict, 
                                           script_metadata: Dict, dirty_dirs: List) -> List[str]:
    """Generate actionable infrastructure improvement recommendations."""
    recommendations = []
    
    # Standard tools recommendations
    if tools_coverage["coverage_percentage"] < 100:
        missing = tools_coverage["missing_tools"]
        recommendations.append(f"Add missing standard tools: {', '.join(missing)}")
    
    if tools_coverage["non_executable"]:
        non_exec = tools_coverage["non_executable"]
        recommendations.append(f"Make tools executable: {', '.join(non_exec)}")
    
    # Modern tooling recommendations
    build_systems = emerging_tools.get("build_systems", {})
    if not any(tool.get("exists", False) for tool in build_systems.values()):
        recommendations.append("Consider adding a build system (Makefile, Taskfile, etc.)")
    
    # Script organization recommendations
    org_pattern = script_metadata.get("script_analysis", {}).get("organization_pattern", "none")
    if org_pattern == "root_scattered":
        recommendations.append("Organize scripts into ./bin/ or ./scripts/ directories")
    elif org_pattern == "none":
        recommendations.append("Consider adding automation scripts for common tasks")
    
    # Cleanup recommendations
    if len(dirty_dirs) > 0:
        total_size = sum(d["size_mb"] for d in dirty_dirs)
        if total_size > 100:  # More than 100MB
            recommendations.append(f"Clean up {len(dirty_dirs)} build/cache directories ({total_size:.1f}MB)")
    
    return recommendations


# ============================================================================
# Integration Functions
# ============================================================================

def get_complete_tooling_analysis(repo_path: Path) -> Dict:
    """
    Get comprehensive tooling analysis for repository.
    
    Single entry point for all tooling detection and analysis.
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        Complete tooling analysis dictionary
    """
    repo_path = Path(repo_path).resolve()
    
    return {
        "standard_bin_tools": detect_standard_bin_tools(repo_path),
        "emerging_tools": detect_emerging_tools(repo_path),
        "script_metadata": detect_script_metadata(repo_path),
        "dirty_directories": detect_dirty_directories(repo_path),
        "infrastructure_analysis": analyze_infrastructure_gaps(repo_path)
    }
