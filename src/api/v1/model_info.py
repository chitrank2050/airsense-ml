"""
Model metadata endpoint for the AirSense ML API.

Exposes the current model version, file paths, and the official CPCB
AQI category reference table. Useful for API consumers who need to
understand the model context or display category labels in a UI.

Responsibility: return model metadata. Nothing else.
Does NOT: run inference, modify model state, or expose training metrics.
"""

from fastapi import APIRouter, HTTPException, Request

from src.api.adapters.prediction_adapter import AQI_CATEGORIES
from src.api.schemas.model_info import ModelInfoResponse

router = APIRouter()


@router.get(
    "/model/info",
    response_model=ModelInfoResponse,
    summary="Current model metadata",
    description="Returns model version, file paths, and AQI category reference table.",
)
async def model_info(request: Request) -> ModelInfoResponse:
    """Return metadata about the currently loaded model.

    Reads model version and path from the loaded AQIPredictor instance.
    Returns 503 if the model failed to load at startup.

    Args:
        request: FastAPI request — used to access app.state.predictor.

    Returns:
        ModelInfoResponse with version, paths, and AQI category mapping.

    Raises:
        HTTPException: 503 if model is not loaded.

    Example:
        GET /v1/model/info
        → {"model_version": "best_model", "aqi_categories": {...}}
    """
    if request.app.state.predictor is None:
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded. Run 'make train' and restart the API.",
        )

    predictor = request.app.state.predictor

    # Build human-readable category reference from AQI_CATEGORIES thresholds
    prev = 0
    categories: dict[str, str] = {}
    for threshold, label in AQI_CATEGORIES:
        categories[f"{prev}-{threshold}"] = label
        prev = threshold + 1

    return ModelInfoResponse(
        model_version=predictor.model_version,
        model_path=str(predictor.model_path),
        dataset_config=predictor.dataset_config_path,
        aqi_categories=categories,
    )
