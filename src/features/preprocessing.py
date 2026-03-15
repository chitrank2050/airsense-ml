import pandas as pd

from src.data import (
    drop_leakage,
    load_config,
    validate_features,
    validate_no_nulls,
    validate_target_range,
)
from src.utils.paths import PROJECT_ROOT

from .feature_engineering import engineer_base_features


def load_and_clean(config_path: str) -> tuple[pd.DataFrame, dict]:
    """
    Load raw data and apply cleaning steps from config.

    Args:
        config_path: path to yaml config file

    Returns:
        df: Cleaned dataframe ready for feature pipeline
        config: Loaded configuration dictionary
    """
    config = load_config(config_path)

    # Load raw data
    df = pd.read_csv(PROJECT_ROOT / config["dataset"]["filepath"])

    # Engineer base features
    df = engineer_base_features(df, config["dataset"]["target"])

    # Drop leakage columns
    df = drop_leakage(df, config["leakage_cols"])

    # Validate data quality
    validate_features(df, config)
    validate_no_nulls(df, config["features"]["numerical"])
    validate_target_range(df, config["dataset"]["target"])
    return df, config
