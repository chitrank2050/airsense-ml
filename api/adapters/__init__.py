"""
Adapter layer between the API schema layer and the inference layer.

Decouples API request/response contracts from the ML pipeline internals.
Any change to the API contract or inference pipeline touches only the
relevant adapter — not both layers.

Responsibility: transform between API schemas and predictor interfaces.
Does NOT: define schemas, run inference, or handle routing.

Pattern: Adapter (GoF) — converts one interface to another without
modifying either.

Available adapters:
    PredictionAdapter — adapts PredictionRequest/Response to AQIPredictor
"""

from .prediction_adapter import PredictionAdapter, get_aqi_category

__all__ = [
    "PredictionAdapter",
    "get_aqi_category",
]
