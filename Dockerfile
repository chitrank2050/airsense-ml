# ─────────────────────────────────────────────────────────────────────────────
# AirSense ML — Optimised Production Dockerfile
#
# Multi-stage build targeting minimum runtime image size.
#
# Stage 1 (builder)  — installs all dependencies, never ships to prod
# Stage 2 (runtime)  — copies only .venv + app code + model artifact
#
# Base image: python:3.12-slim-bookworm
#   Alpine rejected — musl libc breaks numpy/sklearn/lightgbm wheel builds
#   slim-bookworm is the smallest glibc-based image that works with ML stack
#
# Final image target: ~500-600MB
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: Builder ──────────────────────────────────────────────────────────
FROM python:3.12-slim-bookworm AS builder

# Install build-time system dependencies only
# libgomp1  — OpenMP runtime for LightGBM (also needed at runtime)
# gcc       — compiles C extensions during pip install
# git       — some packages reference git during install
# No curl, wget, or other unnecessary tools
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  libgomp1 \
  gcc \
  git \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install uv from official image — pinned version for reproducibility
COPY --from=ghcr.io/astral-sh/uv:0.6.6 /uv /usr/local/bin/uv

# Configure uv for Docker
# UV_COMPILE_BYTECODE  — pre-compiles .pyc files at build time, faster startup
# UV_LINK_MODE=copy    — copy files instead of symlinks (required in containers)
ENV UV_COMPILE_BYTECODE=1 \
  UV_LINK_MODE=copy \
  UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Install dependencies first — separate from code copy for layer caching
# This layer only rebuilds when pyproject.toml or uv.lock changes
COPY pyproject.toml uv.lock ./
COPY README.md ./
COPY LICENCE ./
RUN uv sync \
  --frozen \
  --no-dev \
  --no-group training \
  --no-install-project \
  --no-editable

# Install production dependencies only — no training, no dev tools
COPY src/ ./src/
RUN uv sync \
  --frozen \
  --no-dev \
  --no-group training \
  --no-editable

# XGBoost ships CUDA libraries by default. Force CPU-only build in the Dockerfile:
ENV XGBOOST_BUILD_CUDA=0

# ── Strip GPU libraries — CPU-only inference ──────────────────────────────────
# XGBoost pulls nvidia CUDA packages as transitive dependencies.
# These are 385MB of GPU libraries with zero value on a CPU container.
RUN /app/.venv/bin/pip uninstall -y \
  nvidia-cublas-cu12 \
  nvidia-cuda-cupti-cu12 \
  nvidia-cuda-nvrtc-cu12 \
  nvidia-cuda-runtime-cu12 \
  nvidia-cudnn-cu12 \
  nvidia-cufft-cu12 \
  nvidia-curand-cu12 \
  nvidia-cusolver-cu12 \
  nvidia-cusparse-cu12 \
  nvidia-nccl-cu12 \
  nvidia-nvjitlink-cu12 \
  nvidia-nvtx-cu12 \
  2>/dev/null || true

# ── Stage 2: Runtime ──────────────────────────────────────────────────────────
FROM python:3.12-slim-bookworm AS runtime

# Runtime system dependencies only — no gcc, no git
# libgomp1  — LightGBM requires OpenMP at inference time
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  libgomp1 \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Non-root user — security best practice, required by some platforms
RUN useradd --create-home --no-log-init --shell /bin/bash appuser

WORKDIR /app

# Copy virtual environment from builder — all packages, no build tools
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy only what the runtime needs — nothing else
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser configs/ ./configs/
COPY --chown=appuser:appuser models/best_model.pkl ./models/best_model.pkl

# Runtime environment
# PATH          — makes .venv binaries available without activation
# PYTHONPATH    — makes src/ importable as a package
# PYTHONUNBUFFERED   — stdout/stderr not buffered, logs appear immediately
# PYTHONDONTWRITEBYTECODE — don't write .pyc at runtime (already compiled)
# ENV           — triggers .env.prod loading in pydantic-settings
ENV PATH="/app/.venv/bin:$PATH" \
  PYTHONPATH="/app" \
  PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  ENV=prod

USER appuser

EXPOSE 8000

# Health check — used by Docker, Render, and Railway to verify readiness
# start-period=60s — allows model loading time before health checks begin
HEALTHCHECK \
  --interval=30s \
  --timeout=10s \
  --start-period=60s \
  --retries=3 \
  CMD python -c \
  "import urllib.request; urllib.request.urlopen('http://localhost:8000/v1/health')"

CMD ["python", "-m", "src.api.app"]