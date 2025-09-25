
################################################################################
# Part 01: part_01_header.sh
################################################################################

#!/usr/bin/env bash
#
# ┌─┐┬┌┬┐┌─┐┬┌┬┐
# │ ┬│ │ └─┐││││
# └─┘┴ ┴ └─┘┴┴ ┴
#
# name: gitsim
# semv-version: 2.1.3
# desc: Git & Home Environment Simulator for Testing
#
# portable: find, mkdir, sed, awk, grep, shasum, wc, sort, tac, dirname, basename, mktemp
# builtins: printf, read, local, declare, case, if, for, while, shift, return



################################################################################
# Part 02: part_02_config.sh
################################################################################

################################################################################
# Configuration & XDG+ Compliance
################################################################################

GITSIM_NAME="gitsim"

# XDG+ Base Configuration
: ${XDG_HOME:="$HOME/.local"}
: ${XDG_LIB_HOME:="$XDG_HOME/lib"}
: ${XDG_BIN_HOME:="$XDG_HOME/bin"}
: ${XDG_ETC_HOME:="$XDG_HOME/etc"}
: ${XDG_DATA_HOME:="$XDG_HOME/data"}
: ${XDG_CACHE_HOME:="$HOME/.cache"}

# Temp directory preference (respects user's cache preference)
: ${TMPDIR:="$XDG_CACHE_HOME/tmp"}

# BashFX FX-specific paths
GITSIM_LIB_DIR="$XDG_LIB_HOME/fx/$GITSIM_NAME"
GITSIM_BIN_LINK="$XDG_BIN_HOME/fx/$GITSIM_NAME"
GITSIM_ETC_DIR="$XDG_ETC_HOME/$GITSIM_NAME"

# SIM_ variables that can inherit from live shell or be overridden
: ${SIM_HOME:=${XDG_HOME:-$HOME}}
: ${SIM_USER:=${USER:-testuser}}
: ${SIM_SHELL:=${SHELL:-/bin/bash}}
: ${SIM_EDITOR:=${EDITOR:-nano}}
: ${SIM_LANG:=${LANG:-en_US.UTF-8}}

# Standard option flags
opt_debug=false
opt_trace=false
opt_quiet=false
opt_force=false
opt_yes=false
opt_dev=false


################################################################################
# Part 03: part_03_stderr.sh
################################################################################

################################################################################
# Simple stderr functions
################################################################################

stderr() { printf "%s\n" "$*" >&2; }
info() { [[ "$opt_quiet" == true ]] && return; stderr "[INFO] $*"; }
warn() { [[ "$opt_quiet" == true ]] && return; stderr "[WARN] $*"; }
error() { stderr "[ERROR] $*"; }
fatal() { stderr "[FATAL] $*"; exit 1; }
okay() { [[ "$opt_quiet" == true ]] && return; stderr "[OK] $*"; }
trace() { [[ "$opt_trace" == true ]] && stderr "[TRACE] $*"; }

################################################################################
# Part 04: part_04_helpers.sh
################################################################################

################################################################################
# Helper Functions
################################################################################

# Print logo from figlet block
_logo() {
    local show_logo="${1:-true}"
    
    if [[ "$show_logo" == "false" ]]; then
        return 0
    fi
    
    cat << 'EOF'
┌─┐┬┌┬┐┌─┐┬┌┬┐
│ ┬│ │ └─┐││││
└─┘┴ ┴ └─┘┴┴ ┴
EOF
}

# Create a temporary directory in user's cache instead of /tmp
_mktemp_dir() {
    local temp_base="${XDG_CACHE_HOME}/gitsim-tmp"
    mkdir -p "$temp_base"
    mktemp -d "$temp_base/XXXXXX"
}

# Find the root of the simulated repository by searching upwards for .gitsim
_find_sim_root() {
    local dir="$PWD"
    while [ "$dir" != "/" ]; do
        if [ -d "$dir/.gitsim" ]; then
            printf "%s" "$dir"
            return 0
        fi
        dir=$(dirname "$dir")
    done
    return 1
}

# Get the simulated home directory path
_get_sim_home() {
    local sim_root="$1"
    printf "%s" "$sim_root/.gitsim/.home"
}

# Get the simulated project directory
_get_sim_project_dir() {
    local home_dir="$1"
    local project_name="${2:-testproject}"
    printf "%s" "$home_dir/projects/$project_name"
}

# Safety check: ensure we're in a safe location for file generation
_is_safe_for_generation() {
    local current_dir="$PWD"
    
    # Safe if we're in a .gitsim directory structure
    if [[ "$current_dir" == *"/.gitsim/"* ]] || [[ "$current_dir" == *"/.gitsim" ]]; then
        return 0
    fi
    
    # Safe if we have a .gitsim directory (our simulation root)
    if [[ -d ".gitsim" ]]; then
        return 0
    fi
    
    # Unsafe if we're in a real git repo without .gitsim
    if [[ -d ".git" ]] && [[ ! -d ".gitsim" ]]; then
        return 1
    fi
    
    # Default to safe for other cases
    return 0
}

################################################################################
# Part 05: part_05_git_simulation.sh
################################################################################

################################################################################
# Git Simulation Functions
################################################################################

# Initialize git simulation structure
__create_git_structure() {
    local data_dir="$1"
    local ret=1
    
    if mkdir -p "$data_dir"; then
        touch "$data_dir"/{tags.txt,commits.txt,config,index,branches.txt,remotes.txt,HEAD}
        echo "main" > "$data_dir/branch.txt"
        echo "main" >> "$data_dir/branches.txt"
        ret=0
    fi
    
    return "$ret"
}

# Add .gitignore entry safely
__add_gitignore_entry() {
    local entry="$1"
    local gitignore_file=".gitignore"
    
    if ! grep -q "^${entry}$" "$gitignore_file" 2>/dev/null; then
        echo "$entry" >> "$gitignore_file"
    fi
    return 0
}

################################################################################
# Home Environment Setup - Proper Function Ordinality
################################################################################

# Mid-Ordinal: Home environment orchestrator (no literal operations)
_setup_home_env() {
    local home_dir="$1"
    
    # Orchestrate directory creation
    _create_home_directories "$home_dir" || return 1
    
    # Orchestrate dotfile generation
    _create_home_dotfiles "$home_dir" || return 1
    
    # Orchestrate sample file generation
    _create_sample_files "$home_dir" || return 1
    
    trace "Successfully set up home environment at $home_dir"
    return 0
}

# Mid-Ordinal: Directory structure creation
_create_home_directories() {
    local home_dir="$1"
    
    if mkdir -p "$home_dir"/{.config,.local/{bin,share,state},.cache,projects,Documents,Downloads}; then
        trace "Created home directory structure"
        return 0
    else
        error "Failed to create home directory structure"
        return 1
    fi
}

# Mid-Ordinal: Dotfiles generation orchestrator
_create_home_dotfiles() {
    local home_dir="$1"
    
    # Call low-ordinal print functions for each dotfile
    __print_bashrc "$home_dir/.bashrc" "$home_dir" || {
        error "Failed to create .bashrc"
        return 1
    }
    
    __print_profile "$home_dir/.profile" || {
        error "Failed to create .profile" 
        return 1
    }
    
    __print_gitconfig "$home_dir/.gitconfig" "$SIM_USER" "$SIM_EDITOR" || {
        error "Failed to create .gitconfig"
        return 1
    }
    
    trace "Created dotfiles in $home_dir"
    return 0
}

# Mid-Ordinal: Sample files creation orchestrator  
_create_sample_files() {
    local home_dir="$1"
    
    # Create configuration samples
    __print_sample_config "$home_dir/.config/testrc" || return 1
    __print_sample_data "$home_dir/.local/share/testdata" || return 1
    __print_sample_state "$home_dir/.local/state/teststate" || return 1
    __print_sample_cache "$home_dir/.cache/testcache" || return 1
    
    # Create document samples
    __print_sample_readme "$home_dir/Documents/README.md" || return 1
    __print_sample_download "$home_dir/Downloads/sample.txt" || return 1
    
    trace "Created sample files in $home_dir"
    return 0
}

################################################################################
# Low-Ordinal: Literal File Generation Functions
################################################################################

# Generate .bashrc content
__print_bashrc() {
    local file="$1"
    local home_path="$2"
    
    cat > "$file" << EOF
# Simulated .bashrc for testing
export USER="$SIM_USER"
export HOME="$home_path"
export SHELL="$SIM_SHELL"
export EDITOR="$SIM_EDITOR"
export LANG="$SIM_LANG"

export PATH="\$HOME/.local/bin:\$PATH"
export XDG_CONFIG_HOME="\$HOME/.config"
export XDG_DATA_HOME="\$HOME/.local/share"
export XDG_STATE_HOME="\$HOME/.local/state"
export XDG_CACHE_HOME="\$HOME/.cache"

# Common aliases for testing
alias ll='ls -la'
alias la='ls -A'
alias l='ls -CF'

# Simulate common shell functions
cd() { builtin cd "\$@" && pwd; }
EOF
    return $?
}

# Generate .profile content
__print_profile() {
    local file="$1"
    
    cat > "$file" << 'EOF'
# Simulated .profile for testing
if [ -d "$HOME/.local/bin" ] ; then
    PATH="$HOME/.local/bin:$PATH"
fi

# Source .bashrc if running bash
if [ -n "$BASH_VERSION" ]; then
    if [ -f "$HOME/.bashrc" ]; then
        . "$HOME/.bashrc"
    fi
fi
EOF
    return $?
}

# Generate .gitconfig content
__print_gitconfig() {
    local file="$1"
    local user="$2"
    local editor="$3"
    
    cat > "$file" << EOF
[user]
    name = $user
    email = ${user}@example.com
[init]
    defaultBranch = main
[core]
    editor = $editor
[alias]
    st = status
    co = checkout
    br = branch
    ci = commit
    unstage = reset HEAD --
    last = log -1 HEAD
    visual = !gitk
EOF
    return $?
}

# Generate sample configuration file
__print_sample_config() {
    local file="$1"
    
    printf "# Test configuration for %s\n" "$SIM_USER" > "$file"
    return $?
}

# Generate sample data file
__print_sample_data() {
    local file="$1"
    
    printf "Sample data file for testing\n" > "$file"
    return $?
}

# Generate sample state file
__print_sample_state() {
    local file="$1"
    
    printf "state=initialized\n" > "$file"
    return $?
}

# Generate sample cache file (empty)
__print_sample_cache() {
    local file="$1"
    
    touch "$file"
    return $?
}

# Generate sample README
__print_sample_readme() {
    local file="$1"
    
    printf "# Sample README\n" > "$file"
    return $?
}

# Generate sample download file
__print_sample_download() {
    local file="$1"
    
    printf "Sample download content\n" > "$file"
    return $?
}

################################################################################
# Part 06: part_06_rc_system.sh
################################################################################

################################################################################
# RC System & Configuration Management
################################################################################

# Source .simrc file if it exists
_source_simrc() {
    local simrc_file=".simrc"
    
    if [ -f "$simrc_file" ]; then
        trace "Sourcing $simrc_file"
        # shellcheck disable=SC1090
        source "$simrc_file"
        return 0
    fi
    
    return 1
}

# Check if we should offer to create .simrc
_check_simrc() {
    local simrc_file=".simrc"
    
    if [ ! -f "$simrc_file" ]; then
        warn "No .simrc file found in current directory"
        info "Run 'gitsim rcgen' to create a configuration file for SIM_ variables"
        return 1
    fi
    
    return 0
}

# Track generated files for cleanup
_track_generated_file() {
    local file="$1"
    local simrc_file=".simrc"
    
    # Ensure .simrc exists
    if [[ ! -f "$simrc_file" ]]; then
        warn "No .simrc file found to track generated files"
        return 1
    fi
    
    # Add to GENERATED_FILES array if not already present
    if ! grep -q "GENERATED_FILES.*$file" "$simrc_file"; then
        # Check if GENERATED_FILES array exists
        if grep -q "GENERATED_FILES=" "$simrc_file"; then
            # Array exists, append to it
            sed -i "s/GENERATED_FILES=(/GENERATED_FILES=(\"$file\" /" "$simrc_file"
        else
            # Array doesn't exist, create it
            echo "GENERATED_FILES=(\"$file\")" >> "$simrc_file"
        fi
    fi
}

# Generate .simrc content
__print_simrc() {
    local file="$1"
    
    cat > "$file" << EOF
#!/usr/bin/env bash
# .simrc - GitSim environment configuration
# This file is automatically sourced by gitsim commands

# SIM_ variables that can be overridden for testing
# These inherit from your shell environment but can be customized here

# Base simulated home (inherits from XDG_HOME or HOME)
SIM_HOME=\${XDG_HOME:-\$HOME}

# Simulated user identity
SIM_USER=\${USER:-testuser}

# Simulated shell environment  
SIM_SHELL=\${SHELL:-/bin/bash}

# Simulated default editor
SIM_EDITOR=\${EDITOR:-nano}

# Simulated locale
SIM_LANG=\${LANG:-en_US.UTF-8}

# Generated files tracking (for cleanup)
GENERATED_FILES=()

# Example custom overrides:
# SIM_USER="alice"
# SIM_EDITOR="vim"
# SIM_HOME="/tmp/custom-sim-home"

# Export variables so they're available to subshells
export SIM_HOME SIM_USER SIM_SHELL SIM_EDITOR SIM_LANG
EOF
    
    return $?
}

################################################################################
# Part 13: part_13_template_system.sh
################################################################################

################################################################################
# Template System - Core Infrastructure
################################################################################

# Template registry - populated dynamically by language modules
declare -A TEMPLATES=()
declare -A TEMPLATE_ALIASES=()

################################################################################
# Template Registration System
################################################################################

# Registration function for language modules to call
_register_template() {
    local name="$1"
    local description="$2"
    local aliases="$3"  # Optional: space-separated aliases
    
    TEMPLATES["$name"]="$description"
    
    # Register aliases if provided
    if [[ -n "$aliases" ]]; then
        for alias in $aliases; do
            TEMPLATE_ALIASES["$alias"]="$name"
        done
    fi
    
    trace "Registered template: $name ($description)"
}

################################################################################
# Mid-Ordinal Template Functions
################################################################################

# Validate template exists and resolve aliases
_validate_template() {
    local template="$1"
    local resolved="$template"
    
    # Check if it's an alias
    if [[ -n "${TEMPLATE_ALIASES[$template]}" ]]; then
        resolved="${TEMPLATE_ALIASES[$template]}"
    fi
    
    # Check if template exists
    if [[ -z "${TEMPLATES[$resolved]}" ]]; then
        error "Unknown template: $template"
        info "Available templates: ${!TEMPLATES[*]}"
        return 1
    fi
    
    printf "%s" "$resolved"
    return 0
}

# Template dispatcher - dynamically calls language-specific functions
_dispatch_template() {
    local template="$1"
    local target_dir="$2"
    local project_name="$3"
    local testsh_flag="${4:-false}"

    # Dynamic function call: _create_rust_template, _create_node_template, etc.
    local create_func="_create_${template}_template"

    if declare -f "$create_func" >/dev/null 2>&1; then
        "$create_func" "$target_dir" "$project_name" "$testsh_flag"
    else
        error "Template implementation not found: $template"
        info "Function $create_func is not defined"
        return 1
    fi
}

# Apply template to specified directory
_apply_template() {
    local template="$1"
    local target_dir="$2"
    local project_name="$3"
    local testsh_flag="${4:-false}"
    local validated_template

    # Validate and resolve template name
    validated_template=$(_validate_template "$template") || return 1

    # Ensure target directory exists
    mkdir -p "$target_dir"

    # Dispatch to language-specific implementation
    _dispatch_template "$validated_template" "$target_dir" "$project_name" "$testsh_flag"
}

# Enhanced init functions with template support
_init_with_template() {
    local template="$1"
    local project_name="$2"
    local target_dir="$3"
    
    # First create the git simulation
    if __create_git_structure "$target_dir/.gitsim/.data"; then
        trace "Created git simulation structure"
    else
        error "Failed to create git simulation structure"
        return 1
    fi
    
    # Then apply the template
    if _apply_template "$template" "$target_dir" "$project_name"; then
        okay "Applied $template template to $target_dir"
        __add_gitignore_entry ".gitsim/"
        return 0
    else
        error "Failed to apply template: $template"
        return 1
    fi
}

################################################################################
# Dispatchable Functions (High-Order)
################################################################################

do_template() {
    local template=""
    local project_name=""
    local target_dir="$PWD"
    local testsh_flag=false

    # Parse arguments and flags
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --testsh)
                testsh_flag=true
                shift
                ;;
            --template=*)
                template="${1#--template=}"
                shift
                ;;
            *)
                if [[ -z "$template" ]]; then
                    template="$1"
                elif [[ -z "$project_name" ]]; then
                    project_name="$1"
                else
                    error "Unexpected argument: $1"
                    return 1
                fi
                shift
                ;;
        esac
    done

    # Set defaults
    [[ -z "$project_name" ]] && project_name="$(basename "$PWD")"

    if [[ -z "$template" ]]; then
        error "Template name required"
        info "Usage: gitsim template <template-name> [project-name] [--testsh]"
        do_template_list
        return 1
    fi

    # If project name provided, create subdirectory
    if [[ "$project_name" != "$(basename "$PWD")" ]]; then
        target_dir="$PWD/$project_name"
    fi

    info "Creating $template template in $target_dir"
    if [[ "$testsh_flag" == true ]]; then
        info "Including TESTSH comprehensive test suite"
    fi

    _apply_template "$template" "$target_dir" "$project_name" "$testsh_flag"
}

