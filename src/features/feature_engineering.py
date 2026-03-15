import numpy as np
import pandas as pd


def engineer_base_features(df: pd.DataFrame, target: str) -> pd.DataFrame:
    """
    Create derived features from raw data.
    Runs before leakage drop and validation.
    Cyclical encoding for time features — preserves circular relationships.
    """
    # AQI ceiling flag
    # Only create aqi_capped if target exists — inference won't have it
    if target in df.columns:
        df["aqi_capped"] = (df[target] == 500).astype(int)
    else:
        df["aqi_capped"] = 0

    # Day of week: string → numeric → cyclical
    # map → numbers - tree models
    # get_dummies - linear models
    # sin/cos -> best for cyclical time feature
    day_map = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6,
    }

    if df["day_of_week"].dtype == object:
        df["day_of_week"] = df["day_of_week"].map(day_map)

    df["dow_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7)
    df["dow_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7)
    df = df.drop(columns=["day_of_week"])

    # Hour cyclical
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
    df = df.drop(columns=["hour"])

    # Month cyclical
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)
    df = df.drop(columns=["month"])

    return df
