# Makefile for Python Project with uv and pyproject.toml

# Variables
VENV := .venv
UV := uv

# Read Python version from .python-version file, fallback to 3.12 if not found
PYTHON_VERSION := $(shell if [ -f .python-version ]; then cat .python-version; else echo "3.12"; fi)

# Default target
.DEFAULT_GOAL := help

# PHONY targets (not actual files)
.PHONY: help init install dev tree lint format build clean obliviate python-version menu _clean_cache _clean_models _clean_venv

# Help - Show available commands
help:
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  Python Project Commands"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make init          - Create virtual environment"
	@echo "  make install       - Install/sync dependencies from pyproject.toml"
	@echo ""
	@echo "Development Commands:"
	@echo "  make dev           - Run app in development mode"
	@echo "  make lint          - Check code quality with ruff"
	@echo "  make format        - Auto-format code with ruff"
	@echo "  make build         - Build distribution package"
	@echo ""
	@echo "Maintenance Commands:"
	@echo "  make clean         - Interactive: choose what to delete (cache, models)"
	@echo "  make obliviate     - Interactive: full reset (clean + venv removal)"
	@echo "  make python-version - Show current Python version"
	@echo ""
	@echo "Interactive Wizard:"
	@echo "  make menu          - Arrow-key menu: init, install, clean, obliviate"
	@echo ""

# Init - Create virtual environment
init:
	@echo "🚀 Creating virtual environment..."
	@if [ -f .python-version ]; then \
		echo "📌 Using Python $(PYTHON_VERSION) from .python-version file"; \
	else \
		echo "📌 Using Python $(PYTHON_VERSION) (default)"; \
		echo "💡 Tip: Create .python-version file to pin a specific version"; \
	fi
	@echo ""
	@if [ -d "$(VENV)" ]; then \
		echo "⚠️  Virtual environment already exists at $(VENV)"; \
		echo "💡 Use 'make obliviate' first to remove it, then run 'make init' again"; \
		exit 1; \
	fi
	@echo "📦 Creating venv with Python $(PYTHON_VERSION)..."
	$(UV) venv --python $(PYTHON_VERSION)
	@echo "✅ Virtual environment created at $(VENV)"
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  Next steps:"
	@echo "  → Run 'make install' to install dependencies"
	@echo "  → Run 'make dev' to start development"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Install - Install/sync dependencies from pyproject.toml
install:
	@if [ ! -d "$(VENV)" ]; then \
		echo "❌ Virtual environment not found!"; \
		echo "Run 'make init' first to create the virtual environment."; \
		exit 1; \
	fi
	@if [ ! -f pyproject.toml ]; then \
		echo "❌ pyproject.toml not found!"; \
		echo "Run 'uv init' to create a project or add pyproject.toml manually."; \
		exit 1; \
	fi
	@echo "📥 Installing dependencies from pyproject.toml..."
	. $(VENV)/bin/activate && $(UV) sync
	@echo "✅ Dependencies installed successfully"

# Dev - Run application in development mode
dev:
	@if [ ! -d "$(VENV)" ]; then \
		echo "❌ Virtual environment not found!"; \
		echo "Run 'make init' first."; \
		exit 1; \
	fi
	@echo "🚀 Starting development server..."
	. $(VENV)/bin/activate && ENV=dev $(UV) run -m src.main

# Lint - Check code quality with ruff
lint:
	@if [ ! -d "$(VENV)" ]; then \
		echo "❌ Virtual environment not found!"; \
		echo "Run 'make init' first."; \
		exit 1; \
	fi
	@if ! . $(VENV)/bin/activate && command -v ruff > /dev/null 2>&1; then \
		echo "❌ ruff not installed!"; \
		echo "Add it to your project:"; \
		echo "  uv add ruff --dev"; \
		exit 1; \
	fi
	@echo "🔍 Checking code quality..."
	. $(VENV)/bin/activate && $(UV) run ruff check app/

# Format - Auto-format code with ruff
format:
	@if [ ! -d "$(VENV)" ]; then \
		echo "❌ Virtual environment not found!"; \
		echo "Run 'make init' first."; \
		exit 1; \
	fi
	@if ! . $(VENV)/bin/activate && command -v ruff > /dev/null 2>&1; then \
		echo "❌ ruff not installed!"; \
		echo "Add it to your project:"; \
		echo "  uv add ruff --dev"; \
		exit 1; \
	fi
	@echo "✨ Formatting code..."
	. $(VENV)/bin/activate && $(UV) run ruff format app/

# Build - Create distribution packages using Hatchling
build:
	@if [ ! -d "$(VENV)" ]; then \
		echo "❌ Virtual environment not found!"; \
		echo "Run 'make init' first."; \
		exit 1; \
	fi
	@if [ ! -f pyproject.toml ]; then \
		echo "❌ pyproject.toml not found!"; \
		exit 1; \
	fi
	@echo "📦 Building distribution packages..."
	. $(VENV)/bin/activate && $(UV) run python -m build
	@echo "✅ Build complete! Check the 'dist/' folder for .whl and .tar.gz files"%

# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers (invoked by the interactive menus below)
# ─────────────────────────────────────────────────────────────────────────────
_clean_cache:
	@echo "🧹 Removing Python cache files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf site/ dist/ .pytest_cache .ruff_cache .mypy_cache .ipynb_checkpoints .coverage htmlcov 2>/dev/null || true
	@echo "✅ Cache cleaned"

_clean_models:
	@echo "🧹 Removing saved models..."
	@rm -rf models/
	@echo "✅ Models removed"

_clean_venv:
	@echo "🗑️  Removing virtual environment..."
	@rm -rf $(VENV)
	@echo "✅ Virtual environment removed"

# ─────────────────────────────────────────────────────────────────────────────
# Clean - Interactive checkbox menu
# ─────────────────────────────────────────────────────────────────────────────
clean:
	@uv run --with questionary scripts/menu.py clean

# ─────────────────────────────────────────────────────────────────────────────
# Obliviate - Interactive full-reset menu
# ─────────────────────────────────────────────────────────────────────────────
obliviate:
	@uv run --with questionary scripts/menu.py obliviate

# ─────────────────────────────────────────────────────────────────────────────
# Menu - Top-level interactive wizard
# ─────────────────────────────────────────────────────────────────────────────
menu:
	@uv run --with questionary scripts/menu.py wizard

# Python-version - Show current Python version
python-version:
	@if [ -f .python-version ]; then \
		echo "📌 Current Python version: $(PYTHON_VERSION) (from .python-version)"; \
	else \
		echo "⚠️  No .python-version file found"; \
		echo "📌 Using default: $(PYTHON_VERSION)"; \
		echo ""; \
		echo "To set a specific version:"; \
		echo "  echo '3.12' > .python-version"; \
		echo "  echo '3.13' > .python-version"; \
	fi
	@echo ""
	@echo "Available Python versions:"
	@$(UV) python list 2>/dev/null || echo "  Run 'uv python list' to see installed versions"