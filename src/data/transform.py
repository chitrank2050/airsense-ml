import numpy as np
import pandas as pd


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
