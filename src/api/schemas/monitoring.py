"""
Response schema for monitoring endpoints.
"""

from pydantic import BaseModel, Field


class DriftReportResponse(BaseModel):
    """Drift report summary response."""

    dataset_drift_detected: bool = Field(..., description="True if drift detected")
    drift_score: float = Field(..., description="Proportion of features that drifted")
    n_features_drifted: int = Field(..., description="Number of drifted features")
    n_features_total: int = Field(..., description="Total features monitored")
    n_production_samples: int = Field(..., description="Production samples analysed")
    n_reference_samples: int = Field(..., description="Reference samples used")
