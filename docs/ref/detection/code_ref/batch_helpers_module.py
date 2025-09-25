"""
Batch Helpers Module - Multi-Repository Processing and Caching
Version: 1.0.0
Last Updated: 2025-09-23
Compatible: SEMV v3.0+, Blade Next v1.0+
Dependencies: detection_core.py, tooling_detection.py, workspace_detection.py, projectrc_config.py

Provides batch processing, caching, and export capabilities for multi-repository operations.
"""

from pathlib import Path
from typing import List, Dict, Optional, Union, Set, Tuple, Iterator
import json
import csv
import time
import hashlib
import os
import threading
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess


# ============================================================================
# XDG+ Directory Management
# ============================================================================

def get_cache_directory() -> Path:
    """
    Get XDG+ compliant cache directory for repository data.
    
    Returns:
        Path to cache directory: ~/.local/data/repos/
    """
    home = Path.home()
    
    # Check for XDG_DATA_HOME environment variable
    xdg_data_home = os.environ.get('XDG_DATA_HOME')
    if xdg_data_home:
        base_dir = Path(xdg_data_home)
    else:
        base_dir = home / '.local' / 'data'
    
    cache_dir = base_dir / 'repos'
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    return cache_dir


def get_repo_hash(repo_path: Path) -> str:
    """
    Generate consistent hash for repository path.
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        SHA256 hash of absolute repository path
    """
    abs_path = Path(repo_path).resolve()
    return hashlib.sha256(str(abs_path).encode('utf-8')).hexdigest()[:16]


def get_repo_cache_file(repo_path: Path) -> Path:
    """
    Get cache file path for specific repository.
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        Path to JSON cache file for repository
    """
    cache_dir = get_cache_directory()
    repo_hash = get_repo_hash(repo_path)
    return cache_dir / f"{repo_hash}.json"


def get_index_file() -> Path:
    """
    Get path to repository index TSV file.
    
    Returns:
        Path to repository index TSV file
    """
    cache_dir = get_cache_directory()
    return cache_dir / "repository_index.tsv"


# ============================================================================
# Repository Discovery and Crawling
# ============================================================================

def crawl_repositories(root_path: Path, 
                      filters: Optional[Dict[str, Union[bool, List[str], int]]] = None,
                      max_depth: int = 3) -> List[Path]:
    """
    Discover repositories within a directory tree.
    
    Args:
        root_path: Root directory to search for repositories
        filters: Discovery filters:
            - exclude_archived: Skip archived/deprecated repositories
            - include_types: Only include specific repository types
            - exclude_paths: Skip specific path patterns
            - min_age_days: Skip repositories newer than X days
            - max_age_days: Skip repositories older than X days
        max_depth: Maximum directory depth to search
        
    Returns:
        List of repository paths found
    """
    root_path = Path(root_path).resolve()
    filters = filters or {}
    
    repositories = []
    visited_dirs = set()
    
    def _crawl_directory(current_path: Path, depth: int) -> None:
        if depth > max_depth:
            return
        
        # Avoid infinite loops with symlinks
        try:
            real_path = current_path.resolve()
            if real_path in visited_dirs:
                return
            visited_dirs.add(real_path)
        except OSError:
            return
        
        # Check if current directory is a repository
        if _is_repository(current_path):
            if _passes_filters(current_path, filters):
                repositories.append(current_path)
            return  # Don't search inside repositories
        
        # Search subdirectories
        try:
            for item in current_path.iterdir():
                if item.is_dir() and not _should_skip_directory(item):
                    _crawl_directory(item, depth + 1)
        except (OSError, PermissionError):
            pass
    
    _crawl_directory(root_path, 0)
    return sorted(repositories)


def _is_repository(path: Path) -> bool:
    """Check if directory is a repository (git or gitsim)."""
    return (path / ".git").exists() or (path / ".gitsim").exists()


