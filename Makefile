# ─────────────────────────────────────────────────────────────────────────────
# Makefile for AirSense ML
# ─────────────────────────────────────────────────────────────────────────────
VENV := .venv
UV   := uv
PYTHON_VERSION := $(shell if [ -f .python-version ]; then cat .python-version; else echo "3.12"; fi)
IMAGE_NAME := airsense-ml
DOCKER_HUB_USER := chitrank2050
DOCKER_HUB_IMAGE := $(DOCKER_HUB_USER)/$(IMAGE_NAME)
API_DEPLOYMENT_PLATFORM := Railway
APP_ENV = dev

.DEFAULT_GOAL := help
.PHONY: help init install dev train tune mlflow api \
        docker docker-run _docker-build _docker-run _docker-stop _docker-logs _docker-shell _docker-clean _docker-clean-build _docker-push _docker-deploy \
        lint format tree python-version obliviate \
				git _changelog _changelog-preview _changelog-since _git-tag _git-release \
				docs _docs-build _docs-deploy _docs \
				db _db-migrate _db-migration _db-rollback \
				test airflow _airflow-up _airflow-down _airflow-logs clean clean-all

# ─────────────────────────────────────────────────────────────────────────────
# Help
# ─────────────────────────────────────────────────────────────────────────────
help:
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  AirSense ML"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "Setup:"
	@echo "  make init           - Create virtual environment"
	@echo "  make install        - Install all dependencies"
	@echo "  make install-prod   - Install production dependencies only (Lightweight)"
	@echo ""
	@echo "ML Pipeline:"
	@echo "  make dev            - Run full pipeline"
	@echo "  make train          - Train all 7 models locally"
	@echo "  make train-prod     - Train memory-optimized production models"
	@echo "  make tune           - Hyperparameter tuning (Optuna)"
	@echo "  make mlflow         - Start MLflow UI"
	@echo ""
	@echo "API:"
	@echo "  make api            - Start FastAPI server"
	@echo ""
	@echo "Interactive Menus:"
	@echo "  make docker         - Manage Docker containers & images"
	@echo "  make airflow        - Manage Airflow orchestration"
	@echo "  make docs           - Manage & deploy MkDocs documentation"
	@echo "  make git            - Generate changelogs & releases"
	@echo "  make db             - Manage Alembic database migrations"
	@echo "  make obliviate      - Interactive clean menu"
	@echo ""
	@echo "Code Quality & Testing:"
	@echo "  make lint           - Ruff check"
	@echo "  make format         - Ruff format"
	@echo "  make test           - Run pytest suite"
	@echo ""
	@echo "Maintenance:"
	@echo "  make tree           - Print project structure"
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

train-prod:
	@echo "🤖 Running production training pipeline..."
	$(UV) run python -m src.models.train --config configs/model_config.prod.yaml

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
	@APP_ENV=$(APP_ENV) $(UV) run python -m api.app

# ─────────────────────────────────────────────────────────────────────────────
# Docker
# ─────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
# Docker
# ─────────────────────────────────────────────────────────────────────────────
docker:
	$(UV) run --with questionary scripts/menu.py docker

_docker-build:
	@echo "🐳 Building Docker image: $(IMAGE_NAME)..."
	@docker build --platform linux/amd64 -t $(IMAGE_NAME) .
	@echo "✅ Build complete. Image size:"
	@docker images $(IMAGE_NAME) --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
	@echo "🚀 Run 'make docker-run' to start."

_docker-run:
	@echo "🐳 Starting the unified stack (API + Airflow + DB)..."
	@AIRFLOW_UID=$$(id -u) docker compose up -d
	@echo "✅ Stack is up."
	@echo "   API:     http://localhost:8000"
	@echo "   Airflow: http://localhost:8080"

_docker-stop:
	@echo "🐳 Stopping the unified stack..."
	@AIRFLOW_UID=$$(id -u) docker compose down
	@echo "✅ Container stopped and removed."

_docker-logs:
	@echo "📋 Tailing logs for: $(IMAGE_NAME)..."
	@docker logs -f $(IMAGE_NAME)

_docker-shell:
	@echo "🐚 Opening shell in: $(IMAGE_NAME)..."
	@docker exec -it $(IMAGE_NAME) /bin/bash

_docker-clean:
	@echo "🧹 Pruning Docker system..."
	@docker system prune -a -f --volumes
	@echo "✅ Docker system cleaned."

_docker-clean-build:
	@make _docker-stop
	@make _docker-clean
	@make _docker-build

_docker-push:
	@echo "🐳 Pushing image to Docker Hub..."
	@docker tag $(IMAGE_NAME) $(DOCKER_HUB_IMAGE):latest
	@docker tag $(IMAGE_NAME) $(DOCKER_HUB_IMAGE):v$(shell grep '^version' pyproject.toml | head -1 | tr -d '"' | tr -d ' ' | cut -d'=' -f2)
	@docker push $(DOCKER_HUB_IMAGE):latest
	@docker push $(DOCKER_HUB_IMAGE):v$(shell grep '^version' pyproject.toml | head -1 | tr -d '"' | tr -d ' ' | cut -d'=' -f2)
	@echo "✅ Pushed — $(DOCKER_HUB_IMAGE):latest"

