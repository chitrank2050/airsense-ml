"""
Public API schema package.
Re-exports all request/response models for convenience.

Consumers can import directly from submodules for clarity,
or from this package for brevity.

    from src.api.schemas import PredictionRequest     # brief
    from src.api.schemas.prediction import PredictionRequest  # explicit
"""

from src.api.schemas.batch import BatchPredictionRequest, BatchPredictionResponse
from src.api.schemas.health import HealthResponse
from src.api.schemas.model_info import ModelInfoResponse
from src.api.schemas.prediction import PredictionRequest, PredictionResponse

__all__ = [
    "BatchPredictionRequest",
    "BatchPredictionResponse",
    "HealthResponse",
    "ModelInfoResponse",
    "PredictionRequest",
    "PredictionResponse",
]
