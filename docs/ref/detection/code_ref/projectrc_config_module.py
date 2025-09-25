"""
ProjectRC Configuration Module - Configuration-Driven Detection and Verification
Version: 1.0.0
Last Updated: 2025-09-23
Compatible: SEMV v3.0+, Blade Next v1.0+
Dependencies: detection_core.py

Manages .projectrc configuration files for repository-specific detection hints and overrides.
"""

from pathlib import Path
from typing import List, Dict, Optional, Union, Any, Set
import json
import re
import os
from datetime import datetime


# ============================================================================
# Configuration Schema and Validation
# ============================================================================

# Default .projectrc schema structure
DEFAULT_PROJECTRC_SCHEMA = {
    "hints": {
        "submodules": [],
        "custom_scripts": [],
        "workspace_members": [],
        "ignore_directories": [],
        "additional_version_files": []
    },
    "overrides": {
        "project_types": [],
        "version_authority": None,
        "disable_detection": [],
        "force_workspace_type": None
    },
    "metadata": {
        "team": None,
        "primary_language": None,
        "deployment_target": None,
        "maintenance_status": "active"
    },
    "detection_config": {
        "skip_generated_files": True,
        "enable_deep_search": False,
        "workspace_detection_enabled": True,
        "cache_results": False
    }
}


def load_projectrc(repo_path: Path) -> Optional[Dict[str, Any]]:
    """
    Load and parse .projectrc configuration file.
    
    Supports both JSON and simplified key=value formats.
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        Parsed configuration dictionary, or None if file doesn't exist
        
    Example .projectrc (JSON format):
        {
            "hints": {
                "workspace_members": ["./api", "./cli", "./web"],
                "custom_scripts": ["./scripts/migrate.sh"]
            },
            "overrides": {
                "version_authority": "rust"
            },
            "metadata": {
                "team": "platform",
                "primary_language": "rust"
            }
        }
    """
    repo_path = Path(repo_path).resolve()
    projectrc_path = repo_path / ".projectrc"
    
    if not projectrc_path.exists():
        return None
    
    try:
        content = projectrc_path.read_text(encoding='utf-8').strip()
        
        # Try JSON format first
        if content.startswith('{'):
            try:
                config = json.loads(content)
                return _merge_with_defaults(config)
            except json.JSONDecodeError:
                pass
        
        # Try simplified key=value format
        config = _parse_simple_format(content)
        return _merge_with_defaults(config) if config else None
        
    except (OSError, UnicodeDecodeError) as e:
        return None


def _parse_simple_format(content: str) -> Optional[Dict]:
    """Parse simplified .projectrc format (key=value pairs)."""
    config = {"hints": {}, "overrides": {}, "metadata": {}, "detection_config": {}}
    
    for line in content.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        if '=' not in line:
            continue
        
        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip().strip('"\'')
        
        # Parse different configuration sections
        if key.startswith('hint.'):
            section_key = key[5:]  # Remove 'hint.' prefix
            config["hints"][section_key] = _parse_value(value)
        elif key.startswith('override.'):
            section_key = key[9:]  # Remove 'override.' prefix
            config["overrides"][section_key] = _parse_value(value)
        elif key.startswith('meta.'):
            section_key = key[5:]  # Remove 'meta.' prefix
            config["metadata"][section_key] = _parse_value(value)
        elif key.startswith('config.'):
            section_key = key[7:]  # Remove 'config.' prefix
            config["detection_config"][section_key] = _parse_value(value)
    
    return config if any(config.values()) else None


def _parse_value(value: str) -> Union[str, List[str], bool, None]:
    """Parse configuration value with type inference."""
    # Boolean values
    if value.lower() in ('true', 'yes', '1'):
        return True
    elif value.lower() in ('false', 'no', '0'):
        return False
    elif value.lower() in ('null', 'none', ''):
        return None
    
    # List values (comma-separated)
    if ',' in value:
        return [item.strip() for item in value.split(',') if item.strip()]
    
    # String value
    return value


