#!/usr/bin/env bash
#
# SEMVX Deployment Script
# Deploys semvx Python package using pip
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Functions
print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}   SEMVX DEPLOYMENT${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "python3 not found in PATH"
        exit 1
    fi

    python_version=$(python3 --version | awk '{print $2}')
    print_success "Python $python_version detected"
}

check_pip() {
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 not found in PATH"
        exit 1
    fi

    print_success "pip3 available"
}

install_editable() {
    print_info "Installing semvx in editable mode (development)"

    cd "$ROOT_DIR"

    # Install in editable mode with dev dependencies
    if pip3 install -e ".[dev]" --user; then
        print_success "Installed semvx in editable mode"
        return 0
    else
        print_error "Failed to install in editable mode"
        return 1
    fi
}

install_regular() {
    print_info "Installing semvx (regular mode)"

    cd "$ROOT_DIR"

    # Regular install
    if pip3 install . --user; then
        print_success "Installed semvx"
        return 0
    else
        print_error "Failed to install semvx"
        return 1
    fi
}

install_pipx() {
    print_info "Installing semvx with pipx (isolated environment)"

    if ! command -v pipx &> /dev/null; then
        print_error "pipx not found. Install with: python3 -m pip install --user pipx"
        return 1
    fi

    cd "$ROOT_DIR"

    # Install with pipx
    if pipx install .; then
        print_success "Installed semvx with pipx"
        return 0
    else
        print_error "Failed to install with pipx"
        return 1
    fi
}

uninstall() {
    print_info "Uninstalling semvx"

    if pip3 uninstall -y semvx 2>/dev/null; then
        print_success "Uninstalled semvx"
    else
        print_info "semvx was not installed"
    fi
}

show_status() {
    echo ""
    print_info "Checking installation status..."

    if command -v semvx &> /dev/null; then
        semvx_path=$(which semvx)
        semvx_version=$(semvx --version 2>&1 || echo "unknown")

        print_success "semvx is installed"
        echo "  Location: $semvx_path"
        echo "  Version:  $semvx_version"

        # Test basic functionality
        if semvx status &> /dev/null; then
            print_success "semvx status command works"
        else
            print_error "semvx status command failed"
        fi
    else
        print_error "semvx not found in PATH"
        echo "  Try adding ~/.local/bin to your PATH:"
        echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    fi
}

print_usage() {
    cat << EOF
Usage: $0 [COMMAND]

Commands:
    install         Install semvx (regular mode)
    dev             Install semvx in editable mode (for development)
    pipx            Install semvx with pipx (isolated environment)
    uninstall       Uninstall semvx
    status          Show installation status
    help            Show this help message

Examples:
    $0 dev          # Install in development mode
    $0 install      # Install for regular use
    $0 pipx         # Install with pipx
    $0 status       # Check if semvx is installed

EOF
}

# Main script
main() {
    print_header
    echo ""

    # Parse command
    COMMAND="${1:-install}"

    case "$COMMAND" in
        install)
            check_python
            check_pip
            install_regular
            show_status
            ;;

        dev|editable)
            check_python
            check_pip
            install_editable
            show_status
            ;;

        pipx)
            check_python
            install_pipx
            show_status
            ;;

        uninstall|remove)
            uninstall
            ;;

        status)
            check_python
            check_pip
            show_status
            ;;

        help|--help|-h)
            print_usage
            ;;

        *)
            print_error "Unknown command: $COMMAND"
            echo ""
            print_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
