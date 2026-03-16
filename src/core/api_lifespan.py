"""
FastAPI lifespan context manager for application startup and shutdown.

Manages initialisation and teardown of shared application resources —
specifically the AQIPredictor instance that must be loaded once at
startup and reused across all requests.

Responsibility: own the lifecycle of shared resources. Nothing else.
Does NOT: define routes, handle requests, or run inference.

Pattern: FastAPI lifespan (replaces deprecated on_event handlers).
The predictor is stored on app.state so all routes access the same
instance without re-loading the model per request.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.db.connection import init_db
from src.models.predict import AQIPredictor

from .logger import logger


@asynccontextmanager
async def api_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown lifecycle.

    Loads the AQIPredictor once at startup and stores it on app.state.
    All v1 routes access the predictor via request.app.state.predictor.

    On shutdown, logs teardown — add cleanup logic here if future
    resources require explicit release (DB connections, thread pools).

    Args:
        app: The FastAPI application instance.

    Yields:
        None — control returns to FastAPI to serve requests.

    Example:
        >>> app = FastAPI(lifespan=lifespan)
    """
    # ── Startup ───────────────────────────────────────────────────────────────
    logger.info("Starting AirSense ML API")

    # Initialise database tables
    # await init_db()
    try:
        await init_db()
    except Exception as e:
        logger.error(f"Database initialisation failed: {e}")
        logger.warning("API starting without database — monitoring disabled")

    try:
        app.state.predictor = AQIPredictor()
        logger.success(f"Model loaded — version: {app.state.predictor.model_version}")
    except FileNotFoundError as e:
        # Allow startup to continue in degraded state — health endpoint
        # will report model_loaded: false so load balancers can detect it
        logger.error(f"Model failed to load: {e}")
        logger.warning("API starting in degraded state — /v1/predict will return 503")
        app.state.predictor = None

    yield

    # ── Shutdown ──────────────────────────────────────────────────────────────
    logger.info("Shutting down AirSense ML API")