def _merge_with_defaults(config: Dict) -> Dict:
    """Merge user configuration with default schema."""
    result = {}
    
    for section, defaults in DEFAULT_PROJECTRC_SCHEMA.items():
        if section in config:
            if isinstance(defaults, dict):
                # Merge dictionary sections
                result[section] = {**defaults, **config[section]}
            else:
                # Override non-dictionary values
                result[section] = config[section]
        else:
            result[section] = defaults.copy() if isinstance(defaults, dict) else defaults
    
    return result


def validate_projectrc_schema(config: Dict) -> List[str]:
    """
    Validate .projectrc configuration against expected schema.
    
    Args:
        config: Parsed configuration dictionary
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    # Validate top-level sections
    required_sections = ["hints", "overrides", "metadata", "detection_config"]
    for section in required_sections:
        if section not in config:
            errors.append(f"Missing required section: {section}")
    
    # Validate hints section
    if "hints" in config:
        hints = config["hints"]
        for key, value in hints.items():
            if key in ["submodules", "custom_scripts", "workspace_members", "ignore_directories", "additional_version_files"]:
                if not isinstance(value, list):
                    errors.append(f"hints.{key} must be a list")
    
    # Validate overrides section
    if "overrides" in config:
        overrides = config["overrides"]
        
        if "project_types" in overrides and not isinstance(overrides["project_types"], list):
            errors.append("overrides.project_types must be a list")
        
        valid_project_types = {"rust", "javascript", "python", "bash", "unknown"}
        if "project_types" in overrides:
            for ptype in overrides["project_types"]:
                if ptype not in valid_project_types:
                    errors.append(f"Invalid project type in overrides: {ptype}")
        
        if "version_authority" in overrides:
            authority = overrides["version_authority"]
            if authority and authority not in valid_project_types:
                errors.append(f"Invalid version authority: {authority}")
    
    # Validate metadata section
    if "metadata" in config:
        metadata = config["metadata"]
        valid_statuses = {"active", "maintenance", "deprecated", "archived"}
        
        if "maintenance_status" in metadata:
            status = metadata["maintenance_status"]
            if status and status not in valid_statuses:
                errors.append(f"Invalid maintenance status: {status}")
    
    return errors


# ============================================================================
# Hint Verification and Validation
# ============================================================================

def verify_hints(repo_path: Path, hints: Dict[str, Any]) -> Dict[str, Dict[str, Union[bool, str, List]]]:
    """
    Verify configuration hints against repository reality.
    
    Checks if hinted paths, files, and configurations actually exist and are valid.
    
    Args:
        repo_path: Path to repository directory
        hints: Hints section from .projectrc configuration
        
    Returns:
        Verification results per hint type:
        {
            "submodules": {"verified": True, "missing": [], "extra": []},
            "custom_scripts": {"verified": False, "missing": ["./missing.sh"]},
            "workspace_members": {"verified": True, "missing": [], "extra": []}
        }
    """
    repo_path = Path(repo_path).resolve()
    verification = {}
    
    # Verify submodules
    if "submodules" in hints:
        verification["submodules"] = _verify_submodules(repo_path, hints["submodules"])
    
    # Verify custom scripts
    if "custom_scripts" in hints:
        verification["custom_scripts"] = _verify_custom_scripts(repo_path, hints["custom_scripts"])
    
    # Verify workspace members
    if "workspace_members" in hints:
        verification["workspace_members"] = _verify_workspace_members(repo_path, hints["workspace_members"])
    
    # Verify ignore directories
    if "ignore_directories" in hints:
        verification["ignore_directories"] = _verify_ignore_directories(repo_path, hints["ignore_directories"])
    
    # Verify additional version files
    if "additional_version_files" in hints:
        verification["additional_version_files"] = _verify_version_files(repo_path, hints["additional_version_files"])
    
    return verification


def _verify_submodules(repo_path: Path, hinted_submodules: List[str]) -> Dict:
    """Verify hinted submodules against actual .gitmodules."""
    # Get actual submodules
    actual_submodules = []
    gitmodules_path = repo_path / ".gitmodules"
    
    if gitmodules_path.exists():
        try:
            content = gitmodules_path.read_text(encoding='utf-8')
            path_matches = re.findall(r'path\s*=\s*([^\n]+)', content)
            actual_submodules = [path.strip() for path in path_matches]
        except (OSError, UnicodeDecodeError):
            pass
    
    # Normalize paths for comparison
    hinted_normalized = [path.lstrip('./') for path in hinted_submodules]
    actual_normalized = [path.lstrip('./') for path in actual_submodules]
    
    missing = [path for path in hinted_normalized if path not in actual_normalized]
    extra = [path for path in actual_normalized if path not in hinted_normalized]
    
    return {
        "verified": len(missing) == 0,
        "missing": missing,
        "extra": extra,
        "hinted": hinted_normalized,
        "actual": actual_normalized
    }


def _verify_custom_scripts(repo_path: Path, hinted_scripts: List[str]) -> Dict:
    """Verify hinted custom scripts exist and are executable."""
    missing = []
    non_executable = []
    verified_scripts = []
    
    for script_path in hinted_scripts:
        full_path = repo_path / script_path.lstrip('./')
        
        if not full_path.exists():
            missing.append(script_path)
        elif not full_path.is_file():
            missing.append(f"{script_path} (not a file)")
        else:
            verified_scripts.append(script_path)
            if not os.access(full_path, os.X_OK):
                non_executable.append(script_path)
    
    return {
        "verified": len(missing) == 0,
        "missing": missing,
        "non_executable": non_executable,
        "verified_scripts": verified_scripts
    }


def _verify_workspace_members(repo_path: Path, hinted_members: List[str]) -> Dict:
    """Verify hinted workspace members exist and have project files."""
    missing = []
    invalid = []
    verified_members = []
    
    for member_path in hinted_members:
        full_path = repo_path / member_path.lstrip('./')
        
        if not full_path.exists():
            missing.append(member_path)
        elif not full_path.is_dir():
            invalid.append(f"{member_path} (not a directory)")
        else:
            # Check if directory has project files
            has_project_files = any([
                (full_path / "Cargo.toml").exists(),
                (full_path / "package.json").exists(),
                (full_path / "pyproject.toml").exists(),
                (full_path / "setup.py").exists()
            ])
            
            if has_project_files:
                verified_members.append(member_path)
            else:
                invalid.append(f"{member_path} (no project files)")
    
    return {
        "verified": len(missing) == 0 and len(invalid) == 0,
        "missing": missing,
        "invalid": invalid,
        "verified_members": verified_members
    }


def _verify_ignore_directories(repo_path: Path, hinted_ignores: List[str]) -> Dict:
    """Verify hinted ignore directories exist."""
    missing = []
    verified_dirs = []
    
    for ignore_path in hinted_ignores:
        full_path = repo_path / ignore_path.lstrip('./')
        
        if not full_path.exists():
            missing.append(ignore_path)
        elif full_path.is_dir():
            verified_dirs.append(ignore_path)
        else:
            missing.append(f"{ignore_path} (not a directory)")
    
    return {
        "verified": len(missing) == 0,
        "missing": missing,
        "verified_directories": verified_dirs
    }


def _verify_version_files(repo_path: Path, hinted_files: List[str]) -> Dict:
    """Verify hinted additional version files exist and contain versions."""
    missing = []
    invalid = []
    verified_files = []
    
    for file_path in hinted_files:
        full_path = repo_path / file_path.lstrip('./')
        
        if not full_path.exists():
            missing.append(file_path)
        elif not full_path.is_file():
            invalid.append(f"{file_path} (not a file)")
        else:
            # Try to extract version from file
            version = _extract_version_from_file(full_path)
            if version:
                verified_files.append({"path": file_path, "version": version})
            else:
                invalid.append(f"{file_path} (no version found)")
    
    return {
        "verified": len(missing) == 0 and len(invalid) == 0,
        "missing": missing,
        "invalid": invalid,
        "verified_files": verified_files
    }


def _extract_version_from_file(file_path: Path) -> Optional[str]:
    """Try to extract version from any file type."""
    try:
        # Try different extraction methods based on file extension
        if file_path.suffix == ".toml":
            from detection_core import extract_rust_version
            return extract_rust_version(file_path)
        elif file_path.suffix == ".json":
            from detection_core import extract_javascript_version
            return extract_javascript_version(file_path)
        elif file_path.suffix == ".py":
            from detection_core import extract_python_version
            return extract_python_version(file_path)
        elif file_path.suffix == ".sh":
            from detection_core import extract_bash_version
            return extract_bash_version(file_path)
        else:
            # Generic version extraction for unknown file types
            content = file_path.read_text(encoding='utf-8')
            version_patterns = [
                r'version["\']?\s*[:=]\s*["\']?([0-9]+\.[0-9]+\.[0-9]+[^"\'>\s]*)',
                r'VERSION\s*=\s*["\']([^"\']+)["\']',
                r'__version__\s*=\s*["\']([^"\']+)["\']'
            ]
            
            for pattern in version_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    return match.group(1)
            
            return None
    
    except (OSError, UnicodeDecodeError, ImportError):
        return None


# ============================================================================
# Override Application
# ============================================================================

def apply_overrides(detection_result: Dict, overrides: Dict[str, Any]) -> Dict:
    """
    Apply configuration overrides to detection results.
    
    Modifies detection results based on user-specified overrides in .projectrc.
    
    Args:
        detection_result: Original detection result from get_repository_context()
        overrides: Overrides section from .projectrc configuration
        
    Returns:
        Modified detection result with overrides applied
    """
    result = detection_result.copy()
    
    # Apply project type overrides
    if "project_types" in overrides and overrides["project_types"]:
        result["projects"] = _apply_project_type_override(
            result.get("projects", []), 
            overrides["project_types"]
        )
    
    # Apply version authority override
    if "version_authority" in overrides and overrides["version_authority"]:
        result = _apply_version_authority_override(result, overrides["version_authority"])
    
    # Apply detection disabling
    if "disable_detection" in overrides and overrides["disable_detection"]:
        result["projects"] = _apply_disable_detection(
            result.get("projects", []), 
            overrides["disable_detection"]
        )
    
    # Apply workspace type override
    if "force_workspace_type" in overrides and overrides["force_workspace_type"]:
        if "workspace" in result:
            result["workspace"]["type"] = overrides["force_workspace_type"]
            result["workspace"]["is_workspace"] = True
    
    return result


def _apply_project_type_override(projects: List[Dict], override_types: List[str]) -> List[Dict]:
    """Override detected project types with specified types."""
    if not override_types:
        return projects
    
    # Replace all detected projects with override types
    overridden_projects = []
    for project_type in override_types:
        overridden_projects.append({
            "type": project_type,
            "root": "./",
            "version_file": None,  # Will be determined by detection
            "version": None,
            "override_applied": True
        })
    
    return overridden_projects


def _apply_version_authority_override(detection_result: Dict, authority_type: str) -> Dict:
    """Set version authority to specified project type."""
    projects = detection_result.get("projects", [])
    
    # Find the authoritative project
    authority_project = None
    for project in projects:
        if project["type"] == authority_type:
            authority_project = project
            break
    
    if authority_project and authority_project.get("version"):
        # Mark this project as the version authority
        authority_project["version_authority"] = True
        
        # Update any version synchronization logic here if needed
        detection_result["version_authority"] = {
            "type": authority_type,
            "version": authority_project["version"],
            "source": "override"
        }
    
    return detection_result


def _apply_disable_detection(projects: List[Dict], disabled_types: List[str]) -> List[Dict]:
    """Remove specified project types from detection results."""
    return [project for project in projects if project["type"] not in disabled_types]


# ============================================================================
# Configuration File Generation
# ============================================================================

def generate_projectrc_template(repo_path: Path, detection_result: Dict) -> str:
    """
    Generate a .projectrc template based on current detection results.
    
    Creates a template configuration file that users can customize.
    
    Args:
        repo_path: Path to repository directory
        detection_result: Current detection results
        
    Returns:
        Template .projectrc content as string
    """
    projects = detection_result.get("projects", [])
    workspace = detection_result.get("workspace", {})
    tools = detection_result.get("tools", {})
    scripts = detection_result.get("scripts", {})
    
    template = {
        "hints": {},
        "overrides": {},
        "metadata": {
            "team": "TEAM_NAME",
            "primary_language": _guess_primary_language(projects),
            "deployment_target": "DEPLOYMENT_TARGET",
            "maintenance_status": "active"
        },
        "detection_config": {
            "skip_generated_files": True,
            "enable_deep_search": False,
            "workspace_detection_enabled": True,
            "cache_results": False
        }
    }
    
    # Add hints based on current detection
    if workspace.get("is_workspace"):
        workspace_members = workspace.get("members", [])
        if workspace_members:
            template["hints"]["workspace_members"] = [
                member.get("path", "") for member in workspace_members
            ]
    
    # Add custom scripts hint
    custom_scripts = scripts.get("root_scripts", [])
    if custom_scripts:
        template["hints"]["custom_scripts"] = custom_scripts
    
    # Add potential overrides as comments
    project_types = [project["type"] for project in projects]
    if project_types:
        template["overrides"]["project_types"] = project_types
        # template["overrides"]["version_authority"] = project_types[0]
    
    # Format as JSON with comments
    json_content = json.dumps(template, indent=2)
    
    # Add header comment
    header = f"""# .projectrc - Repository Configuration
# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
#
# This file allows you to override project detection and provide hints
# for complex repository structures. Uncomment and modify as needed.
#
# Documentation: https://docs.semv.dev/projectrc
#

"""
    
    return header + json_content


def _guess_primary_language(projects: List[Dict]) -> Optional[str]:
    """Guess primary language based on detected projects."""
    if not projects:
        return None
    
    # Count project types
    type_counts = {}
    for project in projects:
        project_type = project["type"]
        type_counts[project_type] = type_counts.get(project_type, 0) + 1
    
    # Return most common type (excluding unknown)
    valid_types = {k: v for k, v in type_counts.items() if k != "unknown"}
    if valid_types:
        return max(valid_types, key=valid_types.get)
    
    return None


def save_projectrc_template(repo_path: Path, detection_result: Dict, force: bool = False) -> bool:
    """
    Save generated .projectrc template to repository.
    
    Args:
        repo_path: Path to repository directory
        detection_result: Current detection results
        force: Whether to overwrite existing .projectrc file
        
    Returns:
        True if template was saved, False if file already exists and force=False
    """
    repo_path = Path(repo_path).resolve()
    projectrc_path = repo_path / ".projectrc"
    
    if projectrc_path.exists() and not force:
        return False
    
    template_content = generate_projectrc_template(repo_path, detection_result)
    
    try:
        projectrc_path.write_text(template_content, encoding='utf-8')
        return True
    except OSError:
        return False


# ============================================================================
# Integration Functions
# ============================================================================

def get_enhanced_detection_with_config(repo_path: Path) -> Dict:
    """
    Get enhanced detection results with .projectrc configuration applied.
    
    This is the main integration function that combines core detection
    with configuration overrides and verification.
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        Enhanced detection results with configuration applied
    """
    repo_path = Path(repo_path).resolve()
    
    # Load configuration
    config = load_projectrc(repo_path)
    
    # Get base detection results
    try:
        from detection_core import get_repository_context
        detection_result = get_repository_context(repo_path)
    except ImportError:
        detection_result = {"projects": [], "workspace": {}, "validation": {}}
    
    # Apply configuration if present
    if config:
        # Verify hints
        hints_verification = {}
        if config.get("hints"):
            hints_verification = verify_hints(repo_path, config["hints"])
        
        # Apply overrides
        if config.get("overrides"):
            detection_result = apply_overrides(detection_result, config["overrides"])
        
        # Add configuration information to result
        detection_result["configuration"] = {
            "has_projectrc": True,
            "config": config,
            "hints_verification": hints_verification,
            "schema_errors": validate_projectrc_schema(config)
        }
    else:
        detection_result["configuration"] = {
            "has_projectrc": False,
            "config": None,
            "hints_verification": {},
            "schema_errors": []
        }
    
    return detection_result


def validate_repository_configuration(repo_path: Path) -> Dict[str, Union[bool, List[str], Dict]]:
    """
    Comprehensive validation of repository configuration.
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        Validation report with issues and recommendations
    """
    repo_path = Path(repo_path).resolve()
    
    config = load_projectrc(repo_path)
    issues = []
    recommendations = []
    
    if not config:
        recommendations.append("Consider adding .projectrc for repository-specific configuration")
        return {
            "has_config": False,
            "is_valid": True,
            "issues": issues,
            "recommendations": recommendations
        }
    
    # Validate schema
    schema_errors = validate_projectrc_schema(config)
    issues.extend(schema_errors)
    
    # Verify hints
    if config.get("hints"):
        hints_verification = verify_hints(repo_path, config["hints"])
        
        for hint_type, verification in hints_verification.items():
            if not verification.get("verified", True):
                missing = verification.get("missing", [])
                invalid = verification.get("invalid", [])
                
                if missing:
                    issues.append(f"Missing {hint_type}: {missing}")
                if invalid:
                    issues.append(f"Invalid {hint_type}: {invalid}")
    
    # Generate recommendations
    if not config.get("metadata", {}).get("team"):
        recommendations.append("Add team metadata for better project organization")
    
    if not config.get("metadata", {}).get("primary_language"):
        recommendations.append("Specify primary language in metadata")
    
    return {
        "has_config": True,
        "is_valid": len(issues) == 0,
        "issues": issues,
        "recommendations": recommendations,
        "config_summary": _generate_config_summary(config)
    }


def _generate_config_summary(config: Dict) -> Dict[str, Any]:
    """Generate a summary of configuration contents."""
    summary = {
        "hints_count": 0,
        "overrides_count": 0,
        "has_metadata": False,
        "sections": []
    }
    
    if config.get("hints"):
        hints = config["hints"]
        summary["hints_count"] = sum(
            len(v) if isinstance(v, list) else (1 if v else 0)
            for v in hints.values()
        )
        if summary["hints_count"] > 0:
            summary["sections"].append("hints")
    
    if config.get("overrides"):
        overrides = config["overrides"]
        summary["overrides_count"] = sum(
            1 for v in overrides.values() if v is not None
        )
        if summary["overrides_count"] > 0:
            summary["sections"].append("overrides")
    
    if config.get("metadata"):
        metadata = config["metadata"]
        summary["has_metadata"] = any(
            v is not None for v in metadata.values()
        )
        if summary["has_metadata"]:
            summary["sections"].append("metadata")
    
    return summary


# ============================================================================
# Utility Functions
# ============================================================================

def create_projectrc_from_template(repo_path: Path, template_data: Dict) -> bool:
    """
    Create .projectrc file from template data.
    
    Args:
        repo_path: Path to repository directory
        template_data: Template configuration data
        
    Returns:
        True if file was created successfully, False otherwise
    """
    repo_path = Path(repo_path).resolve()
    projectrc_path = repo_path / ".projectrc"
    
    # Merge with defaults and validate
    config = _merge_with_defaults(template_data)
    errors = validate_projectrc_schema(config)
    
    if errors:
        return False
    
    try:
        json_content = json.dumps(config, indent=2)
        projectrc_path.write_text(json_content, encoding='utf-8')
        return True
    except OSError:
        return False


def list_example_configurations() -> Dict[str, Dict]:
    """
    Get example .projectrc configurations for different repository types.
    
    Returns:
        Dictionary of example configurations by repository type
    """
    examples = {
        "rust_workspace": {
            "hints": {
                "workspace_members": ["./cli", "./server", "./common"]
            },
            "overrides": {
                "version_authority": "rust"
            },
            "metadata": {
                "team": "backend",
                "primary_language": "rust",
                "deployment_target": "production"
            }
        },
        
        "npm_monorepo": {
            "hints": {
                "workspace_members": ["./packages/*", "./apps/*"]
            },
            "overrides": {
                "version_authority": "javascript"
            },
            "metadata": {
                "team": "frontend",
                "primary_language": "javascript",
                "deployment_target": "web"
            }
        },
        
        "mixed_project": {
            "hints": {
                "custom_scripts": ["./scripts/deploy.sh", "./scripts/test.py"]
            },
            "overrides": {
                "project_types": ["rust", "python"],
                "version_authority": "rust"
            },
            "metadata": {
                "team": "platform",
                "primary_language": "rust",
                "deployment_target": "kubernetes"
            }
        },
        
        "legacy_bash": {
            "hints": {
                "additional_version_files": ["./version.txt", "./VERSION"]
            },
            "overrides": {
                "project_types": ["bash"],
                "disable_detection": ["unknown"]
            },
            "metadata": {
                "team": "ops",
                "primary_language": "bash",
                "maintenance_status": "maintenance"
            }
        }
    }
    
    return examples
