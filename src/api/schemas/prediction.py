"""
Request and response schemas for single AQI prediction endpoint.

Responsibility: define and validate the shape of POST /v1/predict
requests and responses. Nothing else.
"""

from typing import Literal

from pydantic import BaseModel, Field

SeasonType = Literal["Winter", "Summer", "Monsoon", "Post-Monsoon"]
DayOfWeekType = Literal[
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


class PredictionRequest(BaseModel):
    """Single AQI prediction request.

    All fields mirror raw dataset columns before feature engineering.
    The inference pipeline applies the same transformations as training.

    Example:
        >>> request = PredictionRequest(
        ...     station="IGI Airport",
        ...     season="Winter",
        ...     latitude=28.5562,
        ...     longitude=77.1000,
        ...     temperature=14.5,
        ...     humidity=82.0,
        ...     wind_speed=3.2,
        ...     visibility=2.1,
        ...     day=15,
        ...     month=1,
        ...     hour=8,
        ...     day_of_week="Monday",
        ...     is_weekend=0,
        ... )
    """

    station: str = Field(..., examples=["IGI Airport"])
    season: SeasonType = Field(..., examples=["Winter"])
    latitude: float = Field(..., examples=[28.5562])
    longitude: float = Field(..., examples=[77.1000])
    temperature: float = Field(..., examples=[14.5])
    humidity: float = Field(..., ge=0, le=100, examples=[82.0])
    wind_speed: float = Field(..., ge=0, examples=[3.2])
    visibility: float = Field(..., ge=0, examples=[2.1])
    day: int = Field(..., ge=1, le=31, examples=[15])
    month: int = Field(..., ge=1, le=12, examples=[1])
    hour: int = Field(..., ge=0, le=23, examples=[8])
    day_of_week: DayOfWeekType = Field(..., examples=["Monday"])
    is_weekend: Literal[0, 1] = Field(..., examples=[0])


class PredictionResponse(BaseModel):
    """Single AQI prediction response.

    Returns predicted AQI on the official CPCB India scale (0-500),
    the corresponding category label, model version, and UTC timestamp.

    Example:
        >>> response.aqi_rounded
        187
        >>> response.category
        'Unhealthy'
    """

    aqi_predicted: float = Field(..., description="Raw predicted AQI value")
    aqi_rounded: int = Field(
        ..., description="AQI rounded and clipped to valid 0-500 range"
    )
    category: str = Field(..., description="CPCB AQI category label")
    model_version: str = Field(
        ..., description="Model file stem used for this prediction"
    )
    prediction_timestamp: str = Field(
        ..., description="UTC ISO timestamp of prediction"
    )