def _should_skip_directory(path: Path) -> bool:
    """Check if directory should be skipped during crawling."""
    skip_patterns = {
        # Build artifacts
        'node_modules', 'target', 'build', 'dist', '.next', '.nuxt',
        # Version control internals
        '.git', '.svn', '.hg', '.gitsim',
        # IDE and editor files
        '.vscode', '.idea', '__pycache__', '.pytest_cache',
        # Virtual environments
        '.venv', 'venv', '.virtualenv',
        # System directories
        '.Trash', '.cache', '.tmp', 'tmp'
    }
    
    return path.name in skip_patterns or path.name.startswith('.')


def _passes_filters(repo_path: Path, filters: Dict) -> bool:
    """Check if repository passes discovery filters."""
    # Exclude archived repositories
    if filters.get('exclude_archived', False):
        if _is_archived_repository(repo_path):
            return False
    
    # Check repository age
    min_age_days = filters.get('min_age_days')
    max_age_days = filters.get('max_age_days')
    
    if min_age_days or max_age_days:
        repo_age = _get_repository_age_days(repo_path)
        if repo_age is not None:
            if min_age_days and repo_age < min_age_days:
                return False
            if max_age_days and repo_age > max_age_days:
                return False
    
    # Check path exclusions
    exclude_paths = filters.get('exclude_paths', [])
    for exclude_pattern in exclude_paths:
        if exclude_pattern in str(repo_path):
            return False
    
    return True


def _is_archived_repository(repo_path: Path) -> bool:
    """Check if repository appears to be archived or deprecated."""
    # Check for archive indicators in path
    archive_indicators = ['archive', 'archived', 'deprecated', 'legacy', 'old']
    path_parts = str(repo_path).lower().split('/')
    
    for indicator in archive_indicators:
        if any(indicator in part for part in path_parts):
            return True
    
    # Check for .projectrc maintenance status
    try:
        from projectrc_config import load_projectrc
        config = load_projectrc(repo_path)
        if config:
            status = config.get('metadata', {}).get('maintenance_status')
            return status in ['deprecated', 'archived']
    except ImportError:
        pass
    
    return False


def _get_repository_age_days(repo_path: Path) -> Optional[int]:
    """Get repository age in days since first commit."""
    try:
        # Try to get first commit date
        result = subprocess.run([
            'git', 'log', '--reverse', '--format=%ct', '--max-count=1'
        ], cwd=repo_path, capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0 and result.stdout.strip():
            first_commit_timestamp = int(result.stdout.strip())
            first_commit_date = datetime.fromtimestamp(first_commit_timestamp)
            age_days = (datetime.now() - first_commit_date).days
            return age_days
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, ValueError):
        pass
    
    # Fallback to directory modification time
    try:
        mtime = repo_path.stat().st_mtime
        mtime_date = datetime.fromtimestamp(mtime)
        age_days = (datetime.now() - mtime_date).days
        return age_days
    except OSError:
        pass
    
    return None


# ============================================================================
# Batch Detection Processing
# ============================================================================

def batch_detect_repositories(repo_paths: List[Path], 
                             max_workers: int = 4,
                             use_cache: bool = True,
                             cache_max_age_hours: int = 24) -> Dict[str, Dict]:
    """
    Perform batch detection across multiple repositories.
    
    Args:
        repo_paths: List of repository paths to analyze
        max_workers: Maximum number of concurrent workers
        use_cache: Whether to use cached results
        cache_max_age_hours: Maximum age of cached results in hours
        
    Returns:
        Dictionary mapping repository paths to detection results:
        {
            "/path/to/repo1": {detection_result},
            "/path/to/repo2": {detection_result}
        }
    """
    results = {}
    
    # Filter repositories that need processing
    repos_to_process = []
    for repo_path in repo_paths:
        if use_cache:
            cached_result = _load_cached_result(repo_path, cache_max_age_hours)
            if cached_result:
                results[str(repo_path)] = cached_result
                continue
        
        repos_to_process.append(repo_path)
    
    if not repos_to_process:
        return results
    
    # Process repositories concurrently
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit detection tasks
        future_to_repo = {
            executor.submit(_detect_single_repository, repo_path): repo_path
            for repo_path in repos_to_process
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_repo):
            repo_path = future_to_repo[future]
            try:
                detection_result = future.result()
                results[str(repo_path)] = detection_result
                
                # Cache the result
                if use_cache:
                    _save_cached_result(repo_path, detection_result)
                    
            except Exception as e:
                # Create error result
                error_result = {
                    "repository": {"path": str(repo_path), "type": "error"},
                    "projects": [],
                    "error": str(e),
                    "meta": {
                        "detector_version": "1.0.0",
                        "detection_time": datetime.now().isoformat(),
                        "detection_success": False
                    }
                }
                results[str(repo_path)] = error_result
    
    return results


