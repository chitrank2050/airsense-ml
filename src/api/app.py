"""
FastAPI application factory for the AirSense ML API.

Creates and configures the FastAPI application instance with lifespan
management, CORS, versioned routing, and OpenAPI metadata.

Responsibility: assemble the application. Nothing else.
Does NOT: define endpoints, run inference, or manage model state.

Usage:
    uvicorn src.api.app:app --reload
    or via Makefile: make api
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1 import router as v1_router
from src.core import api_lifespan

# ─────────────────────────────────────────────────────────────────────────────
# Application factory
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="AirSense ML API",
    description=(
        "Production-grade Air Quality Index prediction API for Delhi. "
        "Predicts AQI and pollution category from weather and location features."
    ),
    version="1.0.0",
    lifespan=api_lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ─────────────────────────────────────────────────────────────────────────────
# Middleware
# ─────────────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,  # ty:ignore[invalid-argument-type] Reason: false positive error by ty
    # Restrict in production — expand only for known frontend origins
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────────────────────
# Routers
# ─────────────────────────────────────────────────────────────────────────────

# Mount v1 — all endpoints live under /v1
app.include_router(v1_router, prefix="/v1")
