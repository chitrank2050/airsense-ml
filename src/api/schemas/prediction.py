"""
Request and response schemas for single AQI prediction endpoint.

Responsibility: define and validate the shape of POST /v1/predict
requests and responses. Nothing else.
"""

from pydantic import BaseModel, Field


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

    station: str = Field(
        ..., description="Monitoring station name", examples=["IGI Airport"]
    )
    season: str = Field(..., description="Season name", examples=["Winter"])
    latitude: float = Field(..., description="Station latitude", examples=[28.5562])
    longitude: float = Field(..., description="Station longitude", examples=[77.1000])
    temperature: float = Field(
        ..., description="Temperature in Celsius", examples=[14.5]
    )
    humidity: float = Field(
        ..., ge=0, le=100, description="Relative humidity %", examples=[82.0]
    )
    wind_speed: float = Field(
        ..., ge=0, description="Wind speed in km/h", examples=[3.2]
    )
    visibility: float = Field(..., ge=0, description="Visibility in km", examples=[2.1])
    day: int = Field(..., ge=1, le=31, description="Day of month", examples=[15])
    month: int = Field(..., ge=1, le=12, description="Month number", examples=[1])
    hour: int = Field(..., ge=0, le=23, description="Hour of day 24h", examples=[8])
    day_of_week: str = Field(..., description="Full day name", examples=["Monday"])
    is_weekend: int = Field(
        ..., ge=0, le=1, description="1 if weekend else 0", examples=[0]
    )


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