def _detect_single_repository(repo_path: Path) -> Dict:
    """Detect single repository with comprehensive analysis."""
    start_time = time.time()
    
    try:
        # Import detection modules
        from detection_core import get_repository_context
        from tooling_detection import get_complete_tooling_analysis
        from workspace_detection import analyze_workspace_structure
        from projectrc_config import get_enhanced_detection_with_config
        
        # Get enhanced detection with configuration
        detection_result = get_enhanced_detection_with_config(repo_path)
        
        # Add tooling analysis
        tooling_analysis = get_complete_tooling_analysis(repo_path)
        detection_result["tooling_analysis"] = tooling_analysis
        
        # Add workspace analysis if not already present
        if not detection_result.get("workspace", {}).get("is_workspace"):
            workspace_analysis = analyze_workspace_structure(repo_path)
            detection_result["workspace"] = workspace_analysis
        
        # Update metadata
        detection_duration = (time.time() - start_time) * 1000  # Convert to milliseconds
        detection_result["meta"].update({
            "detection_duration_ms": round(detection_duration, 2),
            "detection_success": True,
            "batch_processed": True
        })
        
        return detection_result
        
    except ImportError as e:
        # Fallback for missing modules
        return {
            "repository": {
                "path": str(repo_path),
                "type": "unknown"
            },
            "projects": [],
            "error": f"Module import error: {e}",
            "meta": {
                "detector_version": "1.0.0",
                "detection_time": datetime.now().isoformat(),
                "detection_duration_ms": (time.time() - start_time) * 1000,
                "detection_success": False
            }
        }


# ============================================================================
# Caching System
# ============================================================================

def _load_cached_result(repo_path: Path, max_age_hours: int) -> Optional[Dict]:
    """Load cached detection result if valid."""
    cache_file = get_repo_cache_file(repo_path)
    
    if not cache_file.exists():
        return None
    
    try:
        # Check cache file age
        cache_mtime = cache_file.stat().st_mtime
        cache_age = (time.time() - cache_mtime) / 3600  # Convert to hours
        
        if cache_age > max_age_hours:
            return None
        
        # Check if repository has been modified since cache
        repo_mtime = _get_repository_mtime(repo_path)
        if repo_mtime and repo_mtime > cache_mtime:
            return None
        
        # Load and return cached result
        content = cache_file.read_text(encoding='utf-8')
        cached_result = json.loads(content)
        
        # Add cache metadata
        cached_result["meta"]["from_cache"] = True
        cached_result["meta"]["cache_age_hours"] = round(cache_age, 2)
        
        return cached_result
        
    except (OSError, json.JSONDecodeError, KeyError):
        # Remove invalid cache file
        try:
            cache_file.unlink()
        except OSError:
            pass
        return None


def _save_cached_result(repo_path: Path, detection_result: Dict) -> None:
    """Save detection result to cache."""
    cache_file = get_repo_cache_file(repo_path)
    
    try:
        # Remove cache metadata before saving
        result_to_save = detection_result.copy()
        if "meta" in result_to_save:
            result_to_save["meta"].pop("from_cache", None)
            result_to_save["meta"].pop("cache_age_hours", None)
        
        # Save to cache
        cache_content = json.dumps(result_to_save, indent=2, default=str)
        cache_file.write_text(cache_content, encoding='utf-8')
        
    except (OSError, TypeError):
        pass  # Ignore cache save errors