do_template_list() {
    if [[ ${#TEMPLATES[@]} -eq 0 ]]; then
        warn "No templates available"
        return 1
    fi
    
    printf "Available templates:\n"
    for template in "${!TEMPLATES[@]}"; do
        printf "  %-10s - %s\n" "$template" "${TEMPLATES[$template]}"
    done
    
    # Show aliases if any exist
    if [[ ${#TEMPLATE_ALIASES[@]} -gt 0 ]]; then
        printf "\nAliases:\n"
        for alias in "${!TEMPLATE_ALIASES[@]}"; do
            printf "  %-10s -> %s\n" "$alias" "${TEMPLATE_ALIASES[$alias]}"
        done
    fi
}

do_template_show() {
    local template="$1"
    local validated_template
    
    if [[ -z "$template" ]]; then
        error "Template name required"
        info "Usage: gitsim template-show <template-name>"
        return 1
    fi
    
    validated_template=$(_validate_template "$template") || return 1
    
    printf "Template: %s\n" "$validated_template"
    printf "Description: %s\n" "${TEMPLATES[$validated_template]}"
    printf "\nThis template creates:\n"
    
    # Call template-specific show function if it exists
    local show_func="_show_${validated_template}_template"
    if declare -f "$show_func" >/dev/null 2>&1; then
        "$show_func"
    else
        info "No detailed preview available for $validated_template template"
    fi
}

################################################################################
# Enhanced Existing Commands
################################################################################

# Enhanced do_init with template support
do_init_with_template() {
    local template="$1"
    local project_name="${2:-$(basename "$PWD")}"
    
    if _init_with_template "$template" "$project_name" "$PWD"; then
        okay "Initialized Git simulator repository with $template template"
        return 0
    else
        error "Failed to initialize with template: $template"
        return 1
    fi
}

# Enhanced do_init_in_home with template support  
do_init_in_home_with_template() {
    local project_name="$1"
    local template="$2"
    local sim_root
    local home_dir
    local project_dir
    
    sim_root=$(_find_sim_root) || {
        # Create a temporary sim root in current directory
        if __create_git_structure ".gitsim/.data"; then
            sim_root="$PWD"
        else
            error "Failed to create temporary sim root"
            return 1
        fi
    }
    
    home_dir=$(_get_sim_home "$sim_root")
    
    # Ensure home is initialized
    if [ ! -d "$home_dir" ]; then
        do_home_init "$sim_root" "$project_name" || return 1
    fi
    
    project_dir=$(_get_sim_project_dir "$home_dir" "$project_name")
    
    # Apply template to project directory
    if _init_with_template "$template" "$project_name" "$project_dir"; then
        okay "Initialized Git simulator repository with $template template in $project_dir"
        info "Project path: $project_dir"
        info "To work in this project: cd '$project_dir'"
        return 0
    else
        error "Failed to initialize project with template: $template"
        return 1
    fi
}

################################################################################
# Common Template Utilities
################################################################################

# Generate README.md - shared across all templates
__print_readme_md() {
    local file="$1"
    local project_name="$2"
    local language="$3"
    
    cat > "$file" << EOF
# $project_name

A sample $language project generated by GitSim for testing purposes.

## Description

This project was automatically generated to provide a realistic structure for testing deployment scripts, build tools, and other development workflows in a safe, isolated environment.

## Generated by GitSim

This project structure is simulated and intended for testing only. It includes:
- Realistic project files and structure
- Fake package/dependency files for build tool compatibility
- Standard configuration files
- Basic example code

## Usage

This project can be used to test:
- Build and deployment scripts
- Package managers and dependency resolution
- Development tooling and workflows
- CI/CD pipeline configurations

Generated on: $(date)
Generated by: GitSim v$(_get_version)
EOF
}

# Generate common .gitignore patterns
__print_common_gitignore() {
    local file="$1"
    
    cat >> "$file" << 'EOF'

# GitSim
.gitsim/
.simrc

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
EOF
}

################################################################################
# Part 14: part_14_templates_rust.sh
################################################################################

################################################################################
# Rust Template Module
################################################################################

# Register this template with the core system
_register_template "rust" "Rust project with Cargo" "rs"

################################################################################
# Rust Template Implementation
################################################################################

# Main creation function (standard interface)
_create_rust_template() {
    local target_dir="$1"
    local project_name="$2"
    
    # Create Rust project structure
    mkdir -p "$target_dir"/{src,tests,examples}
    
    # Generate all Rust project files
    __print_cargo_toml "$target_dir/Cargo.toml" "$project_name"
    __print_rust_main "$target_dir/src/main.rs" "$project_name"
    __print_rust_lib "$target_dir/src/lib.rs" "$project_name"
    __print_rust_integration_test "$target_dir/tests/integration_test.rs" "$project_name"
    __print_rust_example "$target_dir/examples/basic.rs" "$project_name"
    __print_rust_gitignore "$target_dir/.gitignore"
    __print_readme_md "$target_dir/README.md" "$project_name" "Rust"
    
    # Generate fake Cargo.lock for realism
    __print_cargo_lock "$target_dir/Cargo.lock" "$project_name"
    
    trace "Created Rust project structure in $target_dir"
    return 0
}

# Template preview function
_show_rust_template() {
    cat << 'EOF'
Rust project structure:
  Cargo.toml          - Package manifest with dependencies
  Cargo.lock          - Lock file for reproducible builds
  src/
    main.rs           - Binary entry point
    lib.rs            - Library root with basic functions
  tests/
    integration_test.rs - Integration tests
  examples/
    basic.rs          - Usage example
  .gitignore          - Rust-specific ignore patterns
  README.md           - Project documentation

Dependencies included: clap, serde, tokio (dev)
EOF
}

################################################################################
# Rust File Generators
################################################################################

__print_cargo_toml() {
    local file="$1"
    local name="$2"
    
    cat > "$file" << EOF
[package]
name = "$name"
version = "0.1.0"
edition = "2021"
authors = ["$SIM_USER <${SIM_USER}@example.com>"]
description = "A sample Rust project generated by GitSim"
license = "MIT OR Apache-2.0"
repository = "https://github.com/${SIM_USER}/${name}"
keywords = ["cli", "sample", "gitsim"]
categories = ["command-line-utilities"]

[dependencies]
clap = { version = "4.4", features = ["derive"] }
serde = { version = "1.0", features = ["derive"] }
tokio = { version = "1.0", features = ["rt-multi-thread", "macros"] }

[dev-dependencies]
tokio-test = "0.4"

[[bin]]
name = "$name"
path = "src/main.rs"

[[example]]
name = "basic"
path = "examples/basic.rs"

[profile.release]
opt-level = 3
lto = true
codegen-units = 1
panic = "abort"
EOF
}

__print_rust_main() {
    local file="$1"
    local name="$2"
    
    cat > "$file" << EOF
use clap::{Arg, Command};
use std::process;

fn main() {
    let matches = Command::new("$name")
        .version("0.1.0")
        .author("$SIM_USER <${SIM_USER}@example.com>")
        .about("A sample Rust application generated by GitSim")
        .arg(
            Arg::new("name")
                .short('n')
                .long("name")
                .value_name("NAME")
                .help("Name to greet")
                .default_value("World"),
        )
        .arg(
            Arg::new("count")
                .short('c')
                .long("count")
                .value_name("COUNT")
                .help("Number of times to greet")
                .value_parser(clap::value_parser!(u32))
                .default_value("1"),
        )
        .get_matches();

    let name = matches.get_one::<String>("name").unwrap();
    let count = matches.get_one::<u32>("count").unwrap();

    for i in 1..=*count {
        if *count > 1 {
            println!("{}: Hello, {} from $name!", i, name);
        } else {
            println!("Hello, {} from $name!", name);
        }
    }

    // Demonstrate library usage
    let greeting = ${name//-/_}::create_greeting(name);
    println!("Library says: {}", greeting);

    let sum = ${name//-/_}::add(10, 15);
    println!("10 + 15 = {}", sum);

    println!("\\n$name completed successfully!");
}
EOF
}

__print_rust_lib() {
    local file="$1"
    local name="$2"
    local lib_name="${name//-/_}"  # Convert hyphens to underscores for valid Rust identifiers
    
    cat > "$file" << EOF
//! $name library
//!
//! This is a sample library generated by GitSim for testing purposes.
//! It provides basic functionality for greeting users and performing calculations.

use serde::{Deserialize, Serialize};

/// Configuration struct for the application
#[derive(Debug, Serialize, Deserialize)]
pub struct Config {
    pub default_name: String,
    pub max_count: u32,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            default_name: "World".to_string(),
            max_count: 100,
        }
    }
}

/// Creates a greeting message for the given name
///
/// # Arguments
///
/// * \`name\` - The name to include in the greeting
///
/// # Examples
///
/// \`\`\`
/// use $lib_name::create_greeting;
///
/// let greeting = create_greeting("Alice");
/// assert_eq!(greeting, "Greetings, Alice! Welcome to $name.");
/// \`\`\`
pub fn create_greeting(name: &str) -> String {
    format!("Greetings, {}! Welcome to $name.", name)
}

/// Adds two numbers together
///
/// This is a simple utility function for demonstration purposes.
///
/// # Arguments
///
/// * \`left\` - The first number
/// * \`right\` - The second number
///
/// # Examples
///
/// \`\`\`
/// use $lib_name::add;
///
/// let result = add(2, 3);
/// assert_eq!(result, 5);
/// \`\`\`
pub fn add(left: usize, right: usize) -> usize {
    left + right
}

/// Multiplies two numbers
pub fn multiply(a: i32, b: i32) -> i32 {
    a * b
}

/// Validates that a count is within acceptable limits
pub fn validate_count(count: u32, config: &Config) -> Result<(), String> {
    if count > config.max_count {
        Err(format!("Count {} exceeds maximum of {}", count, config.max_count))
    } else {
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_create_greeting() {
        let result = create_greeting("Test");
        assert_eq!(result, "Greetings, Test! Welcome to $name.");
    }

    #[test]
    fn test_add() {
        assert_eq!(add(2, 3), 5);
        assert_eq!(add(0, 0), 0);
        assert_eq!(add(100, 200), 300);
    }

    #[test]
    fn test_multiply() {
        assert_eq!(multiply(4, 5), 20);
        assert_eq!(multiply(-2, 3), -6);
        assert_eq!(multiply(0, 100), 0);
    }

    #[test]
    fn test_validate_count() {
        let config = Config::default();
        
        assert!(validate_count(50, &config).is_ok());
        assert!(validate_count(100, &config).is_ok());
        assert!(validate_count(101, &config).is_err());
    }

    #[test]
    fn test_config_default() {
        let config = Config::default();
        assert_eq!(config.default_name, "World");
        assert_eq!(config.max_count, 100);
    }
}
EOF
}

__print_rust_integration_test() {
    local file="$1"
    local name="$2"
    local lib_name="${name//-/_}"
    
    cat > "$file" << EOF
//! Integration tests for $name
//!
//! These tests verify that the library components work together correctly.

use $lib_name::{create_greeting, add, multiply, validate_count, Config};

#[test]
fn integration_test_greeting_workflow() {
    // Test the complete greeting workflow
    let name = "Integration Test";
    let greeting = create_greeting(name);
    
    assert!(greeting.contains(name));
    assert!(greeting.contains("$name"));
}

#[test]
fn integration_test_math_operations() {
    // Test mathematical operations work together
    let a = 10;
    let b = 5;
    
    let sum = add(a, b);
    let product = multiply(a as i32, b as i32);
    
    assert_eq!(sum, 15);
    assert_eq!(product, 50);
    
    // Test chaining operations
    let result = add(sum, product as usize);
    assert_eq!(result, 65);
}

#[test]
fn integration_test_config_validation() {
    // Test configuration and validation integration
    let config = Config {
        default_name: "TestUser".to_string(),
        max_count: 10,
    };
    
    // Valid count should pass
    assert!(validate_count(5, &config).is_ok());
    
    // Invalid count should fail
    assert!(validate_count(15, &config).is_err());
}

#[tokio::test]
async fn integration_test_async_operations() {
    // Test async functionality (using tokio for realistic project structure)
    let result = async_greeting("Async Test").await;
    assert!(result.contains("Async Test"));
}

// Helper async function for testing
async fn async_greeting(name: &str) -> String {
    tokio::time::sleep(tokio::time::Duration::from_millis(1)).await;
    create_greeting(name)
}
EOF
}

__print_rust_example() {
    local file="$1"
    local name="$2"
    local lib_name="${name//-/_}"
    
    cat > "$file" << EOF
//! Basic usage example for $name
//!
//! This example demonstrates how to use the $name library
//! in your own applications.

use $lib_name::{create_greeting, add, Config, validate_count};

fn main() {
    println!("=== $name Library Example ===\\n");
    
    // Example 1: Basic greeting
    println!("1. Basic greeting:");
    let greeting = create_greeting("Example User");
    println!("   {}", greeting);
    
    // Example 2: Math operations
    println!("\\n2. Math operations:");
    let sum = add(42, 8);
    println!("   42 + 8 = {}", sum);
    
    // Example 3: Configuration and validation
    println!("\\n3. Configuration and validation:");
    let config = Config {
        default_name: "Default User".to_string(),
        max_count: 50,
    };
    
    println!("   Config: default_name='{}', max_count={}", 
             config.default_name, config.max_count);
    
    // Test validation
    match validate_count(25, &config) {
        Ok(_) => println!("   Count 25 is valid"),
        Err(e) => println!("   Error: {}", e),
    }
    
    match validate_count(75, &config) {
        Ok(_) => println!("   Count 75 is valid"),
        Err(e) => println!("   Error: {}", e),
    }
    
    println!("\\n=== Example completed ===");
}
EOF
}

__print_rust_gitignore() {
    local file="$1"
    
    cat > "$file" << 'EOF'
# Rust
/target/
**/*.rs.bk
*.pdb

# Cargo
Cargo.lock

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Local development
.env
*.log
EOF
    
    # Add common patterns
    __print_common_gitignore "$file"
}

__print_cargo_lock() {
    local file="$1"
    local name="$2"
    
    cat > "$file" << EOF
# This file is automatically @generated by Cargo.
# It is not intended for manual editing.
version = 3

[[package]]
name = "$name"
version = "0.1.0"
dependencies = [
 "clap",
 "serde",
 "tokio",
]

[[package]]
name = "clap"
version = "4.4.0"
source = "registry+https://github.com/rust-lang/crates.io-index"
checksum = "fake-checksum-for-gitsim-testing"

[[package]]  
name = "serde"
version = "1.0.0"
source = "registry+https://github.com/rust-lang/crates.io-index"
checksum = "fake-checksum-for-gitsim-testing"

[[package]]
name = "tokio"
version = "1.0.0"
source = "registry+https://github.com/rust-lang/crates.io-index" 
checksum = "fake-checksum-for-gitsim-testing"
EOF
}

################################################################################
# Part 15: part_15_templates_bash.sh
################################################################################

################################################################################
# BashFX Template Module
################################################################################

# Register this template with the core system
_register_template "bash" "BashFX-compliant script project" "sh bashfx"

################################################################################
# BashFX Template Implementation
################################################################################

# Main creation function (standard interface)
_create_bash_template() {
    local target_dir="$1"
    local project_name="$2"
    local testsh_flag="${3:-false}"

    # Create BashFX project structure
    if [[ "$testsh_flag" == true ]]; then
        # Enhanced structure with TESTSH
        mkdir -p "$target_dir"/{parts,tests/{unit,sanity,smoke,integration,e2e,uat,chaos,bench,_adhoc},scripts}
    else
        # Standard structure
        mkdir -p "$target_dir"/{parts,tests}
    fi

    # Generate BashFX project files
    __print_bashfx_script "$target_dir/${project_name}.sh" "$project_name"
    __print_bashfx_buildmap "$target_dir/parts/build.map"
    __print_bashfx_header "$target_dir/parts/01_header.sh" "$project_name"
    __print_bashfx_main "$target_dir/parts/02_main.sh" "$project_name"
    __print_bashfx_build_script "$target_dir/build.sh" "$project_name"

    # Choose test runner based on testsh flag
    if [[ "$testsh_flag" == true ]]; then
        __print_testsh_bash_runner "$target_dir/test.sh" "$project_name"
        __print_testsh_bootstrap_bash "$target_dir/scripts/bootstrap-tests.sh" "$project_name"
        __print_testsh_bash_examples "$target_dir" "$project_name"
        __print_testsh_gitignore "$target_dir/.gitignore"
    else
        __print_bash_test_runner "$target_dir/test_runner.sh" "$project_name"
        __print_bash_gitignore "$target_dir/.gitignore"
    fi

    __print_readme_md "$target_dir/README.md" "$project_name" "BashFX"

    # Make scripts executable
    chmod +x "$target_dir/${project_name}.sh"
    chmod +x "$target_dir/build.sh"

    if [[ "$testsh_flag" == true ]]; then
        chmod +x "$target_dir/test.sh"
        chmod +x "$target_dir/scripts/bootstrap-tests.sh"
        chmod +x "$target_dir/tests/_adhoc"/*.sh 2>/dev/null || true
    else
        chmod +x "$target_dir/test_runner.sh"
    fi

    trace "Created BashFX project structure in $target_dir"
    if [[ "$testsh_flag" == true ]]; then
        trace "Included TESTSH comprehensive test suite"
    fi
    return 0
}

# Template preview function
_show_bash_template() {
    cat << 'EOF'
BashFX project structure:
  project.sh          - Main BashFX-compliant script
  build.sh            - Modular build system
  parts/
    build.map         - Build configuration
    01_header.sh      - Script header with metadata
    02_main.sh        - Main function and execution
  tests/
  test_runner.sh      - Test framework
  .gitignore          - Bash-specific ignore patterns  
  README.md           - Project documentation

Features: Full BashFX 2.0 compliance, modular build system, proper function ordinality
EOF
}

################################################################################
# BashFX File Generators
################################################################################

__print_bashfx_script() {
    local file="$1"
    local name="$2"
    
    cat > "$file" << EOF
#!/usr/bin/env bash
#
# $name - BashFX-Compliant Script
#
# name: $name
# version: 1.0.0
# desc: Sample BashFX-compliant script generated by GitSim
# author: $SIM_USER
#
# portable: grep, sed, awk, find
# builtins: printf, read, local, declare, case, if, for, while, shift, return

################################################################################
# Configuration & Standards
################################################################################

readonly SCRIPT_NAME="$name"
readonly SCRIPT_VERSION="1.0.0"

# XDG+ Configuration
: \${XDG_HOME:="\$HOME/.local"}
: \${XDG_DATA_HOME:="\$XDG_HOME/data"}
: \${XDG_CONFIG_HOME:="\$HOME/.config"}

# Standard option flags
opt_debug=false
opt_trace=false
opt_quiet=false
opt_force=false
opt_yes=false

################################################################################
# stderr functions
################################################################################

stderr() { printf "%s\\n" "\$*" >&2; }
info() { [[ "\$opt_quiet" == true ]] && return; stderr "[INFO] \$*"; }
warn() { [[ "\$opt_quiet" == true ]] && return; stderr "[WARN] \$*"; }
error() { stderr "[ERROR] \$*"; }
fatal() { stderr "[FATAL] \$*"; exit 1; }
okay() { [[ "\$opt_quiet" == true ]] && return; stderr "[OK] \$*"; }
trace() { [[ "\$opt_trace" == true ]] && stderr "[TRACE] \$*"; }

################################################################################
# Helper Functions
################################################################################

_logo() {
    cat << 'LOGO_EOF'
 _____ _____ _____ _____ 
|   __|     | __  |     |
|__   |   --|    -|-   -|
|_____|_____|__|__|_____|
$name v$SCRIPT_VERSION
LOGO_EOF
}

_validate_input() {
    local input="\$1"
    
    if [[ -z "\$input" ]]; then
        error "Input required"
        return 1
    fi
    
    return 0
}

################################################################################
# Dispatchable Functions (High-Order)
################################################################################

do_hello() {
    local name="\${1:-World}"
    
    if ! _validate_input "\$name"; then
        return 1
    fi
    
    okay "Hello, \$name from \$SCRIPT_NAME!"
    trace "Greeting completed for: \$name"
    return 0
}

do_demo() {
    info "Running \$SCRIPT_NAME demonstration"
    
    _logo
    
    printf "\\nThis is a BashFX-compliant script with:\\n"
    printf "- Proper function ordinality\\n"
    printf "- XDG+ directory compliance\\n"
    printf "- Standard option parsing\\n"
    printf "- Modular build system support\\n"
    printf "- Comprehensive error handling\\n"
    
    okay "Demo completed successfully"
    return 0
}

do_status() {
    printf "Script: %s\\n" "\$SCRIPT_NAME"
    printf "Version: %s\\n" "\$SCRIPT_VERSION"
    printf "Author: %s\\n" "$SIM_USER"
    printf "Debug: %s\\n" "\$opt_debug"
    printf "Quiet: %s\\n" "\$opt_quiet"
    printf "XDG_HOME: %s\\n" "\$XDG_HOME"
    return 0
}

do_version() {
    printf "%s v%s\\n" "\$SCRIPT_NAME" "\$SCRIPT_VERSION"
    return 0
}

################################################################################
# Core System Functions  
################################################################################

dispatch() {
    local cmd="\$1"
    shift
    
    case "\$cmd" in
        hello)   do_hello "\$@";;
        demo)    do_demo "\$@";;
        status)  do_status "\$@";;
        version) do_version "\$@";;
        *)
            error "Unknown command: \$cmd"
            usage
            return 1
            ;;
    esac
}

usage() {
    cat << 'USAGE_EOF'
$name - BashFX-Compliant Script

USAGE:
    $name <command> [options] [args]

COMMANDS:
    hello [name]        Greet someone (default: World)
    demo               Run demonstration
    status             Show script status
    version            Show version information

OPTIONS:
    -d, --debug        Enable debug output
    -t, --trace        Enable trace output (implies -d)
    -q, --quiet        Suppress all output except errors
    -f, --force        Force operations, bypass safety checks
    -y, --yes          Automatically answer yes to prompts

EXAMPLES:
    $name hello Alice
    $name demo
    $name status
    
This script follows BashFX 2.0 architecture standards.
    
USAGE_EOF
}

options() {
    local this next opts=("\$@")
    for ((i=0; i<\${#opts[@]}; i++)); do
        this=\${opts[i]}
        next=\${opts[i+1]}
        case "\$this" in
            -d|--debug)
                opt_debug=true
                ;;
            -t|--trace)
                opt_trace=true
                opt_debug=true
                ;;
            -q|--quiet)
                opt_quiet=true
                ;;
            -f|--force)
                opt_force=true
                ;;
            -y|--yes)
                opt_yes=true
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                :
                ;;
        esac
    done
}

main() {
    # Show logo unless quiet
    if [[ "\$opt_quiet" != true ]]; then
        _logo
        printf "\\n"
    fi
    
    # Show help if no command provided
    if [[ \${#@} -eq 0 ]]; then
        usage
        exit 0
    fi
    
    # Dispatch to command
    dispatch "\$@"
}

# Script execution using BashFX pattern
if [ "\$0" = "-bash" ]; then
    :
else
    # direct call
    orig_args=("\$@")
    options "\${orig_args[@]}"
    args=("\${orig_args[@]##-*}") # delete anything that looks like an option
    main "\${args[@]}"
    ret=\$?
fi
EOF
}

__print_bashfx_buildmap() {
    local file="$1"
    
    cat > "$file" << 'EOF'
# Build Map for BashFX Project
# Format: NN : target_filename.sh
# Lines starting with # are ignored
# Place this file in: parts/build.map

01 : 01_header.sh
02 : 02_main.sh
EOF
}

__print_bashfx_header() {
    local file="$1"
    local name="$2"
    
    cat > "$file" << EOF
#!/usr/bin/env bash
#
# $name - BashFX-Compliant Script
#
# name: $name
# version: 1.0.0
# desc: Sample BashFX-compliant script generated by GitSim
# author: $SIM_USER
#
# portable: grep, sed, awk, find
# builtins: printf, read, local, declare, case, if, for, while, shift, return
EOF
}

__print_bashfx_main() {
    local file="$1"
    local name="$2"
    
    cat > "$file" << EOF
main() {
    # Show logo unless quiet
    if [[ "\$opt_quiet" != true ]]; then
        _logo
        printf "\\n"
    fi
    
    # Show help if no command provided
    if [[ \${#@} -eq 0 ]]; then
        usage
        exit 0
    fi
    
    # Dispatch to command
    dispatch "\$@"
}

# Script execution using BashFX pattern
if [ "\$0" = "-bash" ]; then
    :
else
    # direct call
    orig_args=("\$@")
    options "\${orig_args[@]}"
    args=("\${orig_args[@]##-*}") # delete anything that looks like an option
    main "\${args[@]}"
    ret=\$?
fi
EOF
}

__print_bashfx_build_script() {
    local file="$1"
    local name="$2"
    
    cat > "$file" << EOF
#!/usr/bin/env bash
#
# build.sh - BashFX Build Script for $name
#

# Configuration
OUTPUT_FILE="$name.sh"
PARTS_DIR="parts"
BUILD_MAP="\$PARTS_DIR/build.map"
BACKUP_SUFFIX=".bak"

# Colors for output
readonly RED=\$'\\033[31m'
readonly GREEN=\$'\\033[32m' 
readonly YELLOW=\$'\\033[33m'
readonly BLUE=\$'\\033[34m'
readonly RESET=\$'\\033[0m'

# Logging functions
info() { printf "%s[INFO]%s %s\\n" "\$BLUE" "\$RESET" "\$*" >&2; }
okay() { printf "%s[OK]%s %s\\n" "\$GREEN" "\$RESET" "\$*" >&2; }
warn() { printf "%s[WARN]%s %s\\n" "\$YELLOW" "\$RESET" "\$*" >&2; }
error() { printf "%s[ERROR]%s %s\\n" "\$RED" "\$RESET" "\$*" >&2; }
fatal() { error "\$*"; exit 1; }

# Validate build environment
check_environment() {
    [[ -d "\$PARTS_DIR" ]] || fatal "Parts directory '\$PARTS_DIR' not found"
    [[ -f "\$BUILD_MAP" ]] || fatal "Build map '\$BUILD_MAP' not found"
    info "Environment validated"
}

# Build the output file from parts
build_script() {
    local temp_file="\${OUTPUT_FILE}.tmp"
    local parts_used=0
    
    info "Building \$OUTPUT_FILE from parts..."
    
    # Create temporary file
    > "\$temp_file"
    
    # Process build map
    while IFS= read -r line; do
        # Skip comments and empty lines
        [[ "\$line" =~ ^\[[:space:\]\]*# ]] && continue
        [[ -z "\${line// }" ]] && continue
        
        # Parse map entry: "NN : filename.sh"
        if [[ "\$line" =~ ^([0-9]+)[[:space:]]*:[[:space:]]*(.+)\$ ]]; then
            local part_num="\${BASH_REMATCH[1]}"
            local part_file="\${BASH_REMATCH[2]// /}" # Remove spaces
            local part_path="\$PARTS_DIR/\$part_file"
            
            if [[ -f "\$part_path" ]]; then
                info "Adding part \$part_num: \$part_file"
                cat "\$part_path" >> "\$temp_file"
                echo >> "\$temp_file"  # Add newline between parts
                ((parts_used++))
            else
                warn "Part file not found: \$part_path"
            fi
        fi
    done < "\$BUILD_MAP"
    
    if [[ \$parts_used -eq 0 ]]; then
        fatal "No parts were processed"
    fi
    
    # Backup existing file if it exists
    if [[ -f "\$OUTPUT_FILE" ]]; then
        cp "\$OUTPUT_FILE" "\${OUTPUT_FILE}\${BACKUP_SUFFIX}"
        info "Backed up existing file to \${OUTPUT_FILE}\${BACKUP_SUFFIX}"
    fi
    
    # Move temp file to final location
    mv "\$temp_file" "\$OUTPUT_FILE"
    chmod +x "\$OUTPUT_FILE"
    
    okay "Built \$OUTPUT_FILE from \$parts_used parts"
}

# Main execution
main() {
    case "\${1:-build}" in
        build)
            check_environment
            build_script
            ;;
        clean)
            rm -f "\${OUTPUT_FILE}.tmp" "\${OUTPUT_FILE}\${BACKUP_SUFFIX}"
            okay "Cleaned build artifacts"
            ;;
        *)
            echo "Usage: \$0 [build|clean]"
            exit 1
            ;;
    esac
}

main "\$@"
EOF
}

__print_bash_test_runner() {
    local file="$1"
    local name="$2"
    
    cat > "$file" << EOF
#!/usr/bin/env bash
# test_runner.sh - Test Framework for $name

set -e

# Test configuration
readonly TEST_SCRIPT="./$name.sh"
readonly RED=\$'\\033[31m'
readonly GREEN=\$'\\033[32m'
readonly RESET=\$'\\033[0m'

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

echo "=== Running Tests for $name ==="
echo

# Test framework functions
test_start() {
    local description="\$1"
    printf "Testing: %s ... " "\$description"
    ((TESTS_RUN++))
}

test_pass() {
    printf "%s✓ PASS%s\\n" "\$GREEN" "\$RESET"
    ((TESTS_PASSED++))
}

test_fail() {
    local message="\$1"
    printf "%s✗ FAIL%s" "\$RED" "\$RESET"
    [[ -n "\$message" ]] && printf " - %s" "\$message"
    printf "\\n"
    ((TESTS_FAILED++))
}

# Individual test functions
test_version() {
    test_start "version command"
    local output
    if output=\$("\$TEST_SCRIPT" version 2>&1); then
        if [[ "\$output" == *"$name v1.0.0"* ]]; then
            test_pass
        else
            test_fail "Expected version string not found"
        fi
    else
        test_fail "Command failed"
    fi
}

test_hello() {
    test_start "hello command"
    local output
    if output=\$("\$TEST_SCRIPT" hello Alice 2>&1); then
        if [[ "\$output" == *"Hello, Alice"* ]]; then
            test_pass
        else
            test_fail "Expected greeting not found"
        fi
    else
        test_fail "Command failed"
    fi
}

test_demo() {
    test_start "demo command"
    local output
    if output=\$("\$TEST_SCRIPT" demo 2>&1); then
        if [[ "\$output" == *"demonstration"* ]]; then
            test_pass
        else
            test_fail "Demo output not as expected"
        fi
    else
        test_fail "Command failed"
    fi
}

test_status() {
    test_start "status command"
    local output
    if output=\$("\$TEST_SCRIPT" status 2>&1); then
        if [[ "\$output" == *"Script: $name"* ]]; then
            test_pass
        else
            test_fail "Status output not as expected"
        fi
    else
        test_fail "Command failed"
    fi
}

test_invalid_command() {
    test_start "invalid command handling"
    local output
    if output=\$("\$TEST_SCRIPT" invalid_command 2>&1); then
        # Should fail (return non-zero)
        test_fail "Command should have failed"
    else
        if [[ "\$output" == *"Unknown command"* ]]; then
            test_pass
        else
            test_fail "Expected error message not found"
        fi
    fi
}

test_help() {
    test_start "help output"
    local output
    if output=\$("\$TEST_SCRIPT" --help 2>&1); then
        if [[ "\$output" == *"USAGE:"* ]] && [[ "\$output" == *"COMMANDS:"* ]]; then
            test_pass
        else
            test_fail "Help format not as expected"
        fi
    else
        test_fail "Help command failed"
    fi
}

# Run all tests
run_tests() {
    # Check if script exists
    if [[ ! -f "\$TEST_SCRIPT" ]]; then
        echo "Error: Test script \$TEST_SCRIPT not found"
        echo "Run 'build.sh' first to create the script"
        exit 1
    fi
    
    # Run individual tests
    test_version
    test_hello
    test_demo
    test_status
    test_invalid_command
    test_help
}

# Show results
show_results() {
    echo
    echo "=== Test Results ==="
    printf "Tests run: %d\\n" "\$TESTS_RUN"
    printf "%sPassed: %d%s\\n" "\$GREEN" "\$TESTS_PASSED" "\$RESET"
    
    if [[ \$TESTS_FAILED -gt 0 ]]; then
        printf "%sFailed: %d%s\\n" "\$RED" "\$TESTS_FAILED" "\$RESET"
        echo
        echo "❌ Some tests failed"
        exit 1
    else
        echo
        echo "✅ All tests passed!"
    fi
}

# Main execution
main() {
    run_tests
    show_results
}

main "\$@"
EOF
}

__print_bash_gitignore() {
    local file="$1"
    
    cat > "$file" << 'EOF'
# Build artifacts
*.tmp
*.bak
build/
dist/

# BashFX build system
parts/*.tmp
EOF
    
    # Add common patterns
    __print_common_gitignore "$file"
}

################################################################################
# TESTSH Integration Functions for Bash Template
################################################################################

__print_testsh_bash_runner() {
    local file="$1"
    local name="$2"

    cat > "$file" << EOF
#!/usr/bin/env bash
# test.sh - TESTSH-Compliant Test Runner for $name (BashFX integration)
#
# Supports hierarchical test execution with BashFX project structure

set -e

# Configuration
readonly SCRIPT_NAME="test.sh"
readonly SCRIPT_VERSION="1.0.0"
readonly PROJECT_NAME="$name"
readonly PROJECT_SCRIPT="./$name.sh"

# Colors for output
readonly RED=\$'\\033[31m'
readonly GREEN=\$'\\033[32m'
readonly YELLOW=\$'\\033[33m'
readonly BLUE=\$'\\033[34m'
readonly RESET=\$'\\033[0m'

# Test categories in execution order
readonly TEST_CATEGORIES=(
    "sanity"
    "smoke"
    "unit"
    "integration"
    "e2e"
    "uat"
    "chaos"
    "bench"
)

# Logging functions
info() { printf "%s[INFO]%s %s\\n" "\$BLUE" "\$RESET" "\$*" >&2; }
okay() { printf "%s[OK]%s %s\\n" "\$GREEN" "\$RESET" "\$*" >&2; }
warn() { printf "%s[WARN]%s %s\\n" "\$YELLOW" "\$RESET" "\$*" >&2; }
error() { printf "%s[ERROR]%s %s\\n" "\$RED" "\$RESET" "\$*" >&2; }

# BashFX integration - ensure project is built
ensure_project_built() {
    if [[ -f "build.sh" ]] && [[ ! -f "\$PROJECT_SCRIPT" || "build.sh" -nt "\$PROJECT_SCRIPT" ]]; then
        info "Building project before running tests..."
        bash build.sh build
    fi
}

# Test execution functions
run_category_tests() {
    local category="\$1"
    local test_dir="tests/\$category"
    local tests_found=0
    local tests_passed=0

    info "Running \$category tests..."

    # Run bash test files in category directory
    if [[ -d "\$test_dir" ]]; then
        for test_file in "\$test_dir"/*.sh; do
            [[ -f "\$test_file" ]] || continue
            [[ -x "\$test_file" ]] || continue

            info "Executing: \$(basename "\$test_file")"
            if bash "\$test_file"; then
                (( tests_passed++ ))
            fi
            (( tests_found++ ))
        done
    fi

    # Check for category wrapper script
    if [[ -f "tests/\$category.sh" ]]; then
        info "Executing category wrapper: \$category.sh"
        if bash "tests/\$category.sh"; then
            (( tests_passed++ ))
        fi
        (( tests_found++ ))
    fi

    if [[ \$tests_found -eq 0 ]]; then
        warn "No tests found for category: \$category"
    else
        okay "\$category: \$tests_passed/\$tests_found tests passed"
    fi

    return \$(( tests_found - tests_passed ))
}

run_adhoc_tests() {
    local adhoc_dir="tests/_adhoc"
    local tests_found=0
    local tests_passed=0

    info "Running adhoc tests..."

    if [[ -d "\$adhoc_dir" ]]; then
        for test_file in "\$adhoc_dir"/*; do
            [[ -f "\$test_file" ]] || continue
            [[ -x "\$test_file" ]] || continue

            info "Executing adhoc: \$(basename "\$test_file")"
            if "\$test_file"; then
                (( tests_passed++ ))
            fi
            (( tests_found++ ))
        done
    fi

    if [[ \$tests_found -eq 0 ]]; then
        warn "No adhoc tests found"
    else
        okay "adhoc: \$tests_passed/\$tests_found tests passed"
    fi

    return \$(( tests_found - tests_passed ))
}

# Command implementations
cmd_list() {
    info "Available test categories for \$PROJECT_NAME:"
    for category in "\${TEST_CATEGORIES[@]}"; do
        local count=0
        local wrapper_exists=false

        # Check for category wrapper
        [[ -f "tests/\$category.sh" ]] && wrapper_exists=true

        # Count individual test files
        if [[ -d "tests/\$category" ]]; then
            count=\$(find "tests/\$category" -name "*.sh" -type f | wc -l)
        fi

        printf "  %-12s" "\$category"
        [[ "\$wrapper_exists" == true ]] && printf "[wrapper] "
        printf "(%d files)\\n" "\$count"
    done

    # Count adhoc tests
    local adhoc_count=0
    if [[ -d "tests/_adhoc" ]]; then
        adhoc_count=\$(find "tests/_adhoc" -type f -executable | wc -l)
    fi
    printf "  %-12s(%d files)\\n" "_adhoc" "\$adhoc_count"
}

cmd_run() {
    local category="\$1"

    # Ensure project is built before testing
    ensure_project_built

    if [[ -z "\$category" ]]; then
        # Run all categories
        local total_failures=0

        info "Running all test categories for \$PROJECT_NAME"

        for cat in "\${TEST_CATEGORIES[@]}"; do
            run_category_tests "\$cat" || (( total_failures++ ))
        done

        # Run adhoc tests
        run_adhoc_tests || (( total_failures++ ))

        if [[ \$total_failures -eq 0 ]]; then
            okay "All test categories passed!"
        else
            error "\$total_failures test categories had failures"
            return 1
        fi
    else
        # Run specific category
        if [[ " \${TEST_CATEGORIES[*]} " =~ " \$category " ]]; then
            run_category_tests "\$category"
        elif [[ "\$category" == "adhoc" ]]; then
            run_adhoc_tests
        else
            error "Unknown test category: \$category"
            info "Available categories: \${TEST_CATEGORIES[*]} adhoc"
            return 1
        fi
    fi
}

cmd_bootstrap() {
    if [[ -f "scripts/bootstrap-tests.sh" ]]; then
        info "Running test structure bootstrap..."
        bash scripts/bootstrap-tests.sh "bash"
    else
        error "Bootstrap script not found: scripts/bootstrap-tests.sh"
        return 1
    fi
}

cmd_build() {
    if [[ -f "build.sh" ]]; then
        info "Building project..."
        bash build.sh build
    else
        error "Build script not found: build.sh"
        return 1
    fi
}

cmd_clean() {
    info "Cleaning test and build artifacts..."

    # Clean test artifacts
    find tests/ -name "*.tmp" -delete 2>/dev/null || true

    # Clean build artifacts if build.sh exists
    if [[ -f "build.sh" ]]; then
        bash build.sh clean 2>/dev/null || true
    fi

    okay "Artifacts cleaned"
}

# Usage information
usage() {
    cat << USAGE_EOF
\$SCRIPT_NAME v\$SCRIPT_VERSION - TESTSH Test Runner for \$PROJECT_NAME

USAGE:
    \$SCRIPT_NAME <command> [args]

COMMANDS:
    list                   List all test categories and counts
    run [category]         Run tests (all categories if none specified)
    bootstrap              Initialize TESTSH test structure for bash
    build                  Build the project using build.sh
    clean                  Clean test and build artifacts

TEST CATEGORIES:
    sanity, smoke, unit, integration, e2e, uat, chaos, bench, adhoc

EXAMPLES:
    \$SCRIPT_NAME list
    \$SCRIPT_NAME run
    \$SCRIPT_NAME run sanity
    \$SCRIPT_NAME bootstrap
    \$SCRIPT_NAME build
    \$SCRIPT_NAME clean

BASHFX INTEGRATION:
    - Automatically builds project before testing if needed
    - Supports modular build system via build.sh
    - Compatible with BashFX project structure

USAGE_EOF
}

# Main execution
main() {
    case "\${1:-run}" in
        list|ls)
            cmd_list
            ;;
        run|test)
            shift
            cmd_run "\$@"
            ;;
        bootstrap|init)
            cmd_bootstrap
            ;;
        build)
            cmd_build
            ;;
        clean)
            cmd_clean
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            error "Unknown command: \$1"
            usage
            return 1
            ;;
    esac
}

main "\$@"
EOF
}

__print_testsh_bootstrap_bash() {
    local file="$1"
    local name="$2"

    cat > "$file" << EOF
#!/usr/bin/env bash
# scripts/bootstrap-tests.sh - TESTSH Structure Generator for $name
# Generates bash-specific test structure for BashFX projects

set -euo pipefail

# Colors for output
readonly GREEN=\$'\\033[32m'
readonly BLUE=\$'\\033[34m'
readonly RESET=\$'\\033[0m'

info() { printf "%s[INFO]%s %s\\n" "\$BLUE" "\$RESET" "\$*"; }
okay() { printf "%s[OK]%s %s\\n" "\$GREEN" "\$RESET" "\$*"; }

cat_wrapper() {
    local name="\$1"

    cat > "tests/\${name}.sh" <<BASH_EOF
#!/usr/bin/env bash
# tests/\${name}.sh - \${name} test wrapper for $name

# Source the main script for testing (after building)
if [[ -f "./$name.sh" ]]; then
    # Test by executing commands rather than sourcing
    TEST_SCRIPT="./$name.sh"
else
    echo "Error: Project script not found. Run 'bash build.sh' first."
    exit 1
fi

echo "Running \${name} tests for $name"

# Add your \${name} test logic here
# Example: \\\$TEST_SCRIPT version

exit 0
BASH_EOF
    chmod +x "tests/\${name}.sh"
}

main() {
    info "Bootstrapping TESTSH structure for bash project: $name"

    # Ensure test directories exist
    mkdir -p tests/{unit,sanity,smoke,integration,e2e,uat,chaos,bench,_adhoc}

    # Create top-level test wrappers
    info "Creating top-level test wrappers..."
    cat_wrapper "sanity"
    cat_wrapper "smoke"
    cat_wrapper "unit"
    cat_wrapper "integration"
    cat_wrapper "e2e"
    cat_wrapper "uat"
    cat_wrapper "chaos"
    cat_wrapper "bench"

    # Create category examples
    info "Creating category examples..."
    cat > tests/sanity/basic.sh <<'BASH_EOF'
#!/usr/bin/env bash
# tests/sanity/basic.sh - Basic sanity checks

# Project structure checks
test_project_structure() {
    [[ -f "build.sh" ]] || { echo "build.sh missing"; return 1; }
    [[ -f "parts/build.map" ]] || { echo "parts/build.map missing"; return 1; }
    [[ -d "parts" ]] || { echo "parts directory missing"; return 1; }
    echo "Project structure is sane"
    return 0
}

# Build system check
test_build_system() {
    if ! bash build.sh build; then
        echo "Build system failed"
        return 1
    fi
    echo "Build system is working"
    return 0
}

# Run tests
test_project_structure
test_build_system
BASH_EOF
    chmod +x tests/sanity/basic.sh

    cat > tests/smoke/quick.sh <<'BASH_EOF'
#!/usr/bin/env bash
# tests/smoke/quick.sh - Quick smoke tests

PROJECT_SCRIPT="./$name.sh"

test_script_executable() {
    [[ -x "\$PROJECT_SCRIPT" ]] || { echo "Script not executable"; return 1; }
    echo "Script is executable"
    return 0
}

test_help_command() {
    if ! "\$PROJECT_SCRIPT" --help >/dev/null 2>&1; then
        echo "Help command failed"
        return 1
    fi
    echo "Help command works"
    return 0
}

test_version_command() {
    if ! "\$PROJECT_SCRIPT" version >/dev/null 2>&1; then
        echo "Version command failed"
        return 1
    fi
    echo "Version command works"
    return 0
}

# Run tests
test_script_executable
test_help_command
test_version_command
BASH_EOF
    chmod +x tests/smoke/quick.sh

    # Create adhoc skeleton
    info "Creating adhoc test skeleton..."
    cat > tests/_adhoc/demo.sh <<'ADHOC_EOF'
#!/usr/bin/env bash
# tests/_adhoc/demo.sh - Example adhoc test for $name

echo "This is an adhoc test for $name"
echo "Testing specific functionality or edge cases"

# Example test
if [[ -f "./$name.sh" ]]; then
    echo "Project script found"
else
    echo "Project script missing - run build.sh first"
    exit 1
fi

exit 0
ADHOC_EOF
    chmod +x tests/_adhoc/demo.sh

    okay "TESTSH structure bootstrapped for bash project"
    info "Run '../test.sh list' to see available test categories"
    info "Run '../test.sh bootstrap' to regenerate this structure"
}

main "\$@"
EOF
}

__print_testsh_bash_examples() {
    local target_dir="$1"
    local name="$2"

    # Create comprehensive examples for bash testing
    cat > "$target_dir/tests/unit/functions.sh" << EOF
#!/usr/bin/env bash
# tests/unit/functions.sh - Unit tests for individual functions

# This would test individual functions from your script
# Note: BashFX scripts are typically tested via CLI rather than sourcing

echo "Unit testing individual functions (if applicable)"

# Example: If you expose functions for testing
# test_validate_input() {
#     # Test input validation logic
#     return 0
# }

exit 0
EOF
    chmod +x "$target_dir/tests/unit/functions.sh"

    cat > "$target_dir/tests/integration/workflow.sh" << EOF
#!/usr/bin/env bash
# tests/integration/workflow.sh - Integration workflow tests

PROJECT_SCRIPT="./$name.sh"

test_complete_workflow() {
    echo "Testing complete workflow integration"

    # Example workflow test
    if ! "\$PROJECT_SCRIPT" demo >/dev/null 2>&1; then
        echo "Demo workflow failed"
        return 1
    fi

    echo "Integration workflow passed"
    return 0
}

test_complete_workflow
EOF
    chmod +x "$target_dir/tests/integration/workflow.sh"
}

################################################################################
# Part 16: part_16_templates_node.sh
################################################################################

################################################################################
# Node.js Template Module
################################################################################

# Register this template with the core system
_register_template "node" "Node.js project with npm" "js javascript npm"

################################################################################
# Node.js Template Implementation
################################################################################

# Main creation function (standard interface)
_create_node_template() {
    local target_dir="$1" 
    local project_name="$2"
    
    # Create Node.js project structure
    mkdir -p "$target_dir"/{src,test,config}
    
    # Generate Node.js project files
    __print_package_json "$target_dir/package.json" "$project_name"
    __print_node_index "$target_dir/src/index.js" "$project_name"
    __print_node_server "$target_dir/src/server.js" "$project_name"
    __print_node_utils "$target_dir/src/utils.js" "$project_name"
    __print_node_test "$target_dir/test/index.test.js" "$project_name"
    __print_node_config "$target_dir/config/default.json" "$project_name"
    __print_node_gitignore "$target_dir/.gitignore"
    __print_node_eslintrc "$target_dir/.eslintrc.js"
    __print_node_nvmrc "$target_dir/.nvmrc"
    __print_readme_md "$target_dir/README.md" "$project_name" "Node.js"
    
    # Generate fake package-lock.json for realism
    __print_package_lock_json "$target_dir/package-lock.json" "$project_name"
    
    trace "Created Node.js project structure in $target_dir"
    return 0
}

# Template preview function
_show_node_template() {
    cat << 'EOF'
Node.js project structure:
  package.json        - NPM package manifest with scripts
  package-lock.json   - Dependency lock file
  src/
    index.js          - Main application entry point
    server.js         - Express server implementation  
    utils.js          - Utility functions
  test/
    index.test.js     - Test suite
  config/
    default.json      - Configuration file
  .eslintrc.js        - ESLint configuration
  .nvmrc              - Node version specification
  .gitignore          - Node-specific ignore patterns
  README.md           - Project documentation

Dependencies: express, lodash, config
Dev Dependencies: jest, eslint, nodemon
EOF
}

################################################################################
# Node.js File Generators
################################################################################

__print_package_json() {
    local file="$1"
    local name="$2"
    
    cat > "$file" << EOF
{
  "name": "$name",
  "version": "1.0.0",
  "description": "A sample Node.js project generated by GitSim",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "dev": "nodemon src/index.js",
    "server": "node src/server.js",
    "test": "jest",
    "test:watch": "jest --watch",
    "lint": "eslint src/ test/",
    "lint:fix": "eslint src/ test/ --fix",
    "build": "echo 'Build step would go here'",
    "clean": "rm -rf node_modules package-lock.json"
  },
  "keywords": [
    "nodejs",
    "express",
    "sample",
    "gitsim"
  ],
  "author": "$SIM_USER",
  "license": "MIT",
  "dependencies": {
    "express": "^4.18.2",
    "lodash": "^4.17.21",
    "config": "^3.3.9",
    "cors": "^2.8.5",
    "helmet": "^7.0.0"
  },
  "devDependencies": {
    "jest": "^29.6.2",
    "eslint": "^8.45.0",
    "nodemon": "^3.0.1",
    "supertest": "^6.3.3"
  },
  "engines": {
    "node": ">=16.0.0",
    "npm": ">=8.0.0"
  },
  "repository": {
    "type": "git",
    "url": "https://github.com/${SIM_USER}/${name}.git"
  },
  "jest": {
    "testEnvironment": "node",
    "collectCoverageFrom": [
      "src/**/*.js"
    ],
    "coverageDirectory": "coverage"
  }
}
EOF
}

__print_node_index() {
    local file="$1"
    local name="$2"
    
    cat > "$file" << EOF
// $name - Main application entry point
const config = require('config');
const { createGreeting, formatMessage } = require('./utils');

/**
 * Main application class
 */
class Application {
    constructor(options = {}) {
        this.name = '$name';
        this.version = '1.0.0';
        this.config = { ...config, ...options };
    }

    /**
     * Initialize the application
     */
    async initialize() {
        console.log(formatMessage('info', \`Initializing \${this.name} v\${this.version}\`));
        
        // Simulate some startup tasks
        await this.loadConfiguration();
        await this.setupServices();
        
        console.log(formatMessage('success', 'Application initialized successfully'));
    }

    /**
     * Load configuration
     */
    async loadConfiguration() {
        console.log(formatMessage('info', 'Loading configuration...'));
        
        // Simulate async config loading
        await new Promise(resolve => setTimeout(resolve, 100));
        
        this.config.loaded = true;
    }

    /**
     * Setup services
     */
    async setupServices() {
        console.log(formatMessage('info', 'Setting up services...'));
        
        // Simulate service setup
        await new Promise(resolve => setTimeout(resolve, 50));
        
        this.services = {
            database: { connected: true },
            cache: { connected: true },
            logger: { initialized: true }
        };
    }

    /**
     * Run the main application logic
     */
    async run() {
        try {
            await this.initialize();
            
            // Main application logic
            const greeting = createGreeting('$name User');
            console.log(greeting);
            
            console.log('\\nApplication Status:');
            console.log(\`- Name: \${this.name}\`);
            console.log(\`- Version: \${this.version}\`);
            console.log(\`- Environment: \${process.env.NODE_ENV || 'development'}\`);
            console.log(\`- Services: \${Object.keys(this.services).join(', ')}\`);
            
            console.log(formatMessage('success', 'Application completed successfully'));
            
        } catch (error) {
            console.error(formatMessage('error', \`Application failed: \${error.message}\`));
            process.exit(1);
        }
    }

    /**
     * Graceful shutdown
     */
    async shutdown() {
        console.log(formatMessage('info', 'Shutting down application...'));
        
        // Cleanup logic would go here
        await new Promise(resolve => setTimeout(resolve, 100));
        
        console.log(formatMessage('success', 'Application shutdown complete'));
    }
}

// Run if called directly
if (require.main === module) {
    const app = new Application();
    
    // Handle graceful shutdown
    process.on('SIGINT', async () => {
        console.log('\\n'); // New line after ^C
        await app.shutdown();
        process.exit(0);
    });
    
    process.on('SIGTERM', async () => {
        await app.shutdown();
        process.exit(0);
    });
    
    // Start the application
    app.run().catch(error => {
        console.error('Unhandled error:', error);
        process.exit(1);
    });
}

module.exports = Application;
EOF
}

__print_node_server() {
    local file="$1"
    local name="$2"
    
    cat > "$file" << EOF
// $name - Express server implementation
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const config = require('config');
const { createGreeting, formatMessage } = require('./utils');

/**
 * Server class for $name
 */
class Server {
    constructor(options = {}) {
        this.app = express();
        this.port = options.port || config.get('server.port') || 3000;
        this.host = options.host || config.get('server.host') || 'localhost';
        
        this.setupMiddleware();
        this.setupRoutes();
        this.setupErrorHandling();
    }

    /**
     * Setup middleware
     */
    setupMiddleware() {
        // Security middleware
        this.app.use(helmet());
        this.app.use(cors());
        
        // Body parsing
        this.app.use(express.json({ limit: '10mb' }));
        this.app.use(express.urlencoded({ extended: true }));
        
        // Request logging
        this.app.use((req, res, next) => {
            console.log(formatMessage('info', \`\${req.method} \${req.path}\`));
            next();
        });
    }

    /**
     * Setup routes
     */
    setupRoutes() {
        // Health check
        this.app.get('/health', (req, res) => {
            res.json({
                service: '$name',
                status: 'healthy',
                timestamp: new Date().toISOString(),
                uptime: process.uptime(),
                version: '1.0.0'
            });
        });

        // Root endpoint
        this.app.get('/', (req, res) => {
            res.json({
                message: createGreeting('API'),
                service: '$name',
                version: '1.0.0',
                endpoints: [
                    'GET /',
                    'GET /health',
                    'GET /greet/:name',
                    'POST /echo',
                    'GET /status'
                ]
            });
        });

        // Greeting endpoint
        this.app.get('/greet/:name', (req, res) => {
            const { name } = req.params;
            const greeting = createGreeting(name);
            
            res.json({
                greeting,
                timestamp: new Date().toISOString(),
                requestedName: name
            });
        });

        // Echo endpoint
        this.app.post('/echo', (req, res) => {
            res.json({
                echo: req.body,
                timestamp: new Date().toISOString(),
                headers: req.headers
            });
        });

        // Status endpoint
        this.app.get('/status', (req, res) => {
            res.json({
                service: '$name',
                status: 'running',
                environment: process.env.NODE_ENV || 'development',
                nodejs: process.version,
                memory: process.memoryUsage(),
                uptime: process.uptime(),
                timestamp: new Date().toISOString()
            });
        });
    }

    /**
     * Setup error handling
     */
    setupErrorHandling() {
        // 404 handler
        this.app.use((req, res) => {
            res.status(404).json({
                error: 'Not Found',
                message: \`Route \${req.method} \${req.path} not found\`,
                timestamp: new Date().toISOString()
            });
        });

        // Error handler
        this.app.use((error, req, res, next) => {
            console.error(formatMessage('error', \`Server error: \${error.message}\`));
            
            res.status(500).json({
                error: 'Internal Server Error',
                message: 'Something went wrong',
                timestamp: new Date().toISOString()
            });
        });
    }

    /**
     * Start the server
     */
    async start() {
        return new Promise((resolve, reject) => {
            this.server = this.app.listen(this.port, this.host, (error) => {
                if (error) {
                    reject(error);
                } else {
                    console.log(formatMessage('success', \`Server running at http://\${this.host}:\${this.port}\`));
                    resolve(this.server);
                }
            });
        });
    }

    /**
     * Stop the server
     */
    async stop() {
        if (this.server) {
            return new Promise((resolve) => {
                this.server.close(() => {
                    console.log(formatMessage('info', 'Server stopped'));
                    resolve();
                });
            });
        }
    }
}

// Run if called directly
if (require.main === module) {
    const server = new Server();
    
    // Handle graceful shutdown
    const shutdown = async () => {
        console.log('\\nShutting down server...');
        await server.stop();
        process.exit(0);
    };
    
    process.on('SIGINT', shutdown);
    process.on('SIGTERM', shutdown);
    
    // Start server
    server.start().catch(error => {
        console.error('Failed to start server:', error);
        process.exit(1);
    });
}

module.exports = Server;
EOF
}

__print_node_utils() {
    local file="$1"
    local name="$2"
    
    cat > "$file" << EOF
// $name - Utility functions
const _ = require('lodash');

/**
 * Create a greeting message
 * @param {string} name - Name to greet
 * @returns {string} Greeting message
 */
function createGreeting(name) {
    if (!name || typeof name !== 'string') {
        throw new Error('Name must be a non-empty string');
    }
    
    const capitalizedName = _.capitalize(name.trim());
    return \`Hello, \${capitalizedName}! Welcome to $name.\`;
}

/**
 * Format a log message with timestamp and level
 * @param {string} level - Log level (info, warn, error, success)
 * @param {string} message - Message to format
 * @returns {string} Formatted message
 */
function formatMessage(level, message) {
    const timestamp = new Date().toISOString();
    const levelUpper = level.toUpperCase().padEnd(7);
    
    // Add color codes for terminal output
    const colors = {
        info: '\\x1b[36m',    // Cyan
        warn: '\\x1b[33m',    // Yellow
        error: '\\x1b[31m',   // Red
        success: '\\x1b[32m', // Green
        reset: '\\x1b[0m'     // Reset
    };
    
    const color = colors[level] || colors.reset;
    const reset = colors.reset;
    
    return \`[\${timestamp}] \${color}\${levelUpper}\${reset} \${message}\`;
}

/**
 * Validate email address
 * @param {string} email - Email to validate
 * @returns {boolean} True if valid email
 */
function isValidEmail(email) {
    if (!email || typeof email !== 'string') {
        return false;
    }
    
    const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+\$/;
    return emailRegex.test(email);
}

/**
 * Deep merge objects
 * @param {Object} target - Target object
 * @param {...Object} sources - Source objects
 * @returns {Object} Merged object
 */
function deepMerge(target, ...sources) {
    return _.mergeWith(target, ...sources, (objValue, srcValue) => {
        if (_.isArray(objValue)) {
            return objValue.concat(srcValue);
        }
    });
}

/**
 * Generate a random ID
 * @param {number} length - Length of ID (default: 8)
 * @returns {string} Random ID
 */
function generateId(length = 8) {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    
    for (let i = 0; i < length; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    
    return result;
}

/**
 * Sleep for specified milliseconds
 * @param {number} ms - Milliseconds to sleep
 * @returns {Promise} Promise that resolves after delay
 */
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Retry a function with exponential backoff
 * @param {Function} fn - Function to retry
 * @param {number} maxRetries - Maximum retry attempts
 * @param {number} baseDelay - Base delay in milliseconds
 * @returns {Promise} Promise that resolves with function result
 */
async function retryWithBackoff(fn, maxRetries = 3, baseDelay = 1000) {
    let lastError;
    
    for (let attempt = 0; attempt <= maxRetries; attempt++) {
        try {
            return await fn();
        } catch (error) {
            lastError = error;
            
            if (attempt === maxRetries) {
                throw error;
            }
            
            const delay = baseDelay * Math.pow(2, attempt);
            console.log(formatMessage('warn', \`Retry attempt \${attempt + 1}/\${maxRetries} after \${delay}ms\`));
            await sleep(delay);
        }
    }
    
    throw lastError;
}

module.exports = {
    createGreeting,
    formatMessage,
    isValidEmail,
    deepMerge,
    generateId,
    sleep,
    retryWithBackoff
};
EOF
}
    

################################################################################
# Part 17: part_17_templates_python.sh
################################################################################

################################################################################
# Python Template Module
################################################################################

# Register this template with the core system
_register_template "python" "Python project with modern tooling" "py"

################################################################################
# Python Template Implementation
################################################################################

# Main creation function (standard interface)
_create_python_template() {
    local target_dir="$1"
    local project_name="$2"
    local package_name="${project_name//-/_}"  # Convert hyphens to underscores
    
    # Create Python project structure (src-layout)
    mkdir -p "$target_dir"/{src/$package_name,tests,docs}
    
    # Generate Python project files
    __print_pyproject_toml "$target_dir/pyproject.toml" "$project_name" "$package_name"
    __print_requirements_txt "$target_dir/requirements.txt"
    __print_requirements_dev_txt "$target_dir/requirements-dev.txt"
    __print_python_init "$target_dir/src/$package_name/__init__.py" "$project_name"
    __print_python_main "$target_dir/src/$package_name/main.py" "$project_name" "$package_name"
    __print_python_utils "$target_dir/src/$package_name/utils.py" "$package_name"
    __print_python_config "$target_dir/src/$package_name/config.py" "$package_name"
    __print_python_test_main "$target_dir/tests/test_main.py" "$package_name"
    __print_python_test_utils "$target_dir/tests/test_utils.py" "$package_name"
    __print_python_conftest "$target_dir/tests/conftest.py"
    __print_python_gitignore "$target_dir/.gitignore"
    __print_setup_cfg "$target_dir/setup.cfg"
    __print_python_version "$target_dir/.python-version"
    __print_makefile "$target_dir/Makefile" "$project_name"
    __print_readme_md "$target_dir/README.md" "$project_name" "Python"
    
    # Create empty __init__.py for tests
    touch "$target_dir/tests/__init__.py"
    
    trace "Created Python project structure in $target_dir"
    return 0
}

# Template preview function
_show_python_template() {
    cat << 'EOF'
Python project structure (src-layout):
  pyproject.toml      - Modern Python packaging configuration
  requirements.txt    - Production dependencies
  requirements-dev.txt - Development dependencies
  setup.cfg           - Tool configuration (flake8, pytest, etc.)
  Makefile           - Development automation
  .python-version    - Python version specification
  src/
    package/
      __init__.py     - Package initialization
      main.py         - Main application logic
      utils.py        - Utility functions
      config.py       - Configuration management
  tests/
    __init__.py       - Test package init
    conftest.py       - Pytest configuration
    test_main.py      - Main module tests
    test_utils.py     - Utils module tests
  .gitignore          - Python-specific ignore patterns
  README.md           - Project documentation

Features: Modern src-layout, pytest, type hints, dataclasses
EOF
}

################################################################################
# Python File Generators
################################################################################

__print_pyproject_toml() {
    local file="$1"
    local project_name="$2"
    local package_name="$3"
    
    cat > "$file" << EOF
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "$project_name"
version = "1.0.0"
description = "A sample Python project generated by GitSim"
authors = [
    {name = "$SIM_USER", email = "${SIM_USER}@example.com"}
]
maintainers = [
    {name = "$SIM_USER", email = "${SIM_USER}@example.com"}
]
readme = "README.md"
license = {text = "MIT"}
keywords = ["sample", "gitsim", "python"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
]
requires-python = ">=3.8"
dependencies = [
    "click>=8.0.0",
    "requests>=2.28.0",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "flake8>=6.0.0",
    "mypy>=1.0.0",
    "pre-commit>=3.0.0",
]
docs = [
    "sphinx>=6.0.0",
    "sphinx-rtd-theme>=1.2.0",
]

[project.urls]
Homepage = "https://github.com/${SIM_USER}/${project_name}"
Documentation = "https://github.com/${SIM_USER}/${project_name}/blob/main/README.md"
Repository = "https://github.com/${SIM_USER}/${project_name}.git"
"Bug Tracker" = "https://github.com/${SIM_USER}/${project_name}/issues"

[project.scripts]
$project_name = "${package_name}.main:main"

[tool.setuptools.packages.find]
where = ["src"]
include = ["${package_name}*"]
exclude = ["tests*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--verbose",
    "--cov=${package_name}",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-fail-under=80"
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests"
]

[tool.black]
line-length = 88
target-version = ["py38", "py39", "py310", "py311"]
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
line_length = 88
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[[tool.mypy.overrides]]
module = "tests.*"
ignore_errors = true
EOF
}

__print_requirements_txt() {
    local file="$1"
    
    cat > "$file" << 'EOF'
# Core dependencies
click>=8.0.0,<9.0.0
requests>=2.28.0,<3.0.0
pydantic>=2.0.0,<3.0.0
python-dotenv>=1.0.0,<2.0.0

# Optional: uncomment if needed
# pandas>=2.0.0,<3.0.0
# numpy>=1.24.0,<2.0.0
# sqlalchemy>=2.0.0,<3.0.0
# fastapi>=0.100.0,<1.0.0
EOF
}

__print_requirements_dev_txt() {
    local file="$1"
    
    cat > "$file" << 'EOF'
# Include production requirements
-r requirements.txt

# Development and testing
pytest>=7.0.0,<8.0.0
pytest-cov>=4.0.0,<5.0.0
pytest-mock>=3.10.0,<4.0.0
pytest-asyncio>=0.21.0,<1.0.0

# Code formatting and linting
black>=23.0.0,<24.0.0
isort>=5.12.0,<6.0.0
flake8>=6.0.0,<7.0.0
mypy>=1.0.0,<2.0.0

# Pre-commit hooks
pre-commit>=3.0.0,<4.0.0

# Documentation
sphinx>=6.0.0,<7.0.0
sphinx-rtd-theme>=1.2.0,<2.0.0

# Development utilities
ipython>=8.0.0,<9.0.0
jupyter>=1.0.0,<2.0.0
tox>=4.0.0,<5.0.0
EOF
}

__print_python_init() {
    local file="$1"
    local project_name="$2"
    
    cat > "$file" << EOF
"""
$project_name - A sample Python project generated by GitSim.

This package provides basic functionality for demonstration and testing purposes.
"""

__version__ = "1.0.0"
__author__ = "$SIM_USER"
__email__ = "${SIM_USER}@example.com"

# Import main functionality for easy access
from .main import main, Application, greet
from .utils import format_message, validate_email, timer
from .config import Config, get_config

__all__ = [
    "main",
    "Application", 
    "greet",
    "format_message",
    "validate_email",
    "timer",
    "Config",
    "get_config",
    "__version__",
    "__author__",
    "__email__",
]
EOF
}

__print_python_main() {
    local file="$1"
    local project_name="$2"
    local package_name="$3"
    
    cat > "$file" << EOF
"""
Main application module for $project_name.

This module contains the primary application logic and command-line interface.
"""

import sys
import asyncio
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from pathlib import Path

import click
from pydantic import BaseModel, validator

from .utils import format_message, validate_email, timer
from .config import get_config, Config


class UserModel(BaseModel):
    """User model with validation."""
    name: str
    email: str
    age: Optional[int] = None
    
    @validator('email')
    def validate_email_format(cls, v):
        if not validate_email(v):
            raise ValueError('Invalid email format')
        return v
    
    @validator('age')
    def validate_age_range(cls, v):
        if v is not None and (v < 0 or v > 150):
            raise ValueError('Age must be between 0 and 150')
        return v


@dataclass
class ApplicationState:
    """Application state management."""
    config: Config
    users: List[UserModel] = field(default_factory=list)
    status: str = "initialized"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        self.metadata.update({
            "version": "1.0.0",
            "author": "$SIM_USER",
            "created": "Generated by GitSim"
        })


class Application:
    """Main application class for $project_name."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the application."""
        self.config = get_config(config_path)
        self.state = ApplicationState(config=self.config)
        
    async def initialize(self) -> None:
        """Initialize the application asynchronously."""
        print(format_message("info", "Initializing $project_name..."))
        
        # Simulate async initialization
        await asyncio.sleep(0.1)
        
        self.state.status = "running"
        print(format_message("success", "Application initialized successfully"))
    
    def add_user(self, name: str, email: str, age: Optional[int] = None) -> UserModel:
        """Add a user to the application."""
        try:
            user = UserModel(name=name, email=email, age=age)
            self.state.users.append(user)
            print(format_message("info", f"Added user: {user.name}"))
            return user
        except Exception as e:
            print(format_message("error", f"Failed to add user: {e}"))
            raise
    
    def list_users(self) -> List[UserModel]:
        """List all users."""
        return self.state.users
    
    def get_status(self) -> Dict[str, Any]:
        """Get application status."""
        return {
            "status": self.state.status,
            "user_count": len(self.state.users),
            "config": self.config.model_dump(),
            "metadata": self.state.metadata
        }
    
    async def run_demo(self) -> None:
        """Run a demonstration of the application."""
        print(format_message("info", "Running $project_name demonstration"))
        
        # Add some sample users
        sample_users = [
            ("Alice Johnson", "alice@example.com", 30),
            ("Bob Smith", "bob@example.com", 25),
            ("Carol Williams", "carol@example.com", None),
        ]
        
        for name, email, age in sample_users:
            try:
                with timer(f"Adding user {name}"):
                    await asyncio.sleep(0.05)  # Simulate async work
                    self.add_user(name, email, age)
            except Exception as e:
                print(format_message("error", f"Failed to add {name}: {e}"))
        
        # Display results
        users = self.list_users()
        print(f"\nApplication now has {len(users)} users:")
        for user in users:
            age_str = f", age {user.age}" if user.age else ""
            print(f"  - {user.name} ({user.email}{age_str})")
        
        print(f"\nApplication status: {self.get_status()}")


def greet(name: str, count: int = 1) -> str:
    """Create a greeting message."""
    if not name:
        raise ValueError("Name cannot be empty")
    
    greetings = []
    for i in range(count):
        if count > 1:
            greetings.append(f"{i+1}: Hello, {name} from $project_name!")
        else:
            greetings.append(f"Hello, {name} from $project_name!")
    
    return "\n".join(greetings)


@click.group()
@click.version_option(version="1.0.0")
@click.option("--config", type=click.Path(exists=True), help="Configuration file path")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx, config, verbose):
    """$project_name - A sample Python application."""
    ctx.ensure_object(dict)
    ctx.obj['config_path'] = Path(config) if config else None
    ctx.obj['verbose'] = verbose


@cli.command()
@click.argument("name")
@click.option("--count", "-c", default=1, help="Number of greetings")
@click.pass_context
def hello(ctx, name, count):
    """Greet someone by name."""
    try:
        message = greet(name, count)
        print(message)
    except Exception as e:
        print(format_message("error", str(e)))
        sys.exit(1)


@cli.command()
@click.pass_context
def demo(ctx):
    """Run a demonstration of the application."""
    async def run_demo():
        app = Application(ctx.obj['config_path'])
        await app.initialize()
        await app.run_demo()
    
    try:
        asyncio.run(run_demo())
    except Exception as e:
        print(format_message("error", f"Demo failed: {e}"))
        sys.exit(1)


@cli.command()
@click.argument("name")
@click.argument("email") 
@click.option("--age", type=int, help="User age")
@click.pass_context
def add_user(ctx, name, email, age):
    """Add a user to the application."""
    try:
        app = Application(ctx.obj['config_path'])
        user = app.add_user(name, email, age)
        print(f"Added user: {user.model_dump_json(indent=2)}")
    except Exception as e:
        print(format_message("error", str(e)))
        sys.exit(1)


@cli.command()
@click.pass_context
def status(ctx):
    """Show application status."""
    try:
        app = Application(ctx.obj['config_path'])
        status_info = app.get_status()
        print(f"Status: {status_info}")
    except Exception as e:
        print(format_message("error", str(e)))
        sys.exit(1)


def main() -> None:
    """Main entry point for the application."""
    cli()


if __name__ == "__main__":
    main()
EOF
}

__print_python_utils() {
    local file="$1"
    local package_name="$2"
    
    cat > "$file" << EOF
"""
Utility functions for $package_name.

This module provides common utility functions used throughout the application.
"""

import re
import time
import json
from typing import Any, Dict, Optional, Union
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


def format_message(level: str, message: str) -> str:
    """
    Format a log message with timestamp and level.
    
    Args:
        level: Log level (info, warn, error, success, debug)
        message: Message to format
        
    Returns:
        Formatted message string
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    level_upper = level.upper().ljust(7)
    
    # Add color codes for terminal output
    colors = {
        'info': '\033[36m',     # Cyan
        'warn': '\033[33m',     # Yellow  
        'error': '\033[31m',    # Red
        'success': '\033[32m',  # Green
        'debug': '\033[90m',    # Dark gray
        'reset': '\033[0m'      # Reset
    }
    
    color = colors.get(level, colors['reset'])
    reset = colors['reset']
    
    return f"[{timestamp}] {color}{level_upper}{reset} {message}"


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email format is valid
    """
    if not email or not isinstance(email, str):
        return False
        
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def safe_json_loads(data: Union[str, bytes]) -> Optional[Dict[str, Any]]:
    """
    Safely parse JSON data with error handling.
    
    Args:
        data: JSON string or bytes to parse
        
    Returns:
        Parsed JSON data or None if parsing fails
    """
    try:
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        return json.loads(data)
    except (json.JSONDecodeError, UnicodeDecodeError, TypeError):
        return None


def safe_json_dumps(data: Any, indent: Optional[int] = None) -> Optional[str]:
    """
    Safely serialize data to JSON with error handling.
    
    Args:
        data: Data to serialize
        indent: JSON indentation level
        
    Returns:
        JSON string or None if serialization fails
    """
    try:
        return json.dumps(data, indent=indent, default=str)
    except (TypeError, ValueError):
        return None


def read_file_safe(file_path: Union[str, Path], encoding: str = 'utf-8') -> Optional[str]:
    """
    Safely read file content with error handling.
    
    Args:
        file_path: Path to file
        encoding: File encoding
        
    Returns:
        File content or None if reading fails
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return None
        return path.read_text(encoding=encoding)
    except (OSError, UnicodeDecodeError):
        return None


def write_file_safe(file_path: Union[str, Path], content: str, encoding: str = 'utf-8') -> bool:
    """
    Safely write content to file with error handling.
    
    Args:
        file_path: Path to file
        content: Content to write
        encoding: File encoding
        
    Returns:
        True if write succeeded
    """
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding=encoding)
        return True
    except OSError:
        return False


@contextmanager
def timer(operation: str = "Operation"):
    """
    Context manager to time operations.
    
    Args:
        operation: Description of the operation being timed
        
    Yields:
        None
    """
    start_time = time.time()
    try:
        print(format_message("debug", f"Starting {operation}..."))
        yield
    finally:
        end_time = time.time()
        duration = end_time - start_time
        print(format_message("debug", f"{operation} completed in {duration:.3f}s"))


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary (takes precedence)
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate string to maximum length with suffix.
    
    Args:
        text: String to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    
    if max_length <= len(suffix):
        return text[:max_length]
    
    return text[:max_length - len(suffix)] + suffix


class RetryError(Exception):
    """Exception raised when retry attempts are exhausted."""
    pass


def retry_with_backoff(
    func,
    max_retries: int = 3,
    base_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator to retry function with exponential backoff.
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds
        backoff_factor: Backoff multiplication factor
        exceptions: Tuple of exceptions to catch and retry
        
    Returns:
        Decorated function
    """
    def wrapper(*args, **kwargs):
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                last_exception = e
                
                if attempt == max_retries:
                    break
                
                delay = base_delay * (backoff_factor ** attempt)
                print(format_message("warn", f"Retry {attempt + 1}/{max_retries} after {delay:.1f}s"))
                time.sleep(delay)
        
        raise RetryError(f"Function failed after {max_retries} retries: {last_exception}")
    
    return wrapper
EOF
}

__print_python_config() {
    local file="$1"
    local package_name="$2"
    
    cat > "$file" << EOF
"""
Configuration management for $package_name.

This module handles application configuration loading and validation.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv

from .utils import read_file_safe, safe_json_loads


class DatabaseConfig(BaseModel):
    """Database configuration."""
    host: str = "localhost"
    port: int = Field(5432, ge=1, le=65535)
    database: str = "${package_name}_db"
    username: str = "user"
    password: str = "password"
    ssl_mode: str = Field("prefer", regex="^(disable|allow|prefer|require)$")
    pool_size: int = Field(10, ge=1, le=100)


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = Field("INFO", regex="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_bytes: int = Field(10485760, ge=1024)  # 10MB
    backup_count: int = Field(3, ge=0, le=10)


class Config(BaseModel):
    """Main application configuration."""
    
    # Application settings
    debug: bool = False
    testing: bool = False
    secret_key: str = "your-secret-key-here-change-in-production"
    
    # Server settings
    host: str = "localhost"
    port: int = Field(8000, ge=1, le=65535)
    workers: int = Field(4, ge=1, le=32)
    
    # Database configuration
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    
    # Logging configuration
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    
    # Feature flags
    enable_metrics: bool = True
    enable_health_check: bool = True
    enable_cors: bool = True
    
    # External service URLs
    api_base_url: str = "https://api.example.com"
    timeout_seconds: int = Field(30, ge=1, le=300)
    
    # File paths
    data_directory: str = "./data"
    temp_directory: str = "./tmp"
    
    @validator('secret_key')
    def secret_key_not_default(cls, v):
        """Ensure secret key is changed from default in production."""
        if not cls.__config__.debug and v == "your-secret-key-here-change-in-production":
            raise ValueError("Secret key must be changed in production")
        return v
    
    @validator('data_directory', 'temp_directory')
    def ensure_directory_exists(cls, v):
        """Ensure directories exist."""
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return str(path.resolve())
    
    class Config:
        """Pydantic configuration."""
        env_prefix = "${package_name}_"
        case_sensitive = False


def load_config_from_env() -> Dict[str, Any]:
    """
    Load configuration from environment variables.
    
    Returns:
        Dictionary of configuration values
    """
    # Load .env file if it exists
    env_path = Path('.env')
    if env_path.exists():
        load_dotenv(env_path)
    
    config_dict = {}
    prefix = f"${package_name}_".upper()
    
    for key, value in os.environ.items():
        if key.startswith(prefix):
            # Remove prefix and convert to lowercase
            config_key = key[len(prefix):].lower()
            
            # Handle nested configuration
            if '__' in config_key:
                parts = config_key.split('__')
                current = config_dict
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = value
            else:
                config_dict[config_key] = value
    
    return config_dict


def load_config_from_file(file_path: Path) -> Dict[str, Any]:
    """
    Load configuration from JSON file.
    
    Args:
        file_path: Path to configuration file
        
    Returns:
        Dictionary of configuration values
    """
    content = read_file_safe(file_path)
    if not content:
        return {}
    
    config_data = safe_json_loads(content)
    return config_data or {}


def get_config(config_path: Optional[Path] = None) -> Config:
    """
    Get application configuration.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        Configuration object
    """
    config_dict = {}
    
    # Load from file if provided
    if config_path and config_path.exists():
        file_config = load_config_from_file(config_path)
        config_dict.update(file_config)
    
    # Load from environment (takes precedence)
    env_config = load_config_from_env()
    config_dict.update(env_config)
    
    # Create and validate configuration
    try:
        return Config(**config_dict)
    except Exception as e:
        raise ValueError(f"Configuration validation failed: {e}")


def get_database_url(config: Config) -> str:
    """
    Generate database URL from configuration.
    
    Args:
        config: Configuration object
        
    Returns:
        Database connection URL
    """
    db = config.database
    return f"postgresql://{db.username}:{db.password}@{db.host}:{db.port}/{db.database}"


# Global configuration instance
_config: Optional[Config] = None


def get_global_config() -> Config:
    """
    Get global configuration instance.
    
    Returns:
        Global configuration object
    """
    global _config
    if _config is None:
        _config = get_config()
    return _config


def set_global_config(config: Config) -> None:
    """
    Set global configuration instance.
    
    Args:
        config: Configuration object to set
    """
    global _config
    _config = config
EOF
}

__print_python_test_main() {
    local file="$1"
    local package_name="$2"
    
    cat > "$file" << EOF
"""
Tests for main module.
"""

import pytest
from unittest.mock import patch, AsyncMock
from pydantic import ValidationError

from ${package_name}.main import (
    greet, 
    Application, 
    UserModel, 
    ApplicationState
)
from ${package_name}.config import Config


class TestUserModel:
    """Test UserModel validation."""
    
    def test_valid_user_creation(self):
        """Test creating a valid user."""
        user = UserModel(
            name="Alice Johnson",
            email="alice@example.com",
            age=30
        )
        assert user.name == "Alice Johnson"
        assert user.email == "alice@example.com"
        assert user.age == 30
    
    def test_user_without_age(self):
        """Test creating user without age."""
        user = UserModel(
            name="Bob Smith",
            email="bob@example.com"
        )
        assert user.name == "Bob Smith"
        assert user.email == "bob@example.com"
        assert user.age is None
    
    def test_invalid_email(self):
        """Test user creation with invalid email."""
        with pytest.raises(ValidationError, match="Invalid email format"):
            UserModel(
                name="Invalid User",
                email="not-an-email"
            )
    
    def test_invalid_age(self):
        """Test user creation with invalid age."""
        with pytest.raises(ValidationError, match="Age must be between 0 and 150"):
            UserModel(
                name="Old User",
                email="old@example.com",
                age=200
            )


class TestApplicationState:
    """Test ApplicationState dataclass."""
    
    def test_application_state_creation(self):
        """Test creating application state."""
        config = Config()
        state = ApplicationState(config=config)
        
        assert state.config == config
        assert state.users == []
        assert state.status == "initialized"
        assert "version" in state.metadata
        assert "author" in state.metadata


class TestGreetFunction:
    """Test greet function."""
    
    def test_single_greeting(self):
        """Test single greeting."""
        result = greet("Alice")
        expected = "Hello, Alice from ${package_name}!"
        assert result == expected
    
    def test_multiple_greetings(self):
        """Test multiple greetings."""
        result = greet("Bob", count=3)
        lines = result.split("\\n")
        assert len(lines) == 3
        assert lines[0] == "1: Hello, Bob from ${package_name}!"
        assert lines[1] == "2: Hello, Bob from ${package_name}!"
        assert lines[2] == "3: Hello, Bob from ${package_name}!"
    
    def test_empty_name_raises_error(self):
        """Test that empty name raises error."""
        with pytest.raises(ValueError, match="Name cannot be empty"):
            greet("")


class TestApplication:
    """Test Application class."""
    
    def test_application_initialization(self):
        """Test application initialization."""
        app = Application()
        assert app.config is not None
        assert app.state.status == "initialized"
        assert len(app.state.users) == 0
    
    @pytest.mark.asyncio
    async def test_application_async_initialization(self):
        """Test application async initialization."""
        app = Application()
        await app.initialize()
        assert app.state.status == "running"
    
    def test_add_valid_user(self):
        """Test adding a valid user."""
        app = Application()
        user = app.add_user("Alice", "alice@example.com", 25)
        
        assert len(app.state.users) == 1
        assert user.name == "Alice"
        assert user.email == "alice@example.com"
        assert user.age == 25
    
    def test_add_user_invalid_email(self):
        """Test adding user with invalid email raises error."""
        app = Application()
        with pytest.raises(ValidationError):
            app.add_user("Invalid", "not-email", 25)
    
    def test_list_users(self):
        """Test listing users."""
        app = Application()
        app.add_user("Alice", "alice@example.com")
        app.add_user("Bob", "bob@example.com")
        
        users = app.list_users()
        assert len(users) == 2
        assert users[0].name == "Alice"
        assert users[1].name == "Bob"
    
    def test_get_status(self):
        """Test getting application status."""
        app = Application()
        app.add_user("Alice", "alice@example.com")
        
        status = app.get_status()
        assert status["status"] == "initialized"
        assert status["user_count"] == 1
        assert "config" in status
        assert "metadata" in status
    
    @pytest.mark.asyncio
    async def test_run_demo(self):
        """Test running demo."""
        app = Application()
        await app.initialize()
        
        with patch('builtins.print') as mock_print:
            await app.run_demo()
        
        # Verify users were added
        users = app.list_users()
        assert len(users) == 3
        
        # Verify print was called
        assert mock_print.called


@pytest.mark.integration
class TestIntegration:
    """Integration tests."""
    
    @pytest.mark.asyncio
    async def test_full_application_workflow(self):
        """Test complete application workflow."""
        # Initialize application
        app = Application()
        await app.initialize()
        
        # Add users
        user1 = app.add_user("Alice", "alice@example.com", 30)
        user2 = app.add_user("Bob", "bob@example.com")
        
        # Verify state
        assert len(app.list_users()) == 2
        assert app.state.status == "running"
        
        # Get status
        status = app.get_status()
        assert status["user_count"] == 2
        assert status["status"] == "running"
        
        # Run demo (adds more users)
        await app.run_demo()
        
        # Verify final state
        final_users = app.list_users()
        assert len(final_users) == 5  # 2 + 3 from demo


# Fixtures for testing
@pytest.fixture
def sample_config():
    """Provide a sample configuration."""
    return Config(debug=True, testing=True)


@pytest.fixture
def sample_application(sample_config):
    """Provide a sample application instance."""
    app = Application()
    app.config = sample_config
    return app


@pytest.fixture
def sample_users():
    """Provide sample user data."""
    return [
        ("Alice Johnson", "alice@example.com", 30),
        ("Bob Smith", "bob@example.com", 25),
        ("Carol Williams", "carol@example.com", None),
    ]


# Parameterized tests
@pytest.mark.parametrize("name,email,age,should_succeed", [
    ("Alice", "alice@example.com", 25, True),
    ("Bob", "bob@example.com", None, True),
    ("Carol", "invalid-email", 30, False),
    ("Dave", "dave@example.com", -5, False),
    ("Eve", "eve@example.com", 200, False),
])
def test_user_creation_parametrized(name, email, age, should_succeed):
    """Test user creation with various inputs."""
    if should_succeed:
        user = UserModel(name=name, email=email, age=age)
        assert user.name == name
        assert user.email == email
        assert user.age == age
    else:
        with pytest.raises(ValidationError):
            UserModel(name=name, email=email, age=age)
EOF
}

__print_python_test_utils() {
    local file="$1"
    local package_name="$2"
    
    cat > "$file" << EOF
"""
Tests for utils module.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

from ${package_name}.utils import (
    format_message,
    validate_email,
    safe_json_loads,
    safe_json_dumps,
    read_file_safe,
    write_file_safe,
    timer,
    deep_merge_dicts,
    truncate_string,
    retry_with_backoff,
    RetryError
)


class TestFormatMessage:
    """Test message formatting function."""
    
    def test_format_message_info(self):
        """Test formatting info message."""
        result = format_message("info", "Test message")
        assert "INFO" in result
        assert "Test message" in result
        assert result.startswith("[")
    
    def test_format_message_error(self):
        """Test formatting error message."""
        result = format_message("error", "Error occurred")
        assert "ERROR" in result
        assert "Error occurred" in result
    
    def test_format_message_with_colors(self):
        """Test that format includes color codes."""
        result = format_message("success", "Success!")
        # Should contain ANSI color codes
        assert "\\033[" in result
        assert "SUCCESS" in result


class TestValidateEmail:
    """Test email validation function."""
    
    @pytest.mark.parametrize("email,expected", [
        ("user@example.com", True),
        ("test.email@domain.co.uk", True),
        ("user+tag@example.com", True),
        ("user123@test-domain.com", True),
        ("invalid", False),
        ("user@", False),
        ("@example.com", False),
        ("user@.com", False),
        ("user@com", False),
        ("", False),
        (None, False),
        (123, False),
    ])
    def test_validate_email_cases(self, email, expected):
        """Test email validation with various cases."""
        assert validate_email(email) == expected


class TestSafeJsonOperations:
    """Test safe JSON operations."""
    
    def test_safe_json_loads_valid(self):
        """Test loading valid JSON."""
        data = '{"key": "value", "number": 42}'
        result = safe_json_loads(data)
        assert result == {"key": "value", "number": 42}
    
    def test_safe_json_loads_invalid(self):
        """Test loading invalid JSON."""
        data = '{"key": "value"'  # Missing closing brace
        result = safe_json_loads(data)
        assert result is None
    
    def test_safe_json_loads_bytes(self):
        """Test loading JSON from bytes."""
        data = b'{"key": "value"}'
        result = safe_json_loads(data)
        assert result == {"key": "value"}
    
    def test_safe_json_dumps_valid(self):
        """Test dumping valid data."""
        data = {"key": "value", "number": 42}
        result = safe_json_dumps(data)
        parsed = json.loads(result)
        assert parsed == data
    
    def test_safe_json_dumps_with_indent(self):
        """Test dumping with indentation."""
        data = {"key": "value"}
        result = safe_json_dumps(data, indent=2)
        assert "\\n" in result
        assert "  " in result
    
    def test_safe_json_dumps_invalid(self):
        """Test dumping invalid data."""
        # Object that can't be JSON serialized
        class NonSerializable:
            pass
        
        data = {"obj": NonSerializable()}
        result = safe_json_dumps(data)
        # Should not be None because we use default=str
        assert result is not None


class TestFileOperations:
    """Test file operation utilities."""
    
    def test_read_file_safe_existing(self):
        """Test reading existing file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            f.flush()
            
            result = read_file_safe(f.name)
            assert result == "test content"
            
            # Cleanup
            Path(f.name).unlink()
    
    def test_read_file_safe_nonexistent(self):
        """Test reading non-existent file."""
        result = read_file_safe("/nonexistent/file.txt")
        assert result is None
    
    def test_write_file_safe_success(self):
        """Test successful file writing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.txt"
            result = write_file_safe(file_path, "test content")
            assert result is True
            assert file_path.read_text() == "test content"
    
    def test_write_file_safe_creates_directory(self):
        """Test that write_file_safe creates directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "subdir" / "test.txt"
            result = write_file_safe(file_path, "test content")
            assert result is True
            assert file_path.exists()
            assert file_path.read_text() == "test content"


class TestTimer:
    """Test timer context manager."""
    
    def test_timer_context_manager(self):
        """Test timer context manager."""
        with patch('builtins.print') as mock_print:
            with timer("Test operation"):
                pass  # Do nothing
        
        # Should have printed start and end messages
        assert mock_print.call_count >= 2
        calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("Starting Test operation" in call for call in calls)
        assert any("Test operation completed" in call for call in calls)


class TestDeepMergeDicts:
    """Test deep dictionary merging."""
    
    def test_simple_merge(self):
        """Test simple dictionary merge."""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"c": 3, "d": 4}
        result = deep_merge_dicts(dict1, dict2)
        assert result == {"a": 1, "b": 2, "c": 3, "d": 4}
    
    def test_nested_merge(self):
        """Test nested dictionary merge."""
        dict1 = {"a": {"x": 1, "y": 2}, "b": 3}
        dict2 = {"a": {"z": 4}, "c": 5}
        result = deep_merge_dicts(dict1, dict2)
        expected = {"a": {"x": 1, "y": 2, "z": 4}, "b": 3, "c": 5}
        assert result == expected
    
    def test_overwrite_merge(self):
        """Test that dict2 values overwrite dict1."""
        dict1 = {"a": 1, "b": {"x": 10}}
        dict2 = {"a": 2, "b": {"x": 20, "y": 30}}
        result = deep_merge_dicts(dict1, dict2)
        expected = {"a": 2, "b": {"x": 20, "y": 30}}
        assert result == expected


class TestTruncateString:
    """Test string truncation utility."""
    
    def test_no_truncation_needed(self):
        """Test string that doesn't need truncation."""
        result = truncate_string("short", 10)
        assert result == "short"
    
    def test_truncation_with_default_suffix(self):
        """Test truncation with default suffix."""
        result = truncate_string("this is a long string", 10)
        assert result == "this is..."
        assert len(result) == 10
    
    def test_truncation_with_custom_suffix(self):
        """Test truncation with custom suffix."""
        result = truncate_string("long string", 8, suffix=">>")
        assert result == "long s>>"
        assert len(result) == 8
    
    def test_truncation_suffix_longer_than_max(self):
        """Test when suffix is longer than max length."""
        result = truncate_string("text", 2, suffix="...")
        assert result == "te"
        assert len(result) == 2


class TestRetryWithBackoff:
    """Test retry decorator."""
    
    def test_retry_success_on_first_try(self):
        """Test function that succeeds on first try."""
        @retry_with_backoff(max_retries=3)
        def successful_func():
            return "success"
        
        result = successful_func()
        assert result == "success"
    
    def test_retry_success_after_failures(self):
        """Test function that succeeds after some failures."""
        call_count = 0
        
        @retry_with_backoff(max_retries=3, base_delay=0.01)  # Fast for testing
        def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"
        
        with patch('time.sleep'):  # Mock sleep for faster tests
            result = flaky_func()
        
        assert result == "success"
        assert call_count == 3
    
    def test_retry_exhausted(self):
        """Test function that fails all retry attempts."""
        @retry_with_backoff(max_retries=2, base_delay=0.01)
        def failing_func():
            raise ValueError("Always fails")
        
        with patch('time.sleep'):
            with pytest.raises(RetryError, match="Function failed after 2 retries"):
                failing_func()
    
    def test_retry_specific_exceptions(self):
        """Test retrying only specific exceptions."""
        @retry_with_backoff(max_retries=2, exceptions=(ValueError,))
        def mixed_exception_func():
            raise TypeError("Should not be retried")
        
        # Should not retry TypeError, should fail immediately
        with pytest.raises(TypeError):
            mixed_exception_func()


# Performance and edge case tests
class TestUtilsPerformance:
    """Test utils performance and edge cases."""
    
    def test_large_json_handling(self):
        """Test handling of large JSON data."""
        large_data = {"key_" + str(i): "value_" + str(i) for i in range(1000)}
        
        # Should handle large data without issues
        json_str = safe_json_dumps(large_data)
        assert json_str is not None
        
        parsed = safe_json_loads(json_str)
        assert parsed == large_data
    
    def test_deep_nested_dict_merge(self):
        """Test deep nested dictionary merging."""
        dict1 = {"a": {"b": {"c": {"d": 1}}}}
        dict2 = {"a": {"b": {"c": {"e": 2}}}}
        
        result = deep_merge_dicts(dict1, dict2)
        expected = {"a": {"b": {"c": {"d": 1, "e": 2}}}}
        assert result == expected
    
    @pytest.mark.parametrize("text,max_len,expected_len", [
        ("", 10, 0),
        ("a", 10, 1),
        ("exactly_ten", 10, 10),
        ("more_than_ten_characters", 10, 10),
        ("x" * 100, 20, 20),
    ])
    def test_truncate_various_lengths(self, text, max_len, expected_len):
        """Test truncation with various lengths."""
        result = truncate_string(text, max_len)
        assert len(result) == expected_len
EOF
}

__print_python_conftest() {
    local file="$1"
    
    cat > "$file" << EOF
"""
Pytest configuration and fixtures.
"""

import pytest
import asyncio
from pathlib import Path
from typing import Generator

from ${package_name//-/_}.config import Config


# Configure pytest-asyncio
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_config() -> Config:
    """Provide a test configuration."""
    return Config(
        debug=True,
        testing=True,
        secret_key="test-secret-key",
        database={
            "host": "localhost",
            "port": 5432,
            "database": "test_db",
            "username": "test_user",
            "password": "test_password"
        },
        logging={
            "level": "DEBUG",
            "file_path": None  # No file logging in tests
        }
    )


@pytest.fixture
def temp_directory(tmp_path) -> Path:
    """Provide a temporary directory for tests."""
    return tmp_path


@pytest.fixture
def sample_json_data():
    """Provide sample JSON data for testing."""
    return {
        "string_field": "test_value",
        "number_field": 42,
        "boolean_field": True,
        "null_field": None,
        "array_field": [1, 2, 3, "four"],
        "object_field": {
            "nested_string": "nested_value",
            "nested_number": 3.14
        }
    }


@pytest.fixture
def sample_users_data():
    """Provide sample user data for testing."""
    return [
        {
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "age": 30
        },
        {
            "name": "Bob Smith", 
            "email": "bob@example.com",
            "age": 25
        },
        {
            "name": "Carol Williams",
            "email": "carol@example.com",
            "age": None
        }
    ]


# Pytest markers
pytest_markers = [
    "unit: marks tests as unit tests",
    "integration: marks tests as integration tests", 
    "slow: marks tests as slow running tests",
    "async: marks tests that use async/await"
]


# Test configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    for marker in pytest_markers:
        config.addinivalue_line("markers", marker)


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Mark async tests
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.async)
        
        # Mark slow tests based on name
        if "slow" in item.name or "performance" in item.name:
            item.add_marker(pytest.mark.slow)
        
        # Mark integration tests
        if "integration" in item.name or "Integration" in item.cls.__name__ if item.cls else False:
            item.add_marker(pytest.mark.integration)
        else:
            item.add_marker(pytest.mark.unit)
EOF
}

__print_python_gitignore() {
    local file="$1"
    
    cat > "$file" << 'EOF'
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Translations
*.mo
*.pot

# Django stuff
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff
instance/
.webassets-cache

# Scrapy stuff
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
Pipfile.lock

# poetry
poetry.lock

# pdm
.pdm.toml

# PEP 582
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/

# PyCharm
.idea/
EOF
    
    # Add common patterns
    __print_common_gitignore "$file"
}

__print_setup_cfg() {
    local file="$1"
    
    cat > "$file" << 'EOF'
[metadata]
name = attr: src.package.__name__
version = attr: src.package.__version__
author = attr: src.package.__author__
author_email = attr: src.package.__email__

[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = 
    .git,
    __pycache__,
    build,
    dist,
    .eggs,
    *.egg-info,
    .venv,
    venv,
    .pytest_cache

[isort]
profile = black
multi_line_output = 3
line_length = 88
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true

[mypy]
python_version = 3.8
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true

[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --verbose
EOF
}

__print_python_version() {
    local file="$1"
    
    cat > "$file" << 'EOF'
3.11.0
EOF
}

__print_makefile() {
    local file="$1"
    local project_name="$2"
    
    cat > "$file" << EOF
# Makefile for $project_name

.PHONY: help install install-dev test test-cov lint format clean build docs

# Default target
help:
	@echo "Available targets:"
	@echo "  install     - Install production dependencies"
	@echo "  install-dev - Install development dependencies"
	@echo "  test        - Run tests"
	@echo "  test-cov    - Run tests with coverage"
	@echo "  lint        - Run linting (flake8, mypy)"
	@echo "  format      - Format code (black, isort)"
	@echo "  clean       - Clean build artifacts"
	@echo "  build       - Build package"
	@echo "  docs        - Generate documentation"

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt
	pip install -e .

# Testing
test:
	pytest

test-cov:
	pytest --cov=${project_name//-/_} --cov-report=html --cov-report=term

test-fast:
	pytest -x -v

# Linting and formatting
lint:
	flake8 src/ tests/
	mypy src/

format:
	black src/ tests/
	isort src/ tests/

format-check:
	black --check src/ tests/
	isort --check-only src/ tests/

# Cleaning
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# Building
build:
	python -m build

build-wheel:
	python -m build --wheel

# Documentation
docs:
	@echo "Documentation generation not configured yet"

# Development workflow
dev-setup: install-dev
	pre-commit install

dev-test: format lint test

dev-clean: clean
	rm -rf .venv/

# CI targets
ci-test: install-dev format-check lint test-cov

# Run the application
run:
	python -m ${project_name//-/_}

# Development server (if applicable)
dev:
	python -m ${project_name//-/_}
EOF
}
            

################################################################################
# Part 18: part_18_templates_testsh.sh
################################################################################

################################################################################
# TESTSH Template Module
################################################################################

# Register this template with the core system
_register_template "testsh" "TESTSH-compliant comprehensive test suite" "testsh test-suite testing"

################################################################################
# TESTSH Template Implementation
################################################################################

# Main creation function (standard interface)
_create_testsh_template() {
    local target_dir="$1"
    local project_name="$2"

    # Create TESTSH project structure
    mkdir -p "$target_dir"
    mkdir -p "$target_dir"/{tests/{unit,sanity,smoke,integration,e2e,uat,chaos,bench,_adhoc},scripts}

    # Generate TESTSH project files
    __print_testsh_bootstrap_script "$target_dir/scripts/bootstrap-tests.sh" "$project_name"
    __print_testsh_main_runner "$target_dir/testsim.sh" "$project_name"
    __print_testsh_wrappers "$target_dir" "$project_name"
    __print_testsh_examples "$target_dir" "$project_name"
    __print_testsh_gitignore "$target_dir/.gitignore"
    __print_readme_md "$target_dir/README.md" "$project_name" "TESTSH"

    # Make scripts executable
    chmod +x "$target_dir/scripts/bootstrap-tests.sh"
    chmod +x "$target_dir/testsim.sh"
    chmod +x "$target_dir/tests/_adhoc"/*.sh 2>/dev/null || true

    trace "Created TESTSH project structure in $target_dir"
    return 0
}

# Template preview function
_show_testsh_template() {
    cat << 'EOF'
TESTSH project structure:
  testsim.sh                 - Main test runner with category support
  scripts/
    bootstrap-tests.sh    - Test structure generator
  tests/
    unit/                 - Unit test modules
    sanity/               - Sanity check tests
    smoke/                - Smoke test suite
    integration/          - Integration tests
    e2e/                  - End-to-end tests
    uat/                  - User acceptance tests
    chaos/                - Chaos engineering tests
    bench/                - Benchmark tests
    _adhoc/               - Ad-hoc test scripts
  README.md               - Test documentation

Features: Full TESTSH compliance, hierarchical test organization, multi-language support
EOF
}

################################################################################
# TESTSH File Generators
################################################################################

__print_testsh_bootstrap_script() {
    local file="$1"
    local name="$2"

    cat > "$file" << EOF
#!/usr/bin/env bash
# scripts/bootstrap-tests.sh - TESTSH Structure Generator
# Run from project root to initialize comprehensive test structure

set -euo pipefail

# Colors for output
readonly GREEN=\$'\\033[32m'
readonly BLUE=\$'\\033[34m'
readonly RESET=\$'\\033[0m'

info() { printf "%s[INFO]%s %s\\n" "\$BLUE" "\$RESET" "\$*"; }
okay() { printf "%s[OK]%s %s\\n" "\$GREEN" "\$RESET" "\$*"; }

cat_wrapper() {
    local name="\$1"; shift
    local lang="\${1:-rs}"

    case "\$lang" in
        rs|rust)
            cat > "tests/\${name}.rs" <<RUST_EOF
// Wrapper: \${name}.rs
fn main() {
    println!("placeholder for \${name}");
}
RUST_EOF
            ;;
        sh|bash)
            cat > "tests/\${name}.sh" <<BASH_EOF
#!/usr/bin/env bash
# Wrapper: \${name}.sh
echo "placeholder for \${name}"
BASH_EOF
            chmod +x "tests/\${name}.sh"
            ;;
        js|node)
            cat > "tests/\${name}.js" <<JS_EOF
// Wrapper: \${name}.js
console.log('placeholder for \${name}');
JS_EOF
            ;;
        py|python)
            cat > "tests/\${name}.py" <<PY_EOF
#!/usr/bin/env python3
# Wrapper: \${name}.py
print('placeholder for \${name}')
PY_EOF
            chmod +x "tests/\${name}.py"
            ;;
        *)
            cat > "tests/\${name}.txt" <<TXT_EOF
Placeholder for \${name}
TXT_EOF
            ;;
    esac
}

# Detect project language and set defaults
detect_language() {
    if [[ -f "Cargo.toml" ]]; then
        echo "rust"
    elif [[ -f "package.json" ]]; then
        echo "node"
    elif [[ -f "*.py" ]] || [[ -f "setup.py" ]] || [[ -f "requirements.txt" ]]; then
        echo "python"
    elif [[ -f "*.sh" ]] || [[ -f "build.sh" ]]; then
        echo "bash"
    else
        echo "generic"
    fi
}

main() {
    local lang="\${1:-\$(detect_language)}"

    info "Bootstrapping TESTSH structure for language: \$lang"

    # Ensure test directories exist
    mkdir -p tests/{unit,sanity,smoke,integration,e2e,uat,chaos,bench,_adhoc}

    # Create top-level wrappers
    info "Creating top-level test wrappers..."
    cat_wrapper "sanity" "\$lang"
    cat_wrapper "smoke" "\$lang"
    cat_wrapper "unit" "\$lang"
    cat_wrapper "integration" "\$lang"
    cat_wrapper "e2e" "\$lang"
    cat_wrapper "uat" "\$lang"
    cat_wrapper "chaos" "\$lang"
    cat_wrapper "bench" "\$lang"

    # Create category module examples
    info "Creating category examples..."
    case "\$lang" in
        rust)
            cat > tests/sanity/example.rs <<'RUST_EOF'
// sanity/example.rs
#[test]
fn sanity_example() {
    assert!(true);
}
RUST_EOF

            cat > tests/uat/example.rs <<'RUST_EOF'
// uat/example.rs
#[test]
fn uat_example() {
    assert!(true);
}
RUST_EOF
            ;;
        bash)
            cat > tests/sanity/example.sh <<'BASH_EOF'
#!/usr/bin/env bash
# sanity/example.sh
test_sanity_example() {
    return 0  # Pass
}
BASH_EOF
            chmod +x tests/sanity/example.sh

            cat > tests/uat/example.sh <<'BASH_EOF'
#!/usr/bin/env bash
# uat/example.sh
test_uat_example() {
    return 0  # Pass
}
BASH_EOF
            chmod +x tests/uat/example.sh
            ;;
        node)
            cat > tests/sanity/example.js <<'JS_EOF'
// sanity/example.js
describe('Sanity Tests', () => {
    it('should pass basic sanity check', () => {
        expect(true).toBe(true);
    });
});
JS_EOF

            cat > tests/uat/example.js <<'JS_EOF'
// uat/example.js
describe('UAT Tests', () => {
    it('should pass basic UAT check', () => {
        expect(true).toBe(true);
    });
});
JS_EOF
            ;;
        python)
            cat > tests/sanity/example.py <<'PY_EOF'
#!/usr/bin/env python3
# sanity/example.py
import unittest

class SanityTests(unittest.TestCase):
    def test_sanity_example(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
PY_EOF
            chmod +x tests/sanity/example.py

            cat > tests/uat/example.py <<'PY_EOF'
#!/usr/bin/env python3
# uat/example.py
import unittest

class UATTests(unittest.TestCase):
    def test_uat_example(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
PY_EOF
            chmod +x tests/uat/example.py
            ;;
    esac

    # Create adhoc skeleton
    info "Creating adhoc test skeleton..."
    cat > tests/_adhoc/demo.sh <<'ADHOC_EOF'
#!/usr/bin/env bash
# _adhoc/demo.sh - Example adhoc test
echo "adhoc demo test"
exit 0
ADHOC_EOF
    chmod +x tests/_adhoc/demo.sh

    okay "TESTSH structure bootstrapped successfully"
    info "Run '../testsim.sh list' to see available test categories"
}

main "\$@"
EOF
}

__print_testsh_main_runner() {
    local file="$1"
    local name="$2"

    cat > "$file" << EOF
#!/usr/bin/env bash
# testsim.sh - TESTSH-Compliant Test Runner for $name
#
# Supports hierarchical test execution across multiple categories
# Compatible with GitSim TESTSH architecture

set -e

# Configuration
readonly SCRIPT_NAME="testsim.sh"
readonly SCRIPT_VERSION="1.0.0"
readonly PROJECT_NAME="$name"

# Colors for output
readonly RED=\$'\\033[31m'
readonly GREEN=\$'\\033[32m'
readonly YELLOW=\$'\\033[33m'
readonly BLUE=\$'\\033[34m'
readonly RESET=\$'\\033[0m'

# Test categories in execution order
readonly TEST_CATEGORIES=(
    "sanity"
    "smoke"
    "unit"
    "integration"
    "e2e"
    "uat"
    "chaos"
    "bench"
)

# Logging functions
info() { printf "%s[INFO]%s %s\\n" "\$BLUE" "\$RESET" "\$*" >&2; }
okay() { printf "%s[OK]%s %s\\n" "\$GREEN" "\$RESET" "\$*" >&2; }
warn() { printf "%s[WARN]%s %s\\n" "\$YELLOW" "\$RESET" "\$*" >&2; }
error() { printf "%s[ERROR]%s %s\\n" "\$RED" "\$RESET" "\$*" >&2; }

# Test execution functions
run_category_tests() {
    local category="\$1"
    local test_dir="tests/\$category"
    local wrapper_file="tests/\$category"
    local tests_found=0
    local tests_passed=0

    info "Running \$category tests..."

    # Check for wrapper files (multiple extensions)
    local wrapper_found=false
    for ext in rs sh js py; do
        if [[ -f "\$wrapper_file.\$ext" ]]; then
            info "Executing wrapper: \$wrapper_file.\$ext"
            case "\$ext" in
                rs)
                    if command -v rustc >/dev/null; then
                        rustc "\$wrapper_file.\$ext" -o "/tmp/\$category" && "/tmp/\$category"
                        (( tests_found++ ))
                        [[ \$? -eq 0 ]] && (( tests_passed++ ))
                    else
                        warn "Rust compiler not found, skipping \$wrapper_file.\$ext"
                    fi
                    ;;
                sh)
                    bash "\$wrapper_file.\$ext"
                    (( tests_found++ ))
                    [[ \$? -eq 0 ]] && (( tests_passed++ ))
                    ;;
                js)
                    if command -v node >/dev/null; then
                        node "\$wrapper_file.\$ext"
                        (( tests_found++ ))
                        [[ \$? -eq 0 ]] && (( tests_passed++ ))
                    else
                        warn "Node.js not found, skipping \$wrapper_file.\$ext"
                    fi
                    ;;
                py)
                    if command -v python3 >/dev/null; then
                        python3 "\$wrapper_file.\$ext"
                        (( tests_found++ ))
                        [[ \$? -eq 0 ]] && (( tests_passed++ ))
                    else
                        warn "Python3 not found, skipping \$wrapper_file.\$ext"
                    fi
                    ;;
            esac
            wrapper_found=true
        fi
    done

    # Run individual test files in category directory
    if [[ -d "\$test_dir" ]]; then
        for test_file in "\$test_dir"/*; do
            [[ -f "\$test_file" ]] || continue
            [[ -x "\$test_file" ]] || continue

            info "Executing: \$(basename "\$test_file")"
            if "\$test_file"; then
                (( tests_passed++ ))
            fi
            (( tests_found++ ))
        done
    fi

    if [[ \$tests_found -eq 0 ]]; then
        warn "No tests found for category: \$category"
    else
        okay "\$category: \$tests_passed/\$tests_found tests passed"
    fi

    return \$(( tests_found - tests_passed ))
}

run_adhoc_tests() {
    local adhoc_dir="tests/_adhoc"
    local tests_found=0
    local tests_passed=0

    info "Running adhoc tests..."

    if [[ -d "\$adhoc_dir" ]]; then
        for test_file in "\$adhoc_dir"/*; do
            [[ -f "\$test_file" ]] || continue
            [[ -x "\$test_file" ]] || continue

            info "Executing adhoc: \$(basename "\$test_file")"
            if "\$test_file"; then
                (( tests_passed++ ))
            fi
            (( tests_found++ ))
        done
    fi

    if [[ \$tests_found -eq 0 ]]; then
        warn "No adhoc tests found"
    else
        okay "adhoc: \$tests_passed/\$tests_found tests passed"
    fi

    return \$(( tests_found - tests_passed ))
}

# Command implementations
cmd_list() {
    info "Available test categories:"
    for category in "\${TEST_CATEGORIES[@]}"; do
        local count=0
        local wrapper_exists=false

        # Check for wrapper files
        for ext in rs sh js py; do
            [[ -f "tests/\$category.\$ext" ]] && wrapper_exists=true
        done

        # Count individual test files
        if [[ -d "tests/\$category" ]]; then
            count=\$(find "tests/\$category" -type f -executable | wc -l)
        fi

        printf "  %-12s" "\$category"
        [[ "\$wrapper_exists" == true ]] && printf "[wrapper] "
        printf "(%d files)\\n" "\$count"
    done

    # Count adhoc tests
    local adhoc_count=0
    if [[ -d "tests/_adhoc" ]]; then
        adhoc_count=\$(find "tests/_adhoc" -type f -executable | wc -l)
    fi
    printf "  %-12s(%d files)\\n" "_adhoc" "\$adhoc_count"
}

cmd_run() {
    local category="\$1"

    if [[ -z "\$category" ]]; then
        # Run all categories
        local total_failures=0

        info "Running all test categories for \$PROJECT_NAME"

        for cat in "\${TEST_CATEGORIES[@]}"; do
            run_category_tests "\$cat" || (( total_failures++ ))
        done

        # Run adhoc tests
        run_adhoc_tests || (( total_failures++ ))

        if [[ \$total_failures -eq 0 ]]; then
            okay "All test categories passed!"
        else
            error "\$total_failures test categories had failures"
            return 1
        fi
    else
        # Run specific category
        if [[ " \${TEST_CATEGORIES[*]} " =~ " \$category " ]]; then
            run_category_tests "\$category"
        elif [[ "\$category" == "adhoc" ]]; then
            run_adhoc_tests
        else
            error "Unknown test category: \$category"
            info "Available categories: \${TEST_CATEGORIES[*]} adhoc"
            return 1
        fi
    fi
}

cmd_bootstrap() {
    local lang="\${1:-auto}"

    if [[ -f "scripts/bootstrap-tests.sh" ]]; then
        info "Running test structure bootstrap..."
        bash scripts/bootstrap-tests.sh "\$lang"
    else
        error "Bootstrap script not found: scripts/bootstrap-tests.sh"
        return 1
    fi
}

cmd_clean() {
    info "Cleaning test artifacts..."

    # Remove temporary files
    find tests/ -name "*.tmp" -delete 2>/dev/null || true
    rm -f /tmp/sanity /tmp/smoke /tmp/unit /tmp/integration /tmp/e2e /tmp/uat /tmp/chaos /tmp/bench

    okay "Test artifacts cleaned"
}

# Usage information
usage() {
    cat << USAGE_EOF
\$SCRIPT_NAME v\$SCRIPT_VERSION - TESTSH Test Runner for \$PROJECT_NAME

USAGE:
    \$SCRIPT_NAME <command> [args]

COMMANDS:
    list                   List all test categories and counts
    run [category]         Run tests (all categories if none specified)
    bootstrap [lang]       Initialize test structure (auto-detect language)
    clean                  Clean test artifacts and temporary files

TEST CATEGORIES:
    sanity, smoke, unit, integration, e2e, uat, chaos, bench, adhoc

EXAMPLES:
    \$SCRIPT_NAME list
    \$SCRIPT_NAME run
    \$SCRIPT_NAME run sanity
    \$SCRIPT_NAME bootstrap rust
    \$SCRIPT_NAME clean

USAGE_EOF
}

# Main execution
main() {
    case "\${1:-run}" in
        list|ls)
            cmd_list
            ;;
        run|test)
            shift
            cmd_run "\$@"
            ;;
        bootstrap|init)
            shift
            cmd_bootstrap "\$@"
            ;;
        clean)
            cmd_clean
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            error "Unknown command: \$1"
            usage
            return 1
            ;;
    esac
}

main "\$@"
EOF
}

__print_testsh_wrappers() {
    local target_dir="$1"
    local name="$2"

    # Create placeholder wrapper files for each category
    for category in sanity smoke unit integration e2e uat chaos bench; do
        cat > "$target_dir/tests/$category.sh" << EOF
#!/usr/bin/env bash
# tests/$category.sh - $category test wrapper for $name

echo "Running $category tests for $name"

# Add your $category test logic here
# This wrapper can coordinate multiple test files in tests/$category/

exit 0
EOF
        chmod +x "$target_dir/tests/$category.sh"
    done
}

__print_testsh_examples() {
    local target_dir="$1"
    local name="$2"

    # Create example test files
    cat > "$target_dir/tests/sanity/basic.sh" << EOF
#!/usr/bin/env bash
# tests/sanity/basic.sh - Basic sanity checks

test_project_structure() {
    [[ -f "README.md" ]] || { echo "README.md missing"; return 1; }
    [[ -d "tests" ]] || { echo "tests directory missing"; return 1; }
    echo "Project structure is sane"
    return 0
}

test_project_structure
EOF
    chmod +x "$target_dir/tests/sanity/basic.sh"

    cat > "$target_dir/tests/smoke/quick.sh" << EOF
#!/usr/bin/env bash
# tests/smoke/quick.sh - Quick smoke tests

test_basic_functionality() {
    echo "Running smoke test for $name"
    # Add basic functionality tests here
    return 0
}

test_basic_functionality
EOF
    chmod +x "$target_dir/tests/smoke/quick.sh"

    # Create adhoc demo
    cat > "$target_dir/tests/_adhoc/demo.sh" << EOF
#!/usr/bin/env bash
# tests/_adhoc/demo.sh - Demonstration adhoc test

echo "This is an adhoc test for $name"
echo "Adhoc tests are for one-off testing scenarios"
echo "They don't fit into standard test categories"

# Example: Test a specific bug fix or feature
exit 0
EOF
    chmod +x "$target_dir/tests/_adhoc/demo.sh"
}

__print_testsh_gitignore() {
    local file="$1"

    cat > "$file" << 'EOF'
# Test artifacts
tests/**/*.tmp
tests/**/*.log
/tmp/*test*

# Coverage reports
coverage/
*.coverage
.nyc_output/

# Test outputs
test-results/
junit.xml

# Language-specific test artifacts
target/debug/deps/*test*
node_modules/
__pycache__/
*.pyc
.pytest_cache/

EOF

    # Add common patterns
    __print_common_gitignore "$file"
}


################################################################################
# Part 69: part_69_dispatcher.sh
################################################################################

################################################################################
# Core System Functions
################################################################################

dispatch() {
    local cmd="$1"
    shift
    
    case "$cmd" in
        # Core git simulation
        init)           
            # Check for --template flag
            local template=""
            local other_args=()
            for arg in "$@"; do
                if [[ "$arg" =~ ^--template=(.+)$ ]]; then
                    template="${BASH_REMATCH[1]}"
                else
                    other_args+=("$arg")
                fi
            done
            
            if [[ -n "$template" ]]; then
                do_init_with_template "$template" "${other_args[@]}"
            else
                do_init "$@"
            fi
            ;;
        init-in-home)   
            # Check for --template flag
            local template=""
            local project_name="$1"
            for arg in "$@"; do
                if [[ "$arg" =~ ^--template=(.+)$ ]]; then
                    template="${BASH_REMATCH[1]}"
                    break
                fi
            done
            
            if [[ -n "$template" ]]; then
                do_init_in_home_with_template "$project_name" "$template"
            else
                do_init_in_home "$@"
            fi
            ;;
        add)            do_add "$@";;
        commit)         do_commit "$@";;
        status)         do_status "$@";;
        
        # Home environment
        home-init)      
            # Check for --template flag
            local template=""
            for arg in "$@"; do
                if [[ "$arg" =~ ^--template=(.+)$ ]]; then
                    template="${BASH_REMATCH[1]}"
                    break
                fi
            done
            
            if [[ -n "$template" ]]; then
                do_init_in_home_with_template "$1" "$template" 
            else
                do_home_init "$@"
            fi
            ;;
        home-env)       do_home_env "$@";;
        home-path)      do_home_path "$@";;
        home-ls)        do_home_ls "$@";;
        home-vars)      do_home_vars "$@";;
        
        # Template system
        template)       do_template "$@";;
        template-list)  do_template_list "$@";;
        template-show)  do_template_show "$@";;
        
        # Test data generation
        noise)          do_noise "$@";;
        
        # Configuration
        rcgen)          do_rcgen "$@";;
        cleanup)        do_cleanup "$@";;
        
        # System management
        install)        do_install "$@";;
        uninstall)      do_uninstall "$@";;
        version)        do_version "$@";;
        help)           usage;;

        *)
            error "Unknown command: $cmd"
            usage
            return 1
            ;;
    esac
}

usage() {
    cat << 'EOF'
gitsim - Git & Home Environment Simulator v2.0.0

USAGE:
    gitsim <command> [options] [args]

CORE COMMANDS:
    init [--template=TYPE]      Create git simulation in current directory
    init-in-home [project] [--template=TYPE]  Create git simulation in simulated home project
    add <files>                 Add files to staging area
    commit -m "message"         Create a commit with message
    status                      Show repository status

HOME ENVIRONMENT:
    home-init [project] [--template=TYPE]  Initialize simulated home environment
    home-env                   Show simulated environment variables
    home-path                  Get path to simulated home directory  
    home-ls [dir] [opts]       List contents of simulated home
    home-vars                  Show SIM_ environment variables

TEMPLATES:
    template <type> [project]  Create project template (rust, bash, node, python)
    template-list              List available templates
    template-show <type>       Show template preview

TEST DATA:
    noise [count]              Create random files and stage them

CONFIGURATION:
    rcgen [--force]            Generate .simrc configuration file
    cleanup [--force]          Clean up all GitSim artifacts

SYSTEM:
    install                    Install to XDG+ directories
    uninstall --force          Remove installation
    version                    Show version information

OPTIONS:
    -d, --debug                Enable debug output
    -t, --trace                Enable trace output (implies -d)
    -q, --quiet                Suppress all output except errors
    -f, --force                Force operations, bypass safety checks
    -y, --yes                  Automatically answer yes to prompts
    -D, --dev                  Enable developer mode

ENVIRONMENT VARIABLES:
    SIM_HOME                   Base simulated home [$SIM_HOME]
    SIM_USER                   Simulated username [$SIM_USER]  
    SIM_SHELL                  Simulated shell [$SIM_SHELL]
    SIM_EDITOR                 Simulated editor [$SIM_EDITOR]

EXAMPLES:
    gitsim init --template=rust
    gitsim init-in-home webapp --template=node
    gitsim template python backend
    gitsim home-init myproject
    gitsim noise 5
    gitsim commit -m "Test commit"
    
    # Use simulated environment in scripts:
    HOME_PATH=$(gitsim home-path)
    cp myfile "$HOME_PATH/.config/"

TEMPLATES AVAILABLE:
    rust (rs)      - Rust project with Cargo
    bash (sh)      - BashFX-compliant script project
    node (js)      - Node.js project with npm
    python (py)    - Python project with modern tooling

EOF
}

options() {
    local this next opts=("$@")
    for ((i=0; i<${#opts[@]}; i++)); do
        this=${opts[i]}
        next=${opts[i+1]}
        case "$this" in
            -d|--debug)
                opt_debug=true
                opt_quiet=false
                ;;
            -t|--trace)
                opt_trace=true
                opt_debug=true
                opt_quiet=false
                ;;
            -q|--quiet)
                opt_quiet=true
                ;;
            -f|--force)
                opt_force=true
                ;;
            -y|--yes)
                opt_yes=true
                ;;
            -D|--dev)
                opt_dev=true
                opt_debug=true
                opt_trace=true
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                :
                ;;
        esac
    done
}

################################################################################
# Part 70: part_70_dispatchable_core.sh
################################################################################

################################################################################
# Dispatchable Functions (Core Git Commands)
################################################################################

do_init() {
    local sim_dir=".gitsim"
    local data_dir="$sim_dir/.data"
    local ret=1

    if [ -d "$data_dir" ]; then
        info "Reinitialized existing Git simulator repository in $(pwd)/$sim_dir/"
        ret=0
    else
        if __create_git_structure "$data_dir"; then
            okay "Initialized empty Git simulator repository in $(pwd)/$sim_dir/"
            ret=0
        else
            error "Failed to create Git simulator structure"
        fi
    fi

    __add_gitignore_entry ".gitsim/"
    return "$ret"
}

do_add() {
    local sim_root
    local state_file_index
    local ret=1
    
    sim_root=$(_find_sim_root) || {
        error "Not in a git repository (or any of the parent directories): .gitsim"
        return 128
    }
    
    state_file_index="$sim_root/.gitsim/.data/index"
    
    if [[ "$1" == "." ]] || [[ "$1" == "--all" ]]; then
        > "$state_file_index"
        (cd "$sim_root" && find . -type f -not -path "./.gitsim/*" -not -path "./.git/*" | sed 's|^\./||') >> "$state_file_index"
    else
        for file in "$@"; do
            echo "$file" >> "$state_file_index"
        done
    fi
    
    sort -u "$state_file_index" -o "$state_file_index"
    return 0
}

do_commit() {
    local sim_root
    local commits_file
    local head_file  
    local index_file
    local message=""
    local allow_empty=false
    local ret=1
    
    sim_root=$(_find_sim_root) || {
        error "Not in a git repository (or any of the parent directories): .gitsim"
        return 128
    }
    
    commits_file="$sim_root/.gitsim/.data/commits.txt"
    head_file="$sim_root/.gitsim/.data/HEAD"
    index_file="$sim_root/.gitsim/.data/index"
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -m) message="$2"; shift 2;;
            --allow-empty) allow_empty=true; shift;;
            *) shift;;
        esac
    done
    
    if [ -z "$message" ]; then
        error "No commit message provided"
        return 1
    fi

    if [ "$allow_empty" = false ] && ! [ -s "$index_file" ]; then
        error "nothing to commit, working tree clean"
        return 1
    fi

    local commit_hash
    commit_hash=$( (echo "$message" ; date +%s) | shasum | head -c 7)
    echo "$commit_hash $message" >> "$commits_file"
    echo "$commit_hash" > "$head_file"
    > "$index_file"
    
    okay "Committed: $message [$commit_hash]"
    return 0
}

do_status() {
    local sim_root
    local index_file
    local branch_file
    local ret=1
    
    sim_root=$(_find_sim_root) || {
        error "Not in a git repository (or any of the parent directories): .gitsim"
        return 128
    }
    
    index_file="$sim_root/.gitsim/.data/index"
    branch_file="$sim_root/.gitsim/.data/branch.txt"
    
    if [[ "$1" == "--porcelain" ]]; then
        if [ -s "$index_file" ]; then
            sed 's/^/A  /' "$index_file"
        fi
        return 0
    fi
    
    # Human-readable output
    local branch
    branch=$(cat "$branch_file" 2>/dev/null)
    printf "On branch %s\n" "${branch:-main}"
    
    if [ -s "$index_file" ]; then
        printf "Changes to be committed:\n"
        printf "  (use \"git restore --staged <file>...\" to unstage)\n"
        sed 's/^/\tnew file:   /' "$index_file"
    else
        printf "\n"
        printf "nothing to commit, working tree clean\n"
    fi
    
    return 0
}

################################################################################
# Part 71: part_71_dispatchable_home.sh
################################################################################

################################################################################
# Dispatchable Functions (Home Environment)
################################################################################

do_init_in_home() {
    local project_name="${1:-testproject}"
    local sim_root
    local home_dir
    local project_dir
    local ret=1
    
    sim_root=$(_find_sim_root) || {
        # Create a temporary sim root in current directory
        if __create_git_structure ".gitsim/.data"; then
            sim_root="$PWD"
        else
            error "Failed to create temporary sim root"
            return 1
        fi
    }
    
    home_dir=$(_get_sim_home "$sim_root")
    
    # Ensure home is initialized
    if [ ! -d "$home_dir" ]; then
        do_home_init "$sim_root" "$project_name" || return 1
    fi
    
    project_dir=$(_get_sim_project_dir "$home_dir" "$project_name")
    
    # Create git simulation in the project directory
    local project_data_dir="$project_dir/.gitsim/.data"
    
    if [ -d "$project_data_dir" ]; then
        info "Reinitialized existing Git simulator repository in $project_dir/.gitsim/"
        ret=0
    else
        if __create_git_structure "$project_data_dir"; then
            okay "Initialized empty Git simulator repository in $project_dir/.gitsim/"
            ret=0
        else
            error "Failed to create project Git simulator structure"
            return 1
        fi
    fi
    
    # Create project files
    printf "# %s\n" "$project_name" > "$project_dir/README.md"
    printf "node_modules/\n.gitsim/\n" > "$project_dir/.gitignore"
    
    info "Project path: $project_dir"
    info "To work in this project: cd '$project_dir'"
    
    return "$ret"
}

do_home_init() {
    local sim_root="${1:-$PWD}"
    local project_name="${2:-testproject}"
    local home_dir
    local project_dir
    local ret=1
    
    # Handle case where we don't have a sim_root yet
    if [ ! -d "$sim_root/.gitsim" ]; then
        if __create_git_structure "$sim_root/.gitsim/.data"; then
            trace "Created temporary sim structure"
        else
            error "Failed to create sim structure"
            return 1
        fi
    fi
    
    home_dir=$(_get_sim_home "$sim_root")
    
    if [ -d "$home_dir" ]; then
        info "Reinitialized simulated home environment at $home_dir"
        ret=0
    else
        if _setup_home_env "$home_dir"; then
            okay "Initialized simulated home environment at $home_dir"
            ret=0
        else
            error "Failed to setup home environment"
            return 1
        fi
    fi
    
    # Create project directory
    project_dir=$(_get_sim_project_dir "$home_dir" "$project_name")
    mkdir -p "$project_dir"
    okay "Created project directory at $project_dir"
    
    return "$ret"
}

do_home_env() {
    local sim_root
    local home_dir
    local ret=1
    
    sim_root=$(_find_sim_root) || {
        error "Not in a git simulator repository"
        return 1
    }
    
    home_dir=$(_get_sim_home "$sim_root")
    
    if [ ! -d "$home_dir" ]; then
        error "Simulated home not initialized. Run 'home-init' first."
        return 1
    fi
    
    printf "# Simulated environment paths (do not override \$HOME)\n"
    printf "SIM_HOME='%s'\n" "$home_dir"
    printf "SIM_USER='%s'\n" "$SIM_USER"
    printf "SIM_SHELL='%s'\n" "$SIM_SHELL"
    printf "SIM_EDITOR='%s'\n" "$SIM_EDITOR"
    printf "SIM_LANG='%s'\n" "$SIM_LANG"
    printf "\n"
    printf "# XDG directories within simulated home\n"
    printf "SIM_XDG_CONFIG_HOME='%s/.config'\n" "$home_dir"
    printf "SIM_XDG_DATA_HOME='%s/.local/share'\n" "$home_dir"
    printf "SIM_XDG_STATE_HOME='%s/.local/state'\n" "$home_dir"
    printf "SIM_XDG_CACHE_HOME='%s/.cache'\n" "$home_dir"
    printf "\n"
    printf "# To use in scripts, reference these paths directly\n"
    printf "# Example: cp myfile \"\$SIM_XDG_CONFIG_HOME/\"\n"
    
    return 0
}

do_home_path() {
    local sim_root
    local ret=1
    
    sim_root=$(_find_sim_root) || {
        error "Not in a git simulator repository"
        return 1
    }
    
    _get_sim_home "$sim_root"
    return 0
}

do_home_ls() {
    local sim_root
    local home_dir
    local subdir="${1:-.}"
    local ret=1
    
    sim_root=$(_find_sim_root) || {
        error "Not in a git simulator repository"
        return 1
    }
    
    home_dir=$(_get_sim_home "$sim_root")
    
    if [ ! -d "$home_dir" ]; then
        error "Simulated home not initialized. Run 'home-init' first."
        return 1
    fi
    
    local target_dir="$home_dir/$subdir"
    if [ ! -d "$target_dir" ]; then
        error "Directory not found: $target_dir"
        return 1
    fi
    
    shift
    if [ $# -eq 0 ]; then
        ls "$target_dir"
    else
        ls "$@" "$target_dir"
    fi
    ret=$?
    
    return "$ret"
}

do_home_vars() {
    printf "Current SIM_ environment variables:\n"
    printf "SIM_HOME=%s\n" "$SIM_HOME"
    printf "SIM_USER=%s\n" "$SIM_USER"
    printf "SIM_SHELL=%s\n" "$SIM_SHELL"
    printf "SIM_EDITOR=%s\n" "$SIM_EDITOR"  
    printf "SIM_LANG=%s\n" "$SIM_LANG"
    printf "\n"
    printf "To override, set before running script:\n"
    printf "SIM_USER=alice SIM_EDITOR=vim ./gitsim.sh home-init\n"
    printf "Or create a .simrc file: gitsim rcgen\n"
    return 0
}

################################################################################
# Part 72: part_72_dispatchable_system.sh
################################################################################

################################################################################
# Dispatchable Functions (System Management)
################################################################################

_get_version() {
    # Extract version from semv metadata
    local version
    version=$(grep "^# semv-version:" "$0" | cut -d' ' -f3)
    [[ -z "$version" ]] && version="unknown"
    echo "$version"
}

do_version() {
    printf "%s v%s\n" "$GITSIM_NAME" "$(_get_version)"
    return 0
}

do_install() {
    local ret=1

    info "Installing $GITSIM_NAME to XDG+ directories..."

    # Remove previous installation if it exists
    if [[ -f "$GITSIM_LIB_DIR/gitsim.sh" ]]; then
        info "Removing previous installation..."
        rm -f "$GITSIM_LIB_DIR/gitsim.sh"
        trace "Removed previous lib file"
    fi

    if [[ -L "$GITSIM_BIN_LINK" ]] || [[ -f "$GITSIM_BIN_LINK" ]]; then
        info "Removing previous symlink..."
        rm -f "$GITSIM_BIN_LINK"
        trace "Removed previous bin symlink"
    fi

    # Create directories
    mkdir -p "$GITSIM_LIB_DIR" "$XDG_BIN_HOME/fx" || {
        error "Failed to create installation directories"
        return 1
    }

    # Copy script to lib directory
    if cp "$0" "$GITSIM_LIB_DIR/gitsim.sh"; then
        trace "Copied script to $GITSIM_LIB_DIR"
    else
        error "Failed to copy script to lib directory"
        return 1
    fi

    # Create symlink in bin directory (flattened, no .sh extension)
    if ln -s "$GITSIM_LIB_DIR/gitsim.sh" "$GITSIM_BIN_LINK"; then
        trace "Created symlink at $GITSIM_BIN_LINK"
    else
        error "Failed to create symlink"
        return 1
    fi

    # Make sure it's executable
    chmod +x "$GITSIM_LIB_DIR/gitsim.sh"

    okay "Installed $GITSIM_NAME successfully"
    info "Add $XDG_BIN_HOME/fx to your PATH to use: export PATH=\"$XDG_BIN_HOME/fx:\$PATH\""

    return 0
}

do_uninstall() {
    local ret=1
    
    if [[ "$opt_force" == false ]]; then
        error "Uninstall requires --force flag for safety"
        info "Use: $GITSIM_NAME uninstall --force"
        return 1
    fi
    
    info "Uninstalling $GITSIM_NAME..."
    
    # Remove symlink
    if [ -L "$GITSIM_BIN_LINK" ]; then
        rm -f "$GITSIM_BIN_LINK"
        trace "Removed symlink $GITSIM_BIN_LINK"
    fi
    
    # Remove lib directory
    if [ -d "$GITSIM_LIB_DIR" ]; then
        rm -rf "$GITSIM_LIB_DIR"
        trace "Removed lib directory $GITSIM_LIB_DIR"
    fi
    
    okay "Uninstalled $GITSIM_NAME successfully"
    return 0
}

################################################################################
# Part 80: part_80_dispatchable_utils.sh
################################################################################

################################################################################
# Dispatchable Functions (Utilities)
################################################################################

do_noise() {
    local sim_root
    local data_dir
    local num_files="${1:-1}"
    local ret=1
    
    sim_root=$(_find_sim_root) || {
        error "Not in a git repository (or any of the parent directories): .gitsim"
        return 128
    }
    
    data_dir="$sim_root/.gitsim/.data"
    
    local names=("README" "script" "status" "main" "feature" "hotfix" "docs" "config" "utils" "test")
    local exts=(".md" ".fake" ".log" ".sh" ".txt" ".tmp" ".json" ".yml" ".xml" ".conf")

    for i in $(seq 1 "$num_files"); do
        local rand_name=${names[$RANDOM % ${#names[@]}]}
        local rand_ext=${exts[$RANDOM % ${#exts[@]}]}
        local filename="${rand_name}_${i}${rand_ext}"

        head /dev/urandom | tr -dc A-Za-z0-9 | head -c 32 > "$sim_root/$filename"
        echo "$filename" >> "$data_dir/index"
    done

    sort -u "$data_dir/index" -o "$data_dir/index"
    okay "Created and staged ${num_files} noisy file(s)"
    return 0
}

do_rcgen() {
    local simrc_file=".simrc"
    local force_overwrite=false
    
    # Check for force flag
    if [[ "$1" == "--force" ]]; then
        force_overwrite=true
        shift
    fi
    
    # Check if file exists and we're not forcing
    if [ -f "$simrc_file" ] && [[ "$force_overwrite" == false ]]; then
        error "File $simrc_file already exists. Use --force to overwrite."
        return 1
    fi
    
    # Generate the .simrc file
    __print_simrc "$simrc_file"
    
    okay "Created $simrc_file configuration file"
    info "Edit this file to customize your SIM_ environment variables"
    info "The file will be automatically sourced when running gitsim commands"
    
    return 0
}

do_cleanup() {
    local force_cleanup="${1:-false}"
    local sim_root="$PWD"
    local simrc_file=".simrc"
    
    info "Starting cleanup of GitSim artifacts..."
    
    # Clean up .gitsim directory
    if [[ -d ".gitsim" ]]; then
        if [[ "$force_cleanup" == "true" ]] || [[ "$opt_yes" == "true" ]]; then
            rm -rf ".gitsim"
            okay "Removed .gitsim directory"
        else
            warn "Found .gitsim directory"
            read -p "Remove .gitsim directory? [y/N]: " -r
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                rm -rf ".gitsim"
                okay "Removed .gitsim directory"
            fi
        fi
    fi
    
    # Clean up generated files from .simrc
    if [[ -f "$simrc_file" ]]; then
        # Source the .simrc to get GENERATED_FILES array
        local generated_files=()
        # Extract GENERATED_FILES array safely
        if grep -q "GENERATED_FILES=" "$simrc_file"; then
            # Use eval with proper safety checks
            local files_line
            files_line=$(grep "GENERATED_FILES=" "$simrc_file" | head -1)
            if [[ -n "$files_line" ]]; then
                eval "$files_line"
                generated_files=("${GENERATED_FILES[@]}")
            fi
        fi
        
        if [[ ${#generated_files[@]} -gt 0 ]]; then
            info "Found ${#generated_files[@]} tracked generated files"
            for file in "${generated_files[@]}"; do
                if [[ -f "$file" ]]; then
                    if [[ "$force_cleanup" == "true" ]] || [[ "$opt_yes" == "true" ]]; then
                        rm -f "$file"
                        okay "Removed generated file: $file"
                    else
                        read -p "Remove generated file '$file'? [y/N]: " -r
                        if [[ $REPLY =~ ^[Yy]$ ]]; then
                            rm -f "$file"
                            okay "Removed generated file: $file"
                        fi
                    fi
                fi
            done
        fi
        
        # Clean up .simrc itself
        if [[ "$force_cleanup" == "true" ]] || [[ "$opt_yes" == "true" ]]; then
            rm -f "$simrc_file"
            okay "Removed $simrc_file"
        else
            read -p "Remove $simrc_file? [y/N]: " -r
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                rm -f "$simrc_file"
                okay "Removed $simrc_file"
            fi
        fi
    fi
    
    # Clean up .gitignore entries we added
    if [[ -f ".gitignore" ]] && grep -q "^\.gitsim/$" ".gitignore"; then
        grep -v "^\.gitsim/$" ".gitignore" > ".gitignore.tmp" && mv ".gitignore.tmp" ".gitignore"
        okay "Removed .gitsim/ from .gitignore"
    fi
    
    okay "Cleanup complete"
    return 0
}

################################################################################
# Part 90: part_90_dispatcher.sh
################################################################################

################################################################################
# Core System Functions
################################################################################

# NOTE: Main dispatch() function is defined in part_69_dispatcher.sh
# This part only contains the usage() function to avoid duplication

usage() {
    local version
    version=$(_get_version)

    cat << EOF
gitsim - Git & Home Environment Simulator v$version

USAGE:
    gitsim <command> [options] [args]

CORE COMMANDS:
    init                    Create git simulation in current directory
    init-in-home [project]  Create git simulation in simulated home project
    add <files>             Add files to staging area
    commit -m "message"     Create a commit with message
    status                  Show repository status

HOME ENVIRONMENT:
    home-init [project]     Initialize simulated home environment
    home-env               Show simulated environment variables
    home-path              Get path to simulated home directory  
    home-ls [dir] [opts]   List contents of simulated home
    home-vars              Show SIM_ environment variables

TEMPLATES:
    template <type> [project]  Create project template (rust, bash, node, python)
    template-list              List available templates
    template-show <type>       Show template preview

TEST DATA:
    noise [count]          Create random files and stage them

CONFIGURATION:
    rcgen [--force]        Generate .simrc configuration file
    cleanup [--force]      Clean up all GitSim artifacts

SYSTEM:
    install                Install to XDG+ directories
    uninstall --force      Remove installation
    version                Show version information
    help                   Show this help message

OPTIONS:
    -d, --debug            Enable debug output
    -t, --trace            Enable trace output (implies -d)
    -q, --quiet            Suppress all output except errors
    -f, --force            Force operations, bypass safety checks
    -D, --dev              Enable developer mode
    -h, --help             Show this help message
    -v, --version          Show version information

ENVIRONMENT VARIABLES:
    SIM_HOME               Base simulated home [$SIM_HOME]
    SIM_USER               Simulated username [$SIM_USER]  
    SIM_SHELL              Simulated shell [$SIM_SHELL]
    SIM_EDITOR             Simulated editor [$SIM_EDITOR]

EXAMPLES:
    gitsim init
    gitsim home-init myproject
    gitsim template rust myproject
    gitsim template-list
    gitsim noise 5
    gitsim commit -m "Test commit"
    
    # Use simulated environment in scripts:
    HOME_PATH=$(gitsim home-path)
    cp myfile "$HOME_PATH/.config/"

EOF
}

options() {
    local this next opts=("$@")
    for ((i=0; i<${#opts[@]}; i++)); do
        this=${opts[i]}
        next=${opts[i+1]}
        case "$this" in
            -d|--debug)
                opt_debug=true
                ;;
            -t|--trace)
                opt_trace=true
                opt_debug=true
                ;;
            -q|--quiet)
                opt_quiet=true
                ;;
            -f|--force)
                opt_force=true
                ;;
            -y|--yes)
                opt_yes=true
                ;;
            -D|--dev)
                opt_dev=true
                opt_debug=true
                opt_trace=true
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            -v|--version)
                do_version
                exit 0
                ;;
            *)
                :
                ;;
        esac
    done
}

################################################################################
# Part 99: part_99_main.sh
################################################################################

main() {
    # Show logo for interactive commands only
    case "$1" in
        home-path|version)
            # Skip logo for commands that return data for scripting
            ;;
        *)
            _logo
            ;;
    esac
    
    # Try to source .simrc for environment customization
    _source_simrc
    
    # Show help if no command provided
    if [[ ${#@} -eq 0 ]]; then
        usage
        exit 0
    fi
    
    # For home/project commands, suggest .simrc if not found
    case "$1" in
        home-init|init-in-home|home-vars|template)
            _check_simrc || true  # Don't fail on missing .simrc
            ;;
    esac
    
    # Dispatch to command
    dispatch "$@"
    return $?
}

# Script execution using BashFX pattern
if [ "$0" = "-bash" ]; then
    :
else
    # direct call
    orig_args=("$@")
    options "${orig_args[@]}"
    # Filter out global options but preserve command-specific flags
    args=()
    skip_next=false
    for arg in "${orig_args[@]}"; do
        if [ "$skip_next" = true ]; then
            skip_next=false
            continue
        fi
        
        case "$arg" in
            # Global options that should be filtered
            -d|--debug|-t|--trace|-q|--quiet|-f|-y|--yes|-D|--dev|-h|--help|-v|--version)
                ;;
            # Command-specific flags that should be preserved
            -m|--allow-empty|--template=*|--porcelain|--force|--testsh)
                args+=("$arg")
                # If -m, also preserve the next argument (the message)
                if [[ "$arg" == "-m" ]]; then
                    skip_next=false  # We'll add the next arg in the next iteration
                fi
                ;;
            # Non-option arguments
            *)
                args+=("$arg")
                ;;
        esac
    done
    main "${args[@]}"
    ret=$?
    exit $ret
fi
