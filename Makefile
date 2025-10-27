# SEMVX Makefile for local development and testing
# Uses pyenv Python if available, falls back to system Python

# Python executable detection
PYTHON := $(shell if [ -x ~/.pyenv/shims/python ]; then echo ~/.pyenv/shims/python; else echo python3; fi)
PIP := $(shell if [ -x ~/.pyenv/shims/pip ]; then echo ~/.pyenv/shims/pip; else echo pip3; fi)
PYTEST := $(shell if [ -x ~/.pyenv/shims/pytest ]; then echo ~/.pyenv/shims/pytest; else echo pytest; fi)

# Project directories
SRC_DIR := src
TEST_DIR := tests
COVERAGE_DIR := htmlcov

# Default target
.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help message
	@echo "SEMVX Development Commands"
	@echo "=========================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install      - Install semvx with pipx (globally available)"
	@echo "  make install-dev  - Install only development dependencies"
	@echo "  make uninstall    - Uninstall semvx"
	@echo ""
	@echo "Testing:"
	@echo "  make test         - Run all tests with pytest"
	@echo "  make test-quick   - Run basic tests without pytest (fallback)"
	@echo "  make test-verbose - Run tests with verbose output"
	@echo "  make coverage     - Run tests with coverage report"
	@echo "  make test-unit    - Run only unit tests"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint         - Run ruff linter"
	@echo "  make format       - Format code with black"
	@echo "  make type-check   - Run mypy type checking"
	@echo "  make quality      - Run all quality checks (lint, format check, type check)"
	@echo ""
	@echo "CLI Testing:"
	@echo "  make cli-help     - Show CLI help"
	@echo "  make cli-detect   - Run project detection"
	@echo "  make cli-status   - Show project status"
	@echo "  make cli-test     - Test all CLI commands"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean        - Remove build artifacts and cache"
	@echo "  make clean-all    - Remove everything including coverage reports"
	@echo ""
	@echo "Development:"
	@echo "  make dev          - Install and run basic tests"
	@echo "  make check        - Run all tests and quality checks"

.PHONY: install
install: ## Install package in development mode with all dependencies
	@echo "Installing semvx with pipx (recommended)..."
	@if command -v pipx >/dev/null 2>&1; then \
		pipx install -e . --force; \
		echo "✅ Installation complete. Run 'semvx --version' to verify."; \
	else \
		echo "⚠️  pipx not found. Installing with pip..."; \
		$(PIP) install -e ".[dev]"; \
		echo "✅ Installation complete. Run 'make test' to verify."; \
	fi

.PHONY: install-dev
install-dev: ## Install only development dependencies
	$(PIP) install pytest pytest-cov black mypy ruff

.PHONY: test
test: ## Run all tests with pytest
	$(PYTEST) $(TEST_DIR)/ -v

.PHONY: test-quick
test-quick: ## Run basic tests without pytest (fallback)
	$(PYTHON) tests/run_tests.py

.PHONY: test-verbose
test-verbose: ## Run tests with verbose output
	$(PYTEST) $(TEST_DIR)/ -vv --tb=short

.PHONY: coverage
coverage: ## Run tests with coverage report
	$(PYTEST) $(TEST_DIR)/ -v \
		--cov=$(SRC_DIR)/semvx \
		--cov-report=term-missing \
		--cov-report=html \
		--cov-fail-under=50
	@echo "Coverage report generated in $(COVERAGE_DIR)/index.html"

.PHONY: test-unit
test-unit: ## Run only unit tests
	$(PYTEST) $(TEST_DIR)/unit/ -v

.PHONY: lint
lint: ## Run ruff linter
	ruff check $(SRC_DIR)/ $(TEST_DIR)/

.PHONY: format
format: ## Format code with black
	black $(SRC_DIR)/ $(TEST_DIR)/

.PHONY: format-check
format-check: ## Check formatting without changing files
	black --check $(SRC_DIR)/ $(TEST_DIR)/

.PHONY: type-check
type-check: ## Run mypy type checking
	mypy $(SRC_DIR)/

.PHONY: quality
quality: lint format-check type-check ## Run all quality checks

.PHONY: cli-help
cli-help: ## Show CLI help
	PYTHONPATH=$(SRC_DIR) $(PYTHON) -m semvx.cli.main --help

.PHONY: cli-detect
cli-detect: ## Run project detection
	PYTHONPATH=$(SRC_DIR) $(PYTHON) -m semvx.cli.main detect

.PHONY: cli-status
cli-status: ## Show project status
	PYTHONPATH=$(SRC_DIR) $(PYTHON) -m semvx.cli.main status

.PHONY: cli-version
cli-version: ## Show version details
	PYTHONPATH=$(SRC_DIR) $(PYTHON) -m semvx.cli.main version

.PHONY: cli-bump
cli-bump: ## Test bump command (dry-run)
	@echo "Testing bump commands..."
	@PYTHONPATH=$(SRC_DIR) $(PYTHON) -m semvx.cli.main bump patch --dry-run
	@PYTHONPATH=$(SRC_DIR) $(PYTHON) -m semvx.cli.main bump minor --dry-run
	@PYTHONPATH=$(SRC_DIR) $(PYTHON) -m semvx.cli.main bump major --dry-run

.PHONY: cli-test
cli-test: ## Test all CLI commands
	@echo "Testing CLI commands..."
	@PYTHONPATH=$(SRC_DIR) $(PYTHON) -m semvx.cli.main --version
	@PYTHONPATH=$(SRC_DIR) $(PYTHON) -m semvx.cli.main --help > /dev/null
	@PYTHONPATH=$(SRC_DIR) $(PYTHON) -m semvx.cli.main detect
	@PYTHONPATH=$(SRC_DIR) $(PYTHON) -m semvx.cli.main status
	@PYTHONPATH=$(SRC_DIR) $(PYTHON) -m semvx.cli.main version
	@PYTHONPATH=$(SRC_DIR) $(PYTHON) -m semvx.cli.main bump patch --dry-run > /dev/null
	@echo "✅ All CLI commands working"

.PHONY: clean
clean: ## Remove build artifacts and cache
	rm -rf build/ dist/ *.egg-info/
	rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

.PHONY: clean-all
clean-all: clean ## Remove everything including coverage reports
	rm -rf $(COVERAGE_DIR)/
	rm -rf .coverage

.PHONY: uninstall
uninstall: ## Uninstall semvx
	@if command -v pipx >/dev/null 2>&1; then \
		pipx uninstall semvx; \
		echo "✅ semvx uninstalled"; \
	else \
		$(PIP) uninstall -y semvx; \
		echo "✅ semvx uninstalled"; \
	fi

.PHONY: dev
dev: install test-quick ## Install and run basic tests
	@echo "✅ Development environment ready"

.PHONY: check
check: test quality ## Run all tests and quality checks
	@echo "✅ All checks passed"

# Watch for changes (requires entr)
.PHONY: watch
watch: ## Watch for changes and run tests (requires entr)
	@command -v entr >/dev/null 2>&1 || { echo "entr not installed. Install with: apt install entr"; exit 1; }
	find $(SRC_DIR) $(TEST_DIR) -name "*.py" | entr -c make test-quick