def _get_repository_mtime(repo_path: Path) -> Optional[float]:
    """Get repository modification time (latest of .git, project files)."""
    try:
        max_mtime = 0.0
        
        # Check .git directory
        git_dir = repo_path / ".git"
        if git_dir.exists():
            for item in git_dir.rglob("*"):
                if item.is_file():
                    max_mtime = max(max_mtime, item.stat().st_mtime)
        
        # Check main project files
        project_files = [
            "Cargo.toml", "package.json", "pyproject.toml", "setup.py",
            ".projectrc", "Makefile", "build.sh"
        ]
        
        for filename in project_files:
            file_path = repo_path / filename
            if file_path.exists():
                max_mtime = max(max_mtime, file_path.stat().st_mtime)
        
        return max_mtime if max_mtime > 0 else None
        
    except (OSError, PermissionError):
        return None


def clear_cache(repo_path: Optional[Path] = None) -> int:
    """
    Clear cached detection results.
    
    Args:
        repo_path: Specific repository to clear cache for, or None for all
        
    Returns:
        Number of cache files removed
    """
    cache_dir = get_cache_directory()
    removed_count = 0
    
    if repo_path:
        # Clear cache for specific repository
        cache_file = get_repo_cache_file(repo_path)
        if cache_file.exists():
            try:
                cache_file.unlink()
                removed_count = 1
            except OSError:
                pass
    else:
        # Clear all cache files
        try:
            for cache_file in cache_dir.glob("*.json"):
                try:
                    cache_file.unlink()
                    removed_count += 1
                except OSError:
                    pass
        except OSError:
            pass
    
    return removed_count


def get_cache_stats() -> Dict[str, Union[int, float, str]]:
    """
    Get cache statistics.
    
    Returns:
        Dictionary with cache statistics
    """
    cache_dir = get_cache_directory()
    
    try:
        cache_files = list(cache_dir.glob("*.json"))
        total_files = len(cache_files)
        
        if total_files == 0:
            return {
                "total_files": 0,
                "total_size_mb": 0.0,
                "oldest_cache": None,
                "newest_cache": None,
                "cache_directory": str(cache_dir)
            }
        
        # Calculate total size
        total_size = sum(f.stat().st_size for f in cache_files)
        total_size_mb = total_size / (1024 * 1024)
        
        # Find oldest and newest cache files
        cache_times = [f.stat().st_mtime for f in cache_files]
        oldest_time = min(cache_times)
        newest_time = max(cache_times)
        
        oldest_cache = datetime.fromtimestamp(oldest_time).isoformat()
        newest_cache = datetime.fromtimestamp(newest_time).isoformat()
        
        return {
            "total_files": total_files,
            "total_size_mb": round(total_size_mb, 2),
            "oldest_cache": oldest_cache,
            "newest_cache": newest_cache,
            "cache_directory": str(cache_dir)
        }
        
    except OSError:
        return {
            "total_files": 0,
            "total_size_mb": 0.0,
            "oldest_cache": None,
            "newest_cache": None,
            "cache_directory": str(cache_dir),
            "error": "Unable to access cache directory"
        }


# ============================================================================
# TSV Export for Blade Integration
# ============================================================================

def export_repository_index(detection_results: Dict[str, Dict], 
                           output_file: Optional[Path] = None) -> Path:
    """
    Export repository detection results to TSV format for Blade analysis.
    
    Args:
        detection_results: Results from batch_detect_repositories()
        output_file: Output TSV file path (default: cache directory)
        
    Returns:
        Path to created TSV file
    """
    if output_file is None:
        output_file = get_index_file()
    
    # Define TSV columns
    columns = [
        'repo_path', 'repo_name', 'repository_type', 'project_types', 
        'primary_version', 'workspace_type', 'member_count',
        'has_build', 'has_deploy', 'has_test', 'has_snap',
        'has_makefile', 'script_count', 'dirty_dir_count', 'dirty_size_mb',
        'team', 'primary_language', 'maintenance_status',
        'infrastructure_score', 'detection_success', 'last_updated'
    ]
    
    # Generate TSV rows
    rows = []
    for repo_path_str, result in detection_results.items():
        row = _generate_tsv_row(repo_path_str, result)
        rows.append(row)
    
    # Sort by repository path for consistent output
    rows.sort(key=lambda r: r['repo_path'])
    
    # Write TSV file
    try:
        with output_file.open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns, delimiter='\t')
            writer.writeheader()
            writer.writerows(rows)
        
        return output_file
        
    except OSError as e:
        raise RuntimeError(f"Failed to write TSV file: {e}")


