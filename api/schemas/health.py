"""
Response schema for the API health check endpoint.

Responsibility: define and validate the shape of GET /v1/health.
Used by load balancers, uptime monitors, and deployment health checks.
"""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """API health check response.

    status is 'healthy' when the model is loaded and ready to serve.
    status is 'degraded' when the service is running but the model
    failed to load — requests will return 503 in this state.

    Example:
        >>> response.status
        'healthy'
        >>> response.model_loaded
        True
    """

    status: str = Field(..., description="Service status: healthy or degraded")
    model_loaded: bool = Field(
        ..., description="True if model is loaded and ready to serve"
    )
    timestamp: str = Field(..., description="UTC ISO timestamp of health check")
