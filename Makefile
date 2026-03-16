# ─────────────────────────────────────────────────────────────────────────────
# Makefile for AirSense ML
# ─────────────────────────────────────────────────────────────────────────────
VENV := .venv
UV   := uv
PYTHON_VERSION := $(shell if [ -f .python-version ]; then cat .python-version; else echo "3.12"; fi)
IMAGE_NAME := airsense-ml


.DEFAULT_GOAL := help
.PHONY: help init install dev train tune mlflow api \
        docker-build docker-run docker-stop docker-logs docker-shell docker-prune \
        lint format tree python-version obliviate

# ─────────────────────────────────────────────────────────────────────────────
# Help
# ─────────────────────────────────────────────────────────────────────────────
help:
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  AirSense ML Commands"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "Setup:"
	@echo "  make init          - Create virtual environment"
	@echo "  make install       - Install/sync dependencies"
	@echo "  make install-prod  - Install production dependencies"
	@echo ""
	@echo "ML Pipeline:"
	@echo "  make dev           - Run full pipeline (defined under src/main.py)"
	@echo "  make train         - Run full training pipeline"
	@echo "  make tune          - Run hyperparameter tuning (Optuna)"
	@echo "  make mlflow        - Start MLflow UI"
	@echo ""
	@echo "API:"
	@echo "  make api           - Start FastAPI server (dev mode)"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-run    - Run Docker container"
	@echo "  make docker-stop   - Stop Docker container"
	@echo "  make docker-logs   - Tail container logs"
	@echo "  make docker-shell  - Open shell in running container"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint          - Check code with ruff"
	@echo "  make format        - Format code with ruff"
	@echo ""
	@echo "Maintenance:"
	@echo "  make tree          - Print project structure"
	@echo "  make obliviate     - Interactive obliviate menu"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ─────────────────────────────────────────────────────────────────────────────
# Setup
# ─────────────────────────────────────────────────────────────────────────────
init:
	@echo "🚀 Creating virtual environment with Python $(PYTHON_VERSION)..."
	@if [ -d "$(VENV)" ]; then \
		echo "⚠️  Virtual environment already exists."; \
		echo "💡 Run 'make obliviate' first to remove it."; \
		exit 1; \
	fi
	$(UV) venv --python $(PYTHON_VERSION)
	@echo "✅ Done. Run 'make install' next."

install:
	@echo "📥 Installing dependencies..."
	$(UV) sync --all-groups
	@echo "✅ Done. Run 'make train' to start the pipeline."

install-prod:
	@echo "📥 Installing production dependencies..."
	@$(UV) sync --no-dev --no-group training
	@echo "✅ Done. Run 'make train' to start the pipeline."

# ─────────────────────────────────────────────────────────────────────────────
# ML Pipeline
# ─────────────────────────────────────────────────────────────────────────────
dev:
	@echo "🤖 Running full pipeline..."
	$(UV) run python -m src.main

train:
	@echo "🤖 Running training pipeline..."
	$(UV) run python -m src.models.train

tune:
	@echo "🔬 Running hyperparameter tuning..."
	$(UV) run python -m src.models.tune

mlflow:
	@echo "📊 Starting MLflow UI at http://127.0.0.1:5000"
	$(UV) run mlflow ui --backend-store-uri sqlite:///mlruns.db

# ─────────────────────────────────────────────────────────────────────────────
# API
# ─────────────────────────────────────────────────────────────────────────────
api:
	@echo "🚀 Starting API server..."
	$(UV) run python -m src.api.app

# ─────────────────────────────────────────────────────────────────────────────
# Docker
# ─────────────────────────────────────────────────────────────────────────────
docker-build:
	@echo "🐳 Building Docker image: $(IMAGE_NAME)..."
	@docker build -t $(IMAGE_NAME) .
	@echo "✅ Image built. Run 'make docker-run' to start."

docker-run:
	@echo "🐳 Running container: $(IMAGE_NAME)..."
	@docker run -p 8000:8000 --env-file .env.prod --name $(IMAGE_NAME) $(IMAGE_NAME)

docker-stop:
	@echo "🐳 Stopping container: $(IMAGE_NAME)..."
	@docker stop $(IMAGE_NAME) 2>/dev/null || true
	@docker rm $(IMAGE_NAME) 2>/dev/null || true
	@echo "✅ Container stopped and removed."

docker-logs:
	@echo "📋 Tailing logs for: $(IMAGE_NAME)..."
	@docker logs -f $(IMAGE_NAME)

docker-shell:
	@echo "🐚 Opening shell in: $(IMAGE_NAME)..."
	@docker exec -it $(IMAGE_NAME) /bin/bash

docker-prune:
	@echo "🧹 Pruning Docker system..."
	@docker system prune -a -f --volumes
	@echo "✅ Docker system cleaned."

# ─────────────────────────────────────────────────────────────────────────────
# Code Quality
# ─────────────────────────────────────────────────────────────────────────────
lint:
	@echo "🔍 Checking code quality..."
	$(UV) run --no-sync ruff check src/ --fix

format:
	@echo "✨ Formatting code..."
	$(UV) run --no-sync ruff format src/

# ─────────────────────────────────────────────────────────────────────────────
# Maintenance
# ─────────────────────────────────────────────────────────────────────────────
tree:
	@echo "🌳 Project Structure:"
	@find . \
		-not -path './.venv/*' \
		-not -path './.git/*' \
		-not -path '*/__pycache__/*' \
		-not -path './data/raw/*' \
		-not -path './.dvc/*' \
		-not -path './.ruff_cache/*' \
		| sort | sed 's/[^/]*\//  /g'

_clean_mlflow:
	@echo "⚠️  Removing MLflow experiment database (mlruns.db)..."
	@echo "    This will delete ALL experiment history and cannot be undone."
	@rm -f mlruns.db
	@rm -rf mlruns/
	@echo "✅ MLflow data removed"

_clean_cache:
	@echo "🧹 Removing cache files..."
	@ find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@ find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@ find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@ find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@ find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@ find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@ rm -rf site/ 2>/dev/null || true
	@ rm -rf dist/ 2>/dev/null || true
	@ rm -rf .pytest_cache
	@ rm -rf .ruff_cache
	@ rm -rf .mypy_cache
	@ rm -rf .ipynb_checkpoints
	@ rm -rf .coverage
	rm -rf htmlcov
	@echo "✅ Cache cleaned"

_clean_models:
	@echo "🧹 Removing saved model artifacts..."
	@find models/ -name "*.pkl" -delete 2>/dev/null || true
	@find models/ -name "*.pickle" -delete 2>/dev/null || true
	@echo "✅ Model artifacts removed (DVC pointer files preserved)"

_clean_logs:
	@echo "🧹 Removing log files..."
	@rm -rf logs/
	@echo "✅ Log files removed"

_clean_venv:
	@echo "🗑️  Removing virtual environment..."
	@rm -rf $(VENV)
	@echo "✅ Virtual environment removed"
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  To set up again:"
	@echo "  → Run 'make init' to create venv"
	@echo "  → Run 'make install' to install dependencies"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

obliviate:
	$(UV) run --with questionary scripts/menu.py obliviate

python-version:
	@echo "📌 Python version: $(PYTHON_VERSION)"
	@$(UV) python list 2>/dev/null || true