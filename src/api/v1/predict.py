"""src/api/v1/predict.py

Prediction endpoints for the AirSense ML API.

Exposes single and batch AQI prediction over HTTP. Both endpoints
delegate inference to AQIPredictor via PredictionAdapter — routes
contain no ML logic.

Responsibility: handle HTTP request/response cycle for predictions.
Does NOT: run inference directly, load models, or transform features.

Endpoints:
    POST /v1/predict          — single AQI prediction
    POST /v1/predict/batch    — up to 100 predictions per call
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.batch import BatchPredictionRequest, BatchPredictionResponse
from src.api.schemas.prediction import PredictionRequest, PredictionResponse
from src.core.logger import logger
from src.db.connection import get_db
from src.db.models import PredictionLog

router = APIRouter()


@router.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Predict AQI for a single location and time",
    description=(
        "Predicts Air Quality Index from weather and location features. "
        "Returns AQI on the official CPCB India 0-500 scale with category label."
    ),
)
async def predict(
    request: Request,
    body: PredictionRequest,
    db: AsyncSession = Depends(get_db),
) -> PredictionResponse:
    """Predict AQI for a single input.

    Validates the request via Pydantic, delegates to AQIPredictor,
    and returns a typed PredictionResponse.

    Args:
        request: FastAPI request — used to access app.state.predictor.
        body: Validated PredictionRequest from the request body.

    Returns:
        PredictionResponse with predicted AQI, category, and metadata.

    Raises:
        HTTPException: 503 if model is not loaded.
        HTTPException: 422 if request body fails Pydantic validation.
        HTTPException: 500 if inference fails unexpectedly.

    Example:
        POST /v1/predict
        {"station": "IGI Airport", "season": "Winter", ...}
        → {"aqi_predicted": 187.43, "category": "Unhealthy", ...}
    """
    if request.app.state.predictor is None:
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded. Run 'make train' and restart the API.",
        )

    try:
        response, engineered = request.app.state.predictor.predict(body)

        # Log prediction to database
        log = PredictionLog(
            model_version=response.model_version,
            station=body.station,
            season=body.season,
            latitude=body.latitude,
            longitude=body.longitude,
            temperature=body.temperature,
            humidity=body.humidity,
            wind_speed=body.wind_speed,
            visibility=body.visibility,
            day=body.day,
            month=body.month,
            hour=body.hour,
            day_of_week=body.day_of_week,
            is_weekend=body.is_weekend,
            aqi_predicted=response.aqi_predicted,
            aqi_rounded=response.aqi_rounded,
            category=response.category,
            **engineered,
        )
        db.add(log)
        await db.commit()

        logger.info(
            f"Prediction — station: {body.station} "
            f"AQI: {response.aqi_rounded} "
            f"category: {response.category}"
        )
        return response
    except Exception as e:
        logger.error(f"Inference failed: {e}")
        raise HTTPException(status_code=500, detail="Inference failed.") from e


@router.post(
    "/predict/batch",
    response_model=BatchPredictionResponse,
    summary="Predict AQI for multiple locations and times",
    description=(
        "Accepts up to 100 prediction requests in a single call. "
        "Returns predictions in the same order as inputs."
    ),
)
async def predict_batch(
    request: Request,
    body: BatchPredictionRequest,
) -> BatchPredictionResponse:
    """Predict AQI for multiple inputs in a single call.

    Runs predictions sequentially — each input goes through the same
    pipeline as the single predict endpoint. Order is preserved.

    Args:
        request: FastAPI request — used to access app.state.predictor.
        body: Validated BatchPredictionRequest with 1-100 requests.

    Returns:
        BatchPredictionResponse with ordered predictions and count.

    Raises:
        HTTPException: 503 if model is not loaded.
        HTTPException: 500 if any inference fails.

    Example:
        POST /v1/predict/batch
        {"requests": [{...}, {...}]}
        → {"predictions": [{...}, {...}], "count": 2}
    """
    if request.app.state.predictor is None:
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded. Run 'make train' and restart the API.",
        )

    try:
        predictions = [
            request.app.state.predictor.predict(req) for req in body.requests
        ]
        logger.info(f"Batch prediction — count: {len(predictions)}")
        return BatchPredictionResponse(
            predictions=predictions,
            count=len(predictions),
        )
    except Exception as e:
        logger.error(f"Batch inference failed: {e}")
        raise HTTPException(status_code=500, detail="Batch inference failed.") from e
