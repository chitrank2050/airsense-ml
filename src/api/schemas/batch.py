"""
Request and response schemas for batch AQI prediction endpoint.

Responsibility: define and validate the shape of POST /v1/predict/batch.
Wraps PredictionRequest and PredictionResponse in list containers.
Does NOT define single prediction logic — see prediction.py.
"""

from pydantic import BaseModel, Field

from src.api.schemas.prediction import PredictionRequest, PredictionResponse


class BatchPredictionRequest(BaseModel):
    """Batch AQI prediction request — multiple inputs in one call.

    Enforces a maximum of 100 requests per call to prevent abuse
    and control inference latency at the API layer.

    Args:
        requests: List of individual PredictionRequest objects.

    Example:
        >>> batch = BatchPredictionRequest(requests=[req1, req2])
        >>> len(batch.requests)
        2
    """

    requests: list[PredictionRequest] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of prediction requests. Maximum 100 per call.",
    )


class BatchPredictionResponse(BaseModel):
    """Batch AQI prediction response.

    Returns predictions in the same order as the input requests.
    count is provided as a convenience field for the caller.

    Args:
        predictions: Ordered list of PredictionResponse objects.
        count: Number of predictions returned, mirrors len(predictions).
    """

    predictions: list[PredictionResponse]
    count: int = Field(..., description="Number of predictions returned")