_docker-deploy:
	@echo "🚀 Building and deploying..."
	@$(MAKE) _docker-clean-build
	@$(MAKE) _docker-push
	@echo "✅ Deployed — $(API_DEPLOYMENT_PLATFORM) will pull latest automatically"

# ─────────────────────────────────────────────────────────────────────────────
# Code Quality
# ─────────────────────────────────────────────────────────────────────────────
lint:
	@echo "🔍 Checking code quality..."
	$(UV) run --no-sync ruff check . --fix

format:
	@echo "✨ Formatting code..."
	$(UV) run --no-sync ruff format .

# ─────────────────────────────────────────────────────────────────────────────
# Testing
# ─────────────────────────────────────────────────────────────────────────────
test:
	@echo "🧪 Running test suite..."
	$(UV) run pytest

# ─────────────────────────────────────────────────────────────────────────────
# Airflow Orchestration
# ─────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
# Airflow Orchestration
# ─────────────────────────────────────────────────────────────────────────────
airflow:
	$(UV) run --with questionary scripts/menu.py airflow

_airflow-up:
	@echo "🌬️  Starting Airflow cluster..."
	@AIRFLOW_UID=$$(id -u) docker compose up -d
	@echo "✅ Airflow is running at http://localhost:8080"
	@echo "   User: admin | Pass: admin"

_airflow-down:
	@echo "🌬️  Stopping Airflow cluster..."
	@AIRFLOW_UID=$$(id -u) docker compose down -v

_airflow-logs:
	@echo "📋 Tailing Airflow logs..."
	@AIRFLOW_UID=$$(id -u) docker compose logs -f

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

# ─────────────────────────────────────────────────────────────────────────────
# Git Command
# ─────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
# Git Command
# ─────────────────────────────────────────────────────────────────────────────
git:
	$(UV) run --with questionary scripts/menu.py git

_changelog:
	@echo "📝 Generating changelog..."
	@$(UV) run git-cliff --output CHANGELOG.md
	@git add CHANGELOG.md
	@git diff --cached --quiet || git commit --no-verify -m "docs: update changelog"
	@git push
	@echo "✅ Changelog updated."

_changelog-preview:
	@echo "📝 Preview unreleased changes..."
	@$(UV) run git-cliff --unreleased --strip all

_changelog-since:
	@read -p "Since tag (e.g. v0.1.0): " tag; \
	echo "📝 Changelog since $$tag..."; \
	$(UV) run git-cliff "$$tag"..HEAD --strip all


_git-tag:
	@VERSION=$$(grep '^version' pyproject.toml | head -1 | tr -d '"' | tr -d ' ' | cut -d'=' -f2); \
	echo "🏷️  Tagging v$$VERSION..."; \
	git tag "v$$VERSION" -m "Release v$$VERSION"; \
	git push --tags; \
	echo "✅ Tagged v$$VERSION"

_git-release:
	@VERSION=$$(grep '^version' pyproject.toml | head -1 | tr -d '"' | tr -d ' ' | cut -d'=' -f2); \
	echo "📦 Releasing v$$VERSION..."; \
	$(UV) run git-cliff --output CHANGELOG.md; \
	git add CHANGELOG.md; \
	git diff --cached --quiet || git commit --no-verify -m "docs: update changelog for v$$VERSION"; \
	git push; \
	NOTES=$$($(UV) run git-cliff --latest --strip all 2>/dev/null); \
	gh release edit "v$$VERSION" \
		--title "v$$VERSION" \
		--notes "$$NOTES" 2>/dev/null || \
	gh release create "v$$VERSION" \
		--title "v$$VERSION" \
		--notes "$$NOTES"; \
	echo "✅ Released v$$VERSION"; \
	echo "   https://github.com/chitrank2050/airsense-ml/releases/tag/v$$VERSION"

# ─────────────────────────────────────────────────────────────────────────────
# Docs
# ─────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
# Docs
# ─────────────────────────────────────────────────────────────────────────────
docs:
	$(UV) run --with questionary scripts/menu.py docs

_docs:
	@echo "📚 Starting MkDocs server..."
	@cp CHANGELOG.md docs/changelog.md
	@$(UV) run mkdocs serve

_docs-build:
	@echo "📚 Building docs site..."
	@cp CHANGELOG.md docs/changelog.md
	@$(UV) run mkdocs build
	@echo "✅ Docs built in site/"

_docs-deploy:
	@echo "📚 Deploying to GitHub Pages..."
	@cp CHANGELOG.md docs/changelog.md
	@$(UV) run mkdocs gh-deploy --force
	@echo "✅ Deployed to https://chitrank2050.github.io/airsense-ml"

# ─────────────────────────────────────────────────────────────────────────────
# Database
# ─────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
# Database
# ─────────────────────────────────────────────────────────────────────────────
db:
	$(UV) run --with questionary scripts/menu.py db

_db-migrate:
	@echo "🗄️  Running database migrations..."
	$(UV) run alembic upgrade head
	@echo "✅ Migrations complete."

_db-migration:
	@read -p "Migration name: " name; \
	echo "🗄️  Creating migration: $$name..."; \
	$(UV) run alembic revision --autogenerate -m "$$name"; \
	echo "✅ Migration created."

_db-rollback:
	@echo "🗄️  Rolling back last migration..."
	@$(UV) run alembic downgrade -1
	@echo "✅ Rolled back."