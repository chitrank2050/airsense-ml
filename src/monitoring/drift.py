"""
Evidently drift detection for AirSense ML.

Compares production prediction distribution against training
reference data to detect data drift over time.

Uses Evidently v0.7.x API.

Responsibility: generate drift reports. Nothing else.
Does NOT: log predictions, serve HTTP, or retrain models.
"""

import json
from pathlib import Path

import pandas as pd
from evidently import DataDefinition, Dataset, Report
from evidently.presets import DataDriftPreset
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logger import logger
from src.db.models import DriftReport, PredictionLog
from src.utils.paths import get_model_path

NUMERICAL_FEATURES = [
    "temperature",
    "humidity",
    "wind_speed",
    "visibility",
    "latitude",
    "longitude",
    "day",
    "month",
    "hour",
    "is_weekend",
]

CATEGORICAL_FEATURES = ["station", "season", "day_of_week"]


def save_reference_dataset(X_train: pd.DataFrame, artifact_cfg: dict) -> None:
    """
    Save training feature distribution as reference for Evidently drift detection.
    Called once after training completes — not part of the training loop.

    Args:
        X_train: Training feature dataframe before pipeline transformation.
        artifact_cfg: Artifact config from model_config.yaml.
    """
    model_dir = Path(artifact_cfg["model_dir"])
    reference_path = model_dir / "reference_data.parquet"

    # Save only the features we monitor
    cols_to_save = NUMERICAL_FEATURES + CATEGORICAL_FEATURES
    available_cols = [c for c in cols_to_save if c in X_train.columns]
    X_train[available_cols].to_parquet(reference_path, index=False)
    logger.info(f"Reference dataset saved to {reference_path} ({len(X_train)} rows)")


async def get_production_data(db: AsyncSession, limit: int = 1000) -> pd.DataFrame:
    """
    Fetch recent production predictions from database.

    Args:
        db: Async database session.
        limit: Number of recent predictions to fetch.

    Returns:
        DataFrame of recent production feature values.
    """
    result = await db.execute(
        select(PredictionLog).order_by(PredictionLog.timestamp.desc()).limit(limit)
    )
    logs = result.scalars().all()

    if not logs:
        return pd.DataFrame()

    return pd.DataFrame(
        [
            {
                "temperature": log.temperature,
                "humidity": log.humidity,
                "wind_speed": log.wind_speed,
                "visibility": log.visibility,
                "latitude": log.latitude,
                "longitude": log.longitude,
                "day": log.day,
                "month": log.month,
                "hour": log.hour,
                "is_weekend": log.is_weekend,
                "station": log.station,
                "season": log.season,
                "day_of_week": log.day_of_week,
            }
            for log in logs
        ]
    )


def load_reference_data() -> pd.DataFrame:
    """
    Load training reference dataset saved during make train.

    Returns:
        DataFrame of training feature distribution.

    Raises:
        FileNotFoundError: If reference dataset not found.
    """
    reference_path = get_model_path("reference_data.parquet")
    if not reference_path.exists():
        raise FileNotFoundError(
            f"Reference dataset not found at {reference_path}. "
            "Run 'make train' to generate it."
        )
    return pd.read_parquet(reference_path)


async def generate_drift_report(db: AsyncSession) -> dict:
    """
    Generate Evidently drift report comparing production vs training data.

    Args:
        db: Async database session.

    Returns:
        Dictionary with drift summary and full report JSON.

    Raises:
        ValueError: If insufficient production data for analysis.
    """
    production_df = await get_production_data(db)
    if len(production_df) < 10:
        raise ValueError(
            f"Insufficient production data. "
            f"Need at least 10 predictions, got {len(production_df)}."
        )

    reference_df = load_reference_data()

    # Sample reference to same size as production
    if len(reference_df) > len(production_df):
        reference_df = reference_df.sample(n=len(production_df), random_state=42)

    # Define column types for Evidently v0.7.x
    data_definition = DataDefinition(
        numerical_columns=NUMERICAL_FEATURES,
        categorical_columns=CATEGORICAL_FEATURES,
    )

    # Wrap dataframes in Evidently Dataset
    reference_dataset = Dataset.from_pandas(
        reference_df,
        data_definition=data_definition,
    )
    production_dataset = Dataset.from_pandas(
        production_df,
        data_definition=data_definition,
    )

    # Generate report
    report = Report([DataDriftPreset()])
    result = report.run(
        reference_data=reference_dataset,
        current_data=production_dataset,
    )

    result_dict = result.dict()

    # Extract drift summary
    try:
        drift_metrics = result_dict["metrics"][0]["result"]
        dataset_drift = drift_metrics.get("dataset_drift", False)
        drift_score = drift_metrics.get("drift_share", 0.0)
        n_drifted = drift_metrics.get("number_of_drifted_columns", 0)
        n_total = drift_metrics.get(
            "number_of_columns", len(NUMERICAL_FEATURES + CATEGORICAL_FEATURES)
        )
    except (KeyError, IndexError):
        dataset_drift = False
        drift_score = 0.0
        n_drifted = 0
        n_total = len(NUMERICAL_FEATURES + CATEGORICAL_FEATURES)

    report_json = json.dumps(result_dict, default=str)

    # Save to database
    drift_log = DriftReport(
        dataset_drift_detected=dataset_drift,
        drift_score=drift_score,
        n_features_drifted=n_drifted,
        n_features_total=n_total,
        report_json=report_json,
    )
    db.add(drift_log)
    await db.commit()

    logger.info(
        f"Drift report — detected: {dataset_drift} | "
        f"score: {drift_score:.3f} | "
        f"drifted: {n_drifted}/{n_total}"
    )

    return {
        "dataset_drift_detected": dataset_drift,
        "drift_score": round(float(drift_score), 4),
        "n_features_drifted": int(n_drifted),
        "n_features_total": int(n_total),
        "n_production_samples": len(production_df),
        "n_reference_samples": len(reference_df),
    }
