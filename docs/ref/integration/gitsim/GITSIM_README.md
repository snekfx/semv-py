# GitSim - Git & Home Environment Simulator

![version](https://img.shields.io/badge/version-2.1.2-blue)
![architecture](https://img.shields.io/badge/architecture-BashFX_2.1-green)
![dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen)
![testing](https://img.shields.io/badge/testing-TESTSH_compliant-purple)

A BashFX 2.1 compliant tool for creating realistic git repositories and home environments for testing, demonstrations, and development workflows. GitSim provides safe, isolated environments that simulate real development scenarios without polluting your actual workspace.

**NEW in v2.1.2**: Professional-grade **TESTSH testing framework** with comprehensive test categories, multi-language support, and automated bootstrap capabilities for serious development workflows.

## 🎯 Key Features

- **🔄 Git Simulation**: Full git operations (init, add, commit, status) with realistic repository structure
- **🏠 Home Environment**: Complete XDG-compliant simulated home directories with dotfiles
- **📋 Project Templates**: Professional scaffolding for Rust, Node.js, Python, BashFX, and **TESTSH** projects
- **🧪 TESTSH Testing Framework**: Comprehensive test suites with 8 categories (unit, sanity, smoke, integration, e2e, uat, chaos, bench)
- **🔧 Multi-Language Support**: Template generation for Rust, JavaScript, Python, Bash with automatic language detection
- **⚡ Bootstrap Capabilities**: Automated test structure generation with executable examples
- **🛡️ Safe Operations**: Zero risk to your real repositories and home directory
- **🧹 Rewindable**: Complete cleanup and uninstall capabilities
- **📦 Zero Dependencies**: Pure bash with only POSIX utilities
- **🏗️ Modular Architecture**: 18-part BashFX build system for maintainability

## 🚀 Quick Start

### Basic Usage
```bash
# Clone and test immediately
git clone <repository>
cd fx-gitsim

# Initialize git simulation in current directory
./gitsim.sh init

# Create files and commit them
echo "Hello World" > hello.txt
./gitsim.sh add hello.txt
./gitsim.sh commit -m "Add hello world"
./gitsim.sh status
```

### Professional Test Suite Creation (NEW!)
```bash
# Create comprehensive TESTSH test suite
./gitsim.sh template testsh myproject
cd myproject

# Creates a testsim.sh script!

# Run the complete test suite
./testsim.sh run

# Bootstrap additional test structure for Rust
./testsim.sh bootstrap rust

# Run specific test categories
./testsim.sh run sanity
./testsim.sh run e2e
./testsim.sh list  # See all available tests
```

### Enhanced Project Templates
```bash
# Create BashFX project with integrated TESTSH
./gitsim.sh template bash myproject --testsh
cd myproject && ./testsim.sh run

# Standard project templates
./gitsim.sh template rust myproject
./gitsim.sh template node frontend
./gitsim.sh template python ml-service

# Set up simulated home environment
./gitsim.sh home-init
HOME_PATH=$(./gitsim.sh home-path)
echo "Simulated home: $HOME_PATH"
```

## 📥 Installation

### Option 1: Standalone Usage (Recommended for Testing)
```bash
# Download and use immediately
wget <url>/gitsim.sh
chmod +x gitsim.sh
./gitsim.sh init
```

### Option 2: System Installation (Enhanced in v2.1.2)
```bash
# Install to XDG+ directories (~/.local)
./gitsim.sh install  # Now handles upgrades automatically

# Add to PATH
export PATH="$HOME/.local/bin/fx:$PATH"

# Verify installation with dynamic version
gitsim version
gitsim -v        # Short form
gitsim --version # Long form

# Get help
gitsim help
gitsim -h
gitsim --help

# Generate configuration (optional)
gitsim rcgen
```

### Option 3: Development Setup (Improved Build System)
```bash
# For developers working on GitSim itself
git clone <repository>
cd fx-gitsim

# Build system now includes bin/ directory
./build.sh build     # Build from parts using new architecture
./bin/testsim.sh         # Enhanced test runner with TESTSH
./bin/build.sh        # Modular build scripts
```

## 📖 Complete API Reference

### Core Git Commands

#### `init [options]`
Initialize git simulation in current directory.

**Options:**
- `--template=TYPE` - Apply project template (rust, bash, node, python)

**Examples:**
```bash
./gitsim.sh init                    # Basic git simulation
./gitsim.sh init --template=rust    # With Rust project template
```

#### `init-in-home [project] [options]`
Create git simulation in simulated home environment.

**Arguments:**
- `project` - Project name (default: "testproject")

**Options:**
- `--template=TYPE` - Apply project template

**Examples:**
```bash
./gitsim.sh init-in-home                    # Default project
./gitsim.sh init-in-home webapp             # Named project
./gitsim.sh init-in-home api --template=rust # With template
```

#### `add <files...>`
Add files to staging area.

**Arguments:**
- `files` - One or more file paths to stage

**Examples:**
```bash
./gitsim.sh add file.txt
./gitsim.sh add src/*.rs
./gitsim.sh add .
```

#### `commit -m "message" [options]`
Create a commit with specified message.

**Options:**
- `-m "message"` - Commit message (required)
- `--allow-empty` - Allow commit with no changes

**Examples:**
```bash
./gitsim.sh commit -m "Initial commit"
./gitsim.sh commit -m "Add feature" --allow-empty
```

#### `status`
Show repository status (staged files, commits, etc.)

**Examples:**
```bash
./gitsim.sh status
```

### Home Environment Commands

#### `home-init [project] [options]`
Initialize simulated home environment with XDG directory structure.

**Arguments:**
- `project` - Project name for ~/projects/PROJECT (default: "testproject")

**Options:**
- `--template=TYPE` - Apply project template to the project directory

**Examples:**
```bash
./gitsim.sh home-init                    # Default setup
./gitsim.sh home-init myapp             # Named project
./gitsim.sh home-init api --template=rust # With Rust template
```

#### `home-path`
Get absolute path to simulated home directory.

**Examples:**
```bash
HOME_PATH=$(./gitsim.sh home-path)
cp config.toml "$HOME_PATH/.config/myapp/"
```

#### `home-env`
Show simulated environment variables for the current session.

**Examples:**
```bash
./gitsim.sh home-env
# Output: HOME=/path/to/.gitsim/.home USER=testuser ...
```

#### `home-ls [dir] [options]`
List contents of simulated home directory.

**Arguments:**
- `dir` - Subdirectory to list (default: home root)
- `options` - Standard ls options (-la, -lh, etc.)

**Examples:**
```bash
./gitsim.sh home-ls           # List home root
./gitsim.sh home-ls -la       # Detailed listing
./gitsim.sh home-ls projects  # List projects directory
```

#### `home-vars`
Show all SIM_ environment variables and their values.

**Examples:**
```bash
./gitsim.sh home-vars
# Output: SIM_HOME=/path SIM_USER=testuser ...
```

### Template System

#### `template <type> [project]`
Generate project template in specified or current directory.

**Arguments:**
- `type` - Template type (see template list below)
- `project` - Target directory name (optional)

**Examples:**
```bash
./gitsim.sh template rust           # In current directory
./gitsim.sh template rust myapp     # In ./myapp directory
./gitsim.sh template node frontend  # Node.js project
```

#### `template-list`
Show all available project templates.

**Output includes:**
- Template names and descriptions
- Available aliases

**Examples:**
```bash
./gitsim.sh template-list
```

#### `template-show <type>`
Preview template contents and structure.

**Arguments:**
- `type` - Template type to preview

**Examples:**
```bash
./gitsim.sh template-show rust
```

### Available Templates

| Template | Aliases | Description | Generated Structure |
|----------|---------|-------------|--------------------|
| **testsh** | test-suite, testing | **NEW!** TESTSH-compliant comprehensive test suite | testsim.sh, tests/{8 categories}, scripts/bootstrap-tests.sh |
| **rust** | rs | Cargo project with modern Rust setup | Cargo.toml, src/main.rs, src/lib.rs, tests/, .gitignore |
| **bash** | sh, bashfx | BashFX-compliant script with build system | script.sh, parts/, build.map, test_runner.sh |
| **node** | js, npm, javascript | Node.js project with modern tooling | package.json, src/index.js, test/, .gitignore |
| **python** | py | Modern Python with pyproject.toml | pyproject.toml, src/project/, tests/, .gitignore |

#### Enhanced Template Options (v2.1.2)

**TESTSH Integration**: The bash template now supports the `--testsh` flag for comprehensive testing:
```bash
./gitsim.sh template bash myproject --testsh  # BashFX + TESTSH integration
```

**Test Categories**: TESTSH template includes 8 organized test categories:
- **sanity** - Basic functionality validation
- **smoke** - Quick health checks
- **unit** - Component isolation testing
- **integration** - Component interaction testing
- **e2e** - End-to-end workflow testing
- **uat** - User acceptance testing
- **chaos** - Resilience and failure testing
- **bench** - Performance benchmarking
- **_adhoc** - One-off testing scenarios

### TESTSH Template System (NEW in v2.1.2)

The TESTSH template system provides professional-grade testing infrastructure for any language or project type.

#### `template testsh [project]`
Create a standalone comprehensive test suite.

**Arguments:**
- `project` - Target directory name (optional, uses current directory if omitted)

**Generated Structure:**
```
myproject/
├── testsim.sh                    # Main TESTSH-compliant test runner
├── scripts/
│   └── bootstrap-tests.sh     # Multi-language test generator
├── tests/
│   ├── {category}.sh          # Category wrapper scripts
│   ├── sanity/basic.sh        # Example sanity test
│   ├── smoke/quick.sh         # Example smoke test
│   ├── unit/                  # Unit test modules
│   ├── integration/           # Integration tests
│   ├── e2e/                   # End-to-end tests
│   ├── uat/                   # User acceptance tests
│   ├── chaos/                 # Chaos engineering tests
│   ├── bench/                 # Benchmark tests
│   └── _adhoc/demo.sh         # Adhoc test example
├── README.md                  # Test documentation
└── .gitignore                 # Test-specific ignore patterns
```

**Examples:**
```bash
./gitsim.sh template testsh              # In current directory
./gitsim.sh template testsh myproject    # Create ./myproject/
./gitsim.sh template test-suite api      # Using alias
```

#### TESTSH Template Usage

**Running Tests:**
```bash
cd myproject

# List all available test categories and counts
./testsim.sh list

# Run all test categories in sequence
./testsim.sh run

# Run specific category
./testsim.sh run sanity
./testsim.sh run e2e
./testsim.sh run adhoc
```

**Bootstrapping Language-Specific Tests:**
```bash
# Auto-detect project language and generate tests
./testsim.sh bootstrap

# Generate tests for specific language
./testsim.sh bootstrap rust     # Creates .rs test files
./testsim.sh bootstrap node     # Creates .js test files
./testsim.sh bootstrap python   # Creates .py test files
./testsim.sh bootstrap bash     # Creates .sh test files
```

**Multi-Language Support:**
The bootstrap system automatically detects project type:
- **Rust**: Looks for `Cargo.toml` → generates `.rs` test files
- **Node.js**: Looks for `package.json` → generates `.js` test files
- **Python**: Looks for `.py`, `setup.py`, `requirements.txt` → generates `.py` test files
- **Bash**: Looks for `.sh`, `build.sh` → generates `.sh` test files
- **Generic**: Falls back to `.txt` placeholder files

**Test File Examples Generated:**
```rust
// tests/sanity/example.rs (Rust)
#[test]
fn sanity_example() {
    assert!(true);
}
```

```javascript
// tests/uat/example.js (Node.js)
describe('UAT Tests', () => {
    it('should pass basic UAT check', () => {
        expect(true).toBe(true);
    });
});
```

```python
# tests/unit/example.py (Python)
import unittest

class UnitTests(unittest.TestCase):
    def test_unit_example(self):
        self.assertTrue(True)
```

#### Enhanced Bash Template with TESTSH

**Template with TESTSH Integration:**
```bash
./gitsim.sh template bash myproject --testsh
```

This creates a BashFX project with full TESTSH integration:
- Standard BashFX build system (`parts/`, `build.sh`)
- TESTSH test runner (`testsim.sh` instead of `test_runner.sh`)
- Full test category structure
- Bootstrap script for generating tests
- Integrated build and test workflow

**Workflow Example:**
```bash
./gitsim.sh template bash calculator --testsh
cd calculator

# Build the project
./build.sh build

# Run all tests
./testsim.sh run

# Add custom tests
./testsim.sh bootstrap bash
./testsim.sh run unit
```

### Test Data Generation

#### `noise [count]`
Generate random test files and stage them.

**Arguments:**
- `count` - Number of files to generate (default: 3)

**Examples:**
```bash
./gitsim.sh noise      # Generate 3 random files
./gitsim.sh noise 10   # Generate 10 random files
```

### Configuration Management

#### `rcgen [options]`
Generate GitSim configuration file.

**Options:**
- `--force` - Overwrite existing configuration

**Generated config location:** `~/.local/etc/gitsim/.gitsimrc`

**Examples:**
```bash
./gitsim.sh rcgen          # Generate default config
./gitsim.sh rcgen --force  # Overwrite existing
```

#### `cleanup [options]`
Clean up all GitSim artifacts from current directory.

**Options:**
- `--force` - Skip confirmation prompts

**Examples:**
```bash
./gitsim.sh cleanup         # Interactive cleanup
./gitsim.sh cleanup --force # Force cleanup
```

### System Management

#### `install`
Install GitSim to XDG+ system directories.

**Installs to:**
- Binary: `~/.local/bin/fx/gitsim`
- Library: `~/.local/lib/fx/gitsim/`
- Config: `~/.local/etc/gitsim/`

**Examples:**
```bash
./gitsim.sh install
```

#### `uninstall --force`
Remove GitSim installation completely.

**Options:**
- `--force` - Required flag for safety

**Examples:**
```bash
./gitsim.sh uninstall --force
```

#### `version` / `help` (Enhanced in v2.1.2)
Show version information or comprehensive help.

**Version Command:**
```bash
./gitsim.sh version         # Full version info
./gitsim.sh -v              # Short form
./gitsim.sh --version       # Long form
# Output: gitsim v2.1.2
```

**Help Command:**
```bash
./gitsim.sh help            # Show comprehensive command help
./gitsim.sh -h              # Short form
./gitsim.sh --help          # Long form
./gitsim.sh template --help # Command-specific help
```

## 🔧 Global Options

These options work with any command:

| Option | Description |
|--------|-------------|
| `-d, --debug` | Enable debug output |
| `-t, --trace` | Enable trace output (implies --debug) |
| `-q, --quiet` | Suppress all output except errors |
| `-f, --force` | Force operations, bypass safety checks |
| `-y, --yes` | Auto-confirm prompts |
| `-D, --dev` | Enable developer mode |
| `-h, --help` | Show command help |

**Examples:**
```bash
./gitsim.sh --debug init
./gitsim.sh --quiet --force cleanup
./gitsim.sh --trace template rust myapp
```

## 🌍 Environment Variables

GitSim respects and can override these environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `SIM_HOME` | `$XDG_HOME` or `$HOME` | Base simulated home directory |
| `SIM_USER` | `$USER` or "testuser" | Simulated username |
| `SIM_SHELL` | `$SHELL` or "/bin/bash" | Simulated shell |
| `SIM_EDITOR` | `$EDITOR` or "nano" | Simulated editor |
| `SIM_LANG` | `$LANG` or "en_US.UTF-8" | Simulated locale |

**XDG+ Variables (Advanced):**
- `XDG_HOME` - Base for all local files (default: `~/.local`)
- `XDG_LIB_HOME` - Library files (default: `$XDG_HOME/lib`)
- `XDG_BIN_HOME` - Binary files (default: `$XDG_HOME/bin`)
- `XDG_ETC_HOME` - Configuration files (default: `$XDG_HOME/etc`)

## 📝 Usage Examples

### Professional Test Suite Development (NEW!)

#### Creating Comprehensive Test Infrastructure
```bash
# Create a standalone test suite for existing project
./gitsim.sh template testsh
./testsim.sh list                    # See available test categories

# Bootstrap tests for your language
./testsim.sh bootstrap rust          # Generate Rust test files
./testsim.sh run sanity             # Run sanity checks
./testsim.sh run                    # Run all test categories
```

#### Multi-Language Testing Workflows
```bash
# Python project with comprehensive testing
./gitsim.sh template testsh ml-pipeline
cd ml-pipeline
./testsim.sh bootstrap python

# Run progressive test suite
./testsim.sh run sanity             # Quick validation
./testsim.sh run unit               # Component tests
./testsim.sh run integration        # Integration tests
./testsim.sh run e2e               # End-to-end tests
./testsim.sh clean                 # Clean test artifacts
```

#### BashFX + TESTSH Integration
```bash
# Create professional bash project with testing
./gitsim.sh template bash deploy-tools --testsh
cd deploy-tools

# Development workflow
./build.sh build               # Build from parts/
./testsim.sh run sanity           # Quick health check
./testsim.sh bootstrap bash       # Generate bash tests
./testsim.sh run                  # Full test suite
```

#### Advanced Testing Scenarios
```bash
# Chaos engineering and benchmark testing
./gitsim.sh template testsh performance-suite
cd performance-suite

./testsim.sh run chaos           # Chaos engineering tests
./testsim.sh run bench           # Performance benchmarks
./testsim.sh run uat            # User acceptance tests
```

### Testing Deployment Scripts
```bash
# Create realistic Rust project for testing
./gitsim.sh home-init webapp --template=rust
PROJECT_DIR=$(./gitsim.sh home-path)/projects/webapp

# Test your deployment script
cd "$PROJECT_DIR"
your-deploy-script.sh  # Tests against real Cargo.toml, etc.

# Clean up when done
./gitsim.sh cleanup --force
```

### CI/CD Pipeline Testing
```bash
# Simulate a development workflow
./gitsim.sh init --template=node
echo 'console.log("Hello CI");' > src/app.js
./gitsim.sh add .
./gitsim.sh commit -m "Add app logic"

# Test your CI scripts
your-ci-script.sh

# Generate test data
./gitsim.sh noise 20
./gitsim.sh commit -m "Add test data"
```

### Dotfile Manager Testing
```bash
# Create simulated home environment
./gitsim.sh home-init
HOME_PATH=$(./gitsim.sh home-path)

# Test dotfile installation
HOME="$HOME_PATH" your-dotfile-installer.sh

# Verify results
./gitsim.sh home-ls -la .config
```

### Multi-Project Development Environment
```bash
# Set up multiple projects
./gitsim.sh template rust backend
./gitsim.sh template node frontend
./gitsim.sh template python ml-service

# Each has realistic project structure
ls backend/src/     # main.rs, lib.rs
ls frontend/src/    # index.js
ls ml-service/src/  # Python package structure
```

## 🏗️ Development & Architecture

GitSim is built using the BashFX 2.1 architecture for maintainability and scalability, now enhanced with professional testing infrastructure.

### Enhanced Build System (v2.1.2)
```bash
# Build from modular parts
./build.sh build    # Concatenate parts into gitsim.sh
./build.sh clean    # Remove build artifacts

# Enhanced development workflow with TESTSH
./bin/testsim.sh run    # Run TESTSH-compliant test suite
./bin/build.sh       # Modular build scripts
./build.sh build && ./bin/testsim.sh run  # Build and test
```

### Updated Project Structure (v2.1.2)
```
fx-gitsim/
├── gitsim.sh           # Built script (generated, dynamic version)
├── build.sh            # BashFX build system
├── bin/                # NEW: Build and test utilities
│   ├── testsim.sh         # TESTSH-compliant test runner
│   └── build.sh        # Modular build scripts
├── parts/              # Modular source code (18 parts)
│   ├── build.map       # Build order specification
│   ├── part_01_header.sh
│   ├── part_02_config.sh
│   ├── part_13_template_system.sh
│   ├── part_18_templates_testsh.sh  # NEW: TESTSH template
│   ├── ...
│   └── part_99_main.sh
├── tests/              # Test infrastructure
│   ├── unit/           # Unit tests
│   ├── sanity/         # Sanity checks
│   ├── smoke/          # Smoke tests
│   └── _adhoc/         # Adhoc tests
└── docs/               # Documentation
    ├── gitsim_prd.md   # Product requirements
    ├── ref_template_system.md
    └── ...
```

### Architecture Improvements (v2.1.2)
- **Dynamic Version System**: Version extracted from semv metadata automatically
- **TESTSH Integration**: Professional testing framework with 8 test categories
- **Enhanced Template System**: Multi-language support with bootstrap capabilities
- **Improved Installation**: Handles upgrades and XDG directory management
- **Better CLI**: Comprehensive help system and improved command handling

### Function Ordinality (BashFX Pattern)
- **High-Ordinal**: `do_*` functions (dispatchable commands)
- **Mid-Ordinal**: `_*` functions (orchestration logic)
- **Low-Ordinal**: `__*` functions (literal operations)

### Contributing (Updated Workflow)
1. Edit files in `parts/`, not `gitsim.sh` directly
2. Follow BashFX function ordinality patterns
3. Add tests using TESTSH categories (unit, sanity, smoke, etc.)
4. Update documentation in README.md
5. Test workflow: `./build.sh build && ./bin/testsim.sh run`
6. Use `semv` for version management (no manual version updates)

## 🔒 Safety & Isolation

GitSim is designed to be completely safe:

- **No Pollution**: All artifacts contained in `.gitsim/` directories
- **Safe Defaults**: Confirms before destructive operations
- **XDG Compliance**: Respects user directory standards
- **Easy Cleanup**: `cleanup --force` removes everything
- **Isolated Environments**: No interference with real git repositories

## 🚨 Troubleshooting

### Common Issues

**"Not in a GitSim directory"**
```bash
# Initialize first
./gitsim.sh init
```

**"Template not found"**
```bash
# Check available templates
./gitsim.sh template-list
```

**Permission denied during install**
```bash
# Ensure ~/.local exists
mkdir -p ~/.local/{bin,lib,etc}
./gitsim.sh install
```

**Build fails**
```bash
# Clean and rebuild
./build.sh clean
./build.sh build
```

### Debug Mode
```bash
# Enable detailed logging
./gitsim.sh --trace --debug init
```

## 📄 License

MIT License - See repository for full details.