def _generate_tsv_row(repo_path_str: str, detection_result: Dict) -> Dict[str, str]:
    """Generate TSV row from detection result."""
    repo_path = Path(repo_path_str)
    repository = detection_result.get('repository', {})
    projects = detection_result.get('projects', [])
    workspace = detection_result.get('workspace', {})
    config = detection_result.get('configuration', {}).get('config', {})
    tooling = detection_result.get('tooling_analysis', {})
    meta = detection_result.get('meta', {})
    
    # Extract basic repository info
    repo_name = repo_path.name
    repository_type = repository.get('type', 'unknown')
    
    # Extract project types and primary version
    project_types = [p.get('type', '') for p in projects]
    project_types_str = ','.join(project_types) if project_types else 'none'
    
    # Get primary version (first project with version, or highest version)
    primary_version = 'none'
    if projects:
        versions = [p.get('version') for p in projects if p.get('version')]
        if versions:
            try:
                from detection_core import get_highest_version
                primary_version = get_highest_version(versions) or versions[0]
            except ImportError:
                primary_version = versions[0]
    
    # Extract workspace info
    workspace_type = workspace.get('type', 'none') if workspace.get('is_workspace') else 'none'
    member_count = workspace.get('member_count', 0)
    
    # Extract standard tools
    standard_tools = tooling.get('standard_bin_tools', {})
    has_build = str(standard_tools.get('build.sh', {}).get('exists', False)).lower()
    has_deploy = str(standard_tools.get('deploy.sh', {}).get('exists', False)).lower()
    has_test = str(standard_tools.get('test.sh', {}).get('exists', False)).lower()
    has_snap = str(standard_tools.get('snap.sh', {}).get('exists', False)).lower()
    
    # Extract emerging tools
    emerging_tools = tooling.get('emerging_tools', {})
    build_systems = emerging_tools.get('build_systems', {})
    has_makefile = str(build_systems.get('makefile', {}).get('exists', False)).lower()
    
    # Extract script info
    script_metadata = tooling.get('script_metadata', {})
    script_analysis = script_metadata.get('script_analysis', {})
    script_count = script_analysis.get('total_scripts', 0)
    
    # Extract dirty directories
    dirty_dirs = tooling.get('dirty_directories', [])
    dirty_dir_count = len(dirty_dirs)
    dirty_size_mb = sum(d.get('size_mb', 0) for d in dirty_dirs)
    
    # Extract metadata from config
    metadata = config.get('metadata', {}) if config else {}
    team = metadata.get('team', '')
    primary_language = metadata.get('primary_language', '')
    maintenance_status = metadata.get('maintenance_status', 'unknown')
    
    # Extract infrastructure score
    infra_analysis = tooling.get('infrastructure_analysis', {})
    infrastructure_score = infra_analysis.get('infrastructure_score', 0)
    
    # Extract detection metadata
    detection_success = str(meta.get('detection_success', True)).lower()
    detection_time = meta.get('detection_time', '')
    
    return {
        'repo_path': repo_path_str,
        'repo_name': repo_name,
        'repository_type': repository_type,
        'project_types': project_types_str,
        'primary_version': primary_version,
        'workspace_type': workspace_type,
        'member_count': str(member_count),
        'has_build': has_build,
        'has_deploy': has_deploy,
        'has_test': has_test,
        'has_snap': has_snap,
        'has_makefile': has_makefile,
        'script_count': str(script_count),
        'dirty_dir_count': str(dirty_dir_count),
        'dirty_size_mb': f"{dirty_size_mb:.1f}",
        'team': team,
        'primary_language': primary_language,
        'maintenance_status': maintenance_status,
        'infrastructure_score': f"{infrastructure_score:.1f}",
        'detection_success': detection_success,
        'last_updated': detection_time
    }


