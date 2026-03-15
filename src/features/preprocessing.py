import numpy as np
import pandas as pd
import yaml


def load_config(config_path: str) -> dict:
    """Load dataset config from yaml file."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def drop_leakage(df: pd.DataFrame, leakage_cols: list[str]) -> pd.DataFrame:
    """Drop columns that cause data leakage or have zero value defined in config."""
    cols_to_drop = [c for c in leakage_cols if c in df.columns]
    return df.copy().drop(columns=cols_to_drop)


def transform_target(
    df: pd.DataFrame, target: str, log_transform: bool = True
) -> tuple[pd.DataFrame, pd.Series]:
    """
    Separate and optionally log-transform target variable.

    Args:
        df: input dataframe
        target: target column name from config
        log_transform: whether to apply log1p transform

    Returns:
        X: feature dataframe
        y: target series (log-transformed if specified)
    """
    y = np.log1p(df[target]) if log_transform else df[target]
    X = df.drop(columns=[target])
    return X, y


def inverse_transform_target(
    y_pred: np.ndarray, log_transform: bool = True
) -> np.ndarray:
    """Reverse log-transform predictions back to original scale."""
    return np.expm1(y_pred) if log_transform else y_pred


def engineer_base_features(df: pd.DataFrame, target: str) -> pd.DataFrame:
    """
    Create features that are derived from raw data.
    Runs before leakage drop and validation.
    """
    df["aqi_capped"] = (df[target] == 500).astype(int)
    return df


def validate_features(df: pd.DataFrame, config: dict) -> None:
    """
    Validate that all expected feature columns exist.
    Raises ValueError with clear message if any are missing.
    """
    features = config["features"]
    expected = features["numerical"] + features["categorical"] + features["ordinal"]
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise ValueError(
            f"Missing expected feature columns: {missing}\n"
            f"Available columns: {df.columns.tolist()}"
        )


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
    df = pd.read_csv(config["dataset"]["filepath"])
    df = engineer_base_features(df, config["dataset"]["target"])
    df = drop_leakage(df, config["leakage_cols"])
    validate_features(df, config)
    return df, config
