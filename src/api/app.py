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

import sys

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.api.utils.middleware import add_request_id
from src.api.utils.rate_limit import limiter
from src.api.v1 import router as v1_router
from src.core import bootstrap
from src.core.api_lifespan import api_lifespan
from src.core.config import settings
from src.core.logger import logger

# ─────────────────────────────────────────────────────────────────────────────
# Application factory
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=api_lifespan,
    debug=settings.API_DEBUG,
    docs_url=settings.API_DOCS_URL,
    redoc_url=settings.API_REDOC_URL,
    openapi_url=settings.API_OPENAPI_URL,
)

# ─────────────────────────────────────────────────────────────────────────────
# Middleware
# ─────────────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,  # type: ignore[arg-type]
    # Restrict in production — expand only for known frontend origins
    allow_origins=settings.API_ALLOWED_ORIGINS,
    allow_credentials=settings.API_ALLOW_CREDENTIALS,
    allow_methods=settings.API_ALLOWED_METHODS,
    allow_headers=settings.API_ALLOWED_HEADERS,
)


app.middleware("http")(add_request_id)

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,  # type: ignore[arg-type]
)

# ─────────────────────────────────────────────────────────────────────────────
# Routers
# ─────────────────────────────────────────────────────────────────────────────

# Mount v1 — all endpoints live under /v1
app.include_router(v1_router, prefix=settings.API_PREFIX)


def main():
    uvicorn.run(
        "src.api.app:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
    )


if __name__ == "__main__":
    try:
        bootstrap()
        main()
    except KeyboardInterrupt:
        logger.warning("🛑 Application interrupted by user.")
        sys.exit(0)
