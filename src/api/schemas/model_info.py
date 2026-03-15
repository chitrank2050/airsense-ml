"""
Response schema for the model metadata endpoint.

Responsibility: define and validate the shape of GET /v1/model/info.
Exposes current model version, file paths, and AQI category reference
for API consumers who need to understand the model context.
"""

from pydantic import BaseModel, Field


class ModelInfoResponse(BaseModel):
    """Model metadata response.

    Provides the current model version, file paths, and the official
    CPCB AQI category reference table used for label assignment.

    Example:
        >>> response.model_version
        'best_model'
        >>> response.aqi_categories
        {'0-50': 'Good', '51-100': 'Satisfactory', ...}
    """

    model_version: str = Field(..., description="Model file stem")
    model_path: str = Field(..., description="Absolute path to model artifact")
    dataset_config: str = Field(..., description="Dataset config file used at training")
    aqi_categories: dict[str, str] = Field(
        ..., description="CPCB AQI range to category label mapping"
    )
