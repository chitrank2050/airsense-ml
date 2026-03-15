"""
Health check endpoint for the AirSense ML API.

Used by load balancers, uptime monitors, and deployment platforms
(Render, Railway) to verify the service is running and the model
is loaded. Returns 200 healthy or 200 degraded — never 5xx on health.

Responsibility: report service health status. Nothing else.
Does NOT: run inference, load models, or validate business logic.
"""

from datetime import UTC, datetime

from fastapi import APIRouter, Request

from src.api.schemas.health import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service health check",
    description="Returns service status and model load state. Used by monitoring and load balancers.",
)
async def health(request: Request) -> HealthResponse:
    """Return current service health status.

    Checks whether the AQIPredictor is loaded and ready to serve
    predictions. Returns 'healthy' if model is loaded, 'degraded'
    if the model failed to load at startup.

    Args:
        request: FastAPI request — used to access app.state.predictor.

    Returns:
        HealthResponse with status, model_loaded flag, and UTC timestamp.

    Example:
        GET /v1/health
        → {"status": "healthy", "model_loaded": true, "timestamp": "..."}
    """
    model_loaded = request.app.state.predictor is not None

    return HealthResponse(
        status="healthy" if model_loaded else "degraded",
        model_loaded=model_loaded,
        timestamp=datetime.now(UTC).isoformat(),
    )
