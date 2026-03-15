"""
Adapter between the API schema layer and the inference layer.

Decouples PredictionRequest/PredictionResponse schemas from the
AQIPredictor internals. Any change to the API contract or the
inference pipeline touches only this file — not both layers.

Responsibility: transform API input to predictor input, and
predictor output to API response. Nothing else.
Does NOT: run inference, validate business rules, or define schemas.

Pattern: Adapter (GoF) — converts one interface to another without
modifying either.
"""

from datetime import UTC, datetime

import pandas as pd

from src.api.schemas.prediction import PredictionRequest, PredictionResponse

# Official CPCB India AQI category thresholds
# Source: https://cpcb.nic.in/
AQI_CATEGORIES: list[tuple[int, str]] = [
    (50, "Good"),
    (100, "Satisfactory"),
    (200, "Moderate"),
    (300, "Poor"),
    (400, "Very Poor"),
    (500, "Severe"),
]


def get_aqi_category(aqi: float) -> str:
    """Map a predicted AQI value to the official CPCB category label.

    Args:
        aqi: Predicted AQI value on the 0-500 scale.

    Returns:
        CPCB category label string.

    Example:
        >>> get_aqi_category(187)
        'Unhealthy'
    """
    for threshold, label in AQI_CATEGORIES:
        if aqi <= threshold:
            return label
    return "Severe"


class PredictionAdapter:
    """Adapts between the API schema layer and the AQIPredictor.

    Converts a PredictionRequest into a DataFrame the predictor
    pipeline expects, and converts raw numpy predictions back into
    a typed PredictionResponse.

    This class is stateless — all methods are static. Instantiation
    is not required but allowed for dependency injection in tests.

    Example:
        >>> adapter = PredictionAdapter()
        >>> df = adapter.to_dataframe(request)
        >>> response = adapter.to_response(prediction, model_version)
    """

    @staticmethod
    def to_dataframe(request: PredictionRequest) -> pd.DataFrame:
        """Convert a PredictionRequest to a single-row DataFrame.

        The resulting DataFrame mirrors the raw dataset column structure
        before feature engineering — matching what the training pipeline
        was built on.

        Args:
            request: Validated PredictionRequest from the API layer.

        Returns:
            Single-row DataFrame ready for engineer_base_features().
        """
        return pd.DataFrame([request.model_dump()])

    @staticmethod
    def to_response(
        aqi_predicted: float,
        model_version: str,
    ) -> PredictionResponse:
        """Convert a raw AQI prediction to a typed PredictionResponse.

        Clips the predicted value to the valid 0-500 AQI range,
        assigns the CPCB category label, and attaches metadata.

        Args:
            aqi_predicted: Raw float AQI prediction from the pipeline.
            model_version: Model file stem for traceability.

        Returns:
            Validated PredictionResponse ready to return to the caller.
        """
        # Clip to valid AQI range — model can extrapolate beyond 0-500
        aqi_rounded = max(0, min(500, round(aqi_predicted)))

        return PredictionResponse(
            aqi_predicted=round(aqi_predicted, 2),
            aqi_rounded=aqi_rounded,
            category=get_aqi_category(aqi_predicted),
            model_version=model_version,
            prediction_timestamp=datetime.now(UTC).isoformat(),
        )
