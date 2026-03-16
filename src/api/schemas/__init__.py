"""
Public API schema package.
Re-exports all request/response models for convenience.

Consumers can import directly from submodules for clarity,
or from this package for brevity.

    from src.api.schemas import PredictionRequest     # brief
    from src.api.schemas.prediction import PredictionRequest  # explicit
"""

from .batch import BatchPredictionRequest, BatchPredictionResponse
from .health import HealthResponse
from .model_info import ModelInfoResponse
from .monitoring import DriftReportResponse
from .prediction import PredictionRequest, PredictionResponse

__all__ = [
    "BatchPredictionRequest",
    "BatchPredictionResponse",
    "DriftReportResponse",
    "HealthResponse",
    "ModelInfoResponse",
    "PredictionRequest",
    "PredictionResponse",
]