def load_repository_index(tsv_file: Optional[Path] = None) -> List[Dict[str, str]]:
    """
    Load repository index from TSV file.
    
    Args:
        tsv_file: TSV file path (default: cache directory)
        
    Returns:
        List of repository records as dictionaries
    """
    if tsv_file is None:
        tsv_file = get_index_file()
    
    if not tsv_file.exists():
        return []
    
    try:
        with tsv_file.open('r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            return list(reader)
    except (OSError, csv.Error):
        return []


# ============================================================================
# Query and Analysis Functions
# ============================================================================

def query_repositories(filters: Optional[Dict[str, Union[str, List[str], bool]]] = None) -> List[Dict[str, str]]:
    """
    Query repository index with filters.
    
    Args:
        filters: Query filters:
            - project_types: Include repositories with specific project types
            - team: Filter by team name
            - maintenance_status: Filter by maintenance status
            - has_tools: Require specific standard tools
            - min_infrastructure_score: Minimum infrastructure score
            - workspace_only: Only include workspace repositories
            
    Returns:
        Filtered list of repository records
    """
    index = load_repository_index()
    if not index:
        return []
    
    if not filters:
        return index
    
    filtered_repos = []
    
    for repo in index:
        if _matches_filters(repo, filters):
            filtered_repos.append(repo)
    
    return filtered_repos


def _matches_filters(repo: Dict[str, str], filters: Dict) -> bool:
    """Check if repository record matches query filters."""
    # Filter by project types
    if 'project_types' in filters:
        required_types = filters['project_types']
        if isinstance(required_types, str):
            required_types = [required_types]
        
        repo_types = repo['project_types'].split(',')
        if not any(rtype in repo_types for rtype in required_types):
            return False
    
    # Filter by team
    if 'team' in filters:
        if repo['team'] != filters['team']:
            return False
    
    # Filter by maintenance status
    if 'maintenance_status' in filters:
        if repo['maintenance_status'] != filters['maintenance_status']:
            return False
    
    # Filter by required tools
    if 'has_tools' in filters:
        required_tools = filters['has_tools']
        if isinstance(required_tools, str):
            required_tools = [required_tools]
        
        for tool in required_tools:
            tool_field = f'has_{tool}'
            if tool_field in repo and repo[tool_field] != 'true':
                return False
    
    # Filter by infrastructure score
    if 'min_infrastructure_score' in filters:
        try:
            repo_score = float(repo['infrastructure_score'])
            if repo_score < filters['min_infrastructure_score']:
                return False
        except (ValueError, KeyError):
            return False
    
    # Filter workspace repositories only
    if filters.get('workspace_only', False):
        if repo['workspace_type'] == 'none':
            return False
    
    return True


def generate_analysis_report(detection_results: Dict[str, Dict]) -> Dict[str, Union[int, float, List, Dict]]:
    """
    Generate analysis report from batch detection results.
    
    Args:
        detection_results: Results from batch_detect_repositories()
        
    Returns:
        Comprehensive analysis report
    """
    total_repos = len(detection_results)
    if total_repos == 0:
        return {"total_repositories": 0, "analysis": "No repositories found"}
    
    # Aggregate statistics
    project_type_counts = {}
    workspace_type_counts = {}
    team_counts = {}
    language_counts = {}
    maintenance_status_counts = {}
    tool_coverage = {'build': 0, 'deploy': 0, 'test': 0, 'snap': 0}
    infrastructure_scores = []
    
    successful_detections = 0
    
    for result in detection_results.values():
        meta = result.get('meta', {})
        if meta.get('detection_success', True):
            successful_detections += 1
        
        # Count project types
        projects = result.get('projects', [])
        for project in projects:
            ptype = project.get('type', 'unknown')
            project_type_counts[ptype] = project_type_counts.get(ptype, 0) + 1
        
        # Count workspace types
        workspace = result.get('workspace', {})
        if workspace.get('is_workspace'):
            wtype = workspace.get('type', 'unknown')
            workspace_type_counts[wtype] = workspace_type_counts.get(wtype, 0) + 1
        
        # Count teams and languages from config
        config = result.get('configuration', {}).get('config', {})
        if config:
            metadata = config.get('metadata', {})
            team = metadata.get('team')
            if team:
                team_counts[team] = team_counts.get(team, 0) + 1
            
            language = metadata.get('primary_language')
            if language:
                language_counts[language] = language_counts.get(language, 0) + 1
            
            status = metadata.get('maintenance_status', 'unknown')
            maintenance_status_counts[status] = maintenance_status_counts.get(status, 0) + 1
        
        # Count tool coverage
        tooling = result.get('tooling_analysis', {})
        standard_tools = tooling.get('standard_bin_tools', {})
        for tool_name in ['build', 'deploy', 'test', 'snap']:
            tool_key = f'{tool_name}.sh'
            if standard_tools.get(tool_key, {}).get('exists', False):
                tool_coverage[tool_name] += 1
        
        # Collect infrastructure scores
        infra_analysis = tooling.get('infrastructure_analysis', {})
        score = infra_analysis.get('infrastructure_score', 0)
        if score > 0:
            infrastructure_scores.append(score)
    
    # Calculate averages and percentages
    success_rate = (successful_detections / total_repos) * 100
    
    tool_coverage_percentages = {
        tool: (count / total_repos) * 100 
        for tool, count in tool_coverage.items()
    }
    
    avg_infrastructure_score = (
        sum(infrastructure_scores) / len(infrastructure_scores) 
        if infrastructure_scores else 0
    )
    
    return {
        "summary": {
            "total_repositories": total_repos,
            "successful_detections": successful_detections,
            "success_rate_percent": round(success_rate, 1),
            "average_infrastructure_score": round(avg_infrastructure_score, 1)
        },
        "project_types": dict(sorted(project_type_counts.items(), key=lambda x: x[1], reverse=True)),
        "workspace_types": dict(sorted(workspace_type_counts.items(), key=lambda x: x[1], reverse=True)),
        "teams": dict(sorted(team_counts.items(), key=lambda x: x[1], reverse=True)),
        "primary_languages": dict(sorted(language_counts.items(), key=lambda x: x[1], reverse=True)),
        "maintenance_status": dict(sorted(maintenance_status_counts.items(), key=lambda x: x[1], reverse=True)),
        "tool_coverage": {
            "counts": tool_coverage,
            "percentages": {k: round(v, 1) for k, v in tool_coverage_percentages.items()}
        },
        "infrastructure": {
            "average_score": round(avg_infrastructure_score, 1),
            "score_distribution": _calculate_score_distribution(infrastructure_scores)
        }
    }


def _calculate_score_distribution(scores: List[float]) -> Dict[str, int]:
    """Calculate infrastructure score distribution."""
    if not scores:
        return {}
    
    distribution = {
        "excellent (90-100)": 0,
        "good (70-89)": 0,
        "fair (50-69)": 0,
        "poor (0-49)": 0
    }
    
    for score in scores:
        if score >= 90:
            distribution["excellent (90-100)"] += 1
        elif score >= 70:
            distribution["good (70-89)"] += 1
        elif score >= 50:
            distribution["fair (50-69)"] += 1
        else:
            distribution["poor (0-49)"] += 1
    
    return distribution


# ============================================================================
# Main Batch Processing Functions
# ============================================================================

def process_directory_tree(root_path: Path,
                          output_dir: Optional[Path] = None,
                          filters: Optional[Dict] = None,
                          max_workers: int = 4,
                          use_cache: bool = True) -> Dict[str, Union[Path, Dict, int]]:
    """
    Complete directory tree processing with discovery, detection, and export.
    
    Main entry point for batch processing operations.
    
    Args:
        root_path: Root directory to search for repositories
        output_dir: Output directory for results (default: cache directory)
        filters: Repository discovery and processing filters
        max_workers: Maximum concurrent workers for detection
        use_cache: Whether to use cached detection results
        
    Returns:
        Processing results summary:
        {
            "repositories_found": 42,
            "repositories_processed": 40,
            "processing_time_seconds": 125.3,
            "tsv_file": Path("/path/to/index.tsv"),
            "cache_directory": Path("/path/to/cache"),
            "analysis_report": {...}
        }
    """
    start_time = time.time()
    
    if output_dir is None:
        output_dir = get_cache_directory()
    
    # Step 1: Discover repositories
    print(f"Discovering repositories in {root_path}...")
    repositories = crawl_repositories(root_path, filters)
    print(f"Found {len(repositories)} repositories")
    
    if not repositories:
        return {
            "repositories_found": 0,
            "repositories_processed": 0,
            "processing_time_seconds": 0,
            "tsv_file": None,
            "cache_directory": output_dir,
            "analysis_report": {}
        }
    
    # Step 2: Batch detect repositories
    print(f"Processing {len(repositories)} repositories with {max_workers} workers...")
    detection_results = batch_detect_repositories(
        repositories, 
        max_workers=max_workers,
        use_cache=use_cache
    )
    
    # Step 3: Export to TSV
    tsv_file = output_dir / "repository_index.tsv"
    print(f"Exporting results to {tsv_file}...")
    export_repository_index(detection_results, tsv_file)
    
    # Step 4: Generate analysis report
    analysis_report = generate_analysis_report(detection_results)
    
    # Save analysis report as JSON
    report_file = output_dir / "analysis_report.json"
    try:
        with report_file.open('w', encoding='utf-8') as f:
            json.dump(analysis_report, f, indent=2, default=str)
    except OSError:
        pass
    
    processing_time = time.time() - start_time
    
    print(f"Processing complete in {processing_time:.1f} seconds")
    print(f"Results: {tsv_file}")
    print(f"Cache: {get_cache_directory()}")
    
    return {
        "repositories_found": len(repositories),
        "repositories_processed": len(detection_results),
        "processing_time_seconds": round(processing_time, 2),
        "tsv_file": tsv_file,
        "cache_directory": get_cache_directory(),
        "analysis_report": analysis_report
    }


# ============================================================================
# Utility Functions
# ============================================================================

def cleanup_old_cache(max_age_days: int = 30) -> int:
    """
    Clean up cache files older than specified age.
    
    Args:
        max_age_days: Maximum age in days before removal
        
    Returns:
        Number of files removed
    """
    cache_dir = get_cache_directory()
    cutoff_time = time.time() - (max_age_days * 24 * 3600)
    removed_count = 0
    
    try:
        for cache_file in cache_dir.glob("*.json"):
            try:
                if cache_file.stat().st_mtime < cutoff_time:
                    cache_file.unlink()
                    removed_count += 1
            except OSError:
                pass
    except OSError:
        pass
    
    return removed_count


def get_detection_registry() -> Dict[str, callable]:
    """
    Get registry of available detection functions for extensibility.
    
    Returns:
        Dictionary mapping detection names to functions
    """
    registry = {}
    
    try:
        from detection_core import get_repository_context
        registry["core_detection"] = get_repository_context
    except ImportError:
        pass
    
    try:
        from tooling_detection import get_complete_tooling_analysis
        registry["tooling_analysis"] = get_complete_tooling_analysis
    except ImportError:
        pass
    
    try:
        from workspace_detection import analyze_workspace_structure
        registry["workspace_analysis"] = analyze_workspace_structure
    except ImportError:
        pass
    
    try:
        from projectrc_config import get_enhanced_detection_with_config
        registry["enhanced_detection"] = get_enhanced_detection_with_config
    except ImportError:
        pass
    
    return registry


def register_custom_detection(name: str, detection_func: callable) -> None:
    """
    Register custom detection function for batch processing.
    
    Args:
        name: Name for the detection function
        detection_func: Function that takes repo_path and returns detection data
    """
    # This would be implemented with a global registry in a real system
    # For now, it's a placeholder for the extensibility pattern
    pass
