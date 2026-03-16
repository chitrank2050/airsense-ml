"""
SQLAlchemy ORM models for AirSense ML.

Defines database table schemas for prediction logging and
monitoring. All tables use UUID primary keys for distributed safety.

Responsibility: define table schemas. Nothing else.
Does NOT: run queries, handle business logic, or manage connections.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.db.connection import Base


class PredictionLog(Base):
    """
    Logs every prediction request for drift monitoring.

    Stores both input features and output prediction so Evidently
    can compare production distribution against training distribution.
    """

    __tablename__ = "prediction_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        index=True,
    )
    model_version: Mapped[str] = mapped_column(String(100))

    # Input features
    station: Mapped[str] = mapped_column(String(100))
    season: Mapped[str] = mapped_column(String(50))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    temperature: Mapped[float] = mapped_column(Float)
    humidity: Mapped[float] = mapped_column(Float)
    wind_speed: Mapped[float] = mapped_column(Float)
    visibility: Mapped[float] = mapped_column(Float)
    day: Mapped[int] = mapped_column(Integer)
    month: Mapped[int] = mapped_column(Integer)
    hour: Mapped[int] = mapped_column(Integer)
    day_of_week: Mapped[str] = mapped_column(String(20))
    is_weekend: Mapped[int] = mapped_column(Integer)

    # Output
    aqi_predicted: Mapped[float] = mapped_column(Float)
    aqi_rounded: Mapped[int] = mapped_column(Integer)
    category: Mapped[str] = mapped_column(String(50))


class DriftReport(Base):
    """
    Stores generated Evidently drift reports.

    Records when drift was detected, which features drifted,
    and the overall drift score for trend analysis.
    """

    __tablename__ = "drift_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        index=True,
    )
    dataset_drift_detected: Mapped[bool] = mapped_column(Boolean)
    drift_score: Mapped[float] = mapped_column(Float)
    n_features_drifted: Mapped[int] = mapped_column(Integer)
    n_features_total: Mapped[int] = mapped_column(Integer)
    report_json: Mapped[str] = mapped_column(String)  # full Evidently report as JSON
