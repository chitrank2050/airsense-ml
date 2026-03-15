import pandas as pd


def validate_features(df: pd.DataFrame, config: dict) -> None:
    """
    Validate all expected feature columns exist after cleaning.
    Raises ValueError with clear message if any are missing.

    Args:
        df: cleaned dataframe
        config: loaded yaml config dict
    """
    features = config["features"]
    expected = features["numerical"] + features["categorical"] + features["ordinal"]
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise ValueError(
            f"Missing expected feature columns: {missing}\n"
            f"Available columns: {df.columns.tolist()}"
        )


def validate_no_nulls(df: pd.DataFrame, cols: list[str]) -> None:
    """
    Validate no nulls exist in critical columns.
    Raises ValueError if nulls found.

    Args:
        df: dataframe to check
        cols: list of column names to check
    """
    null_cols = [c for c in cols if df[c].isna().any()]
    if null_cols:
        raise ValueError(
            f"Null values found in columns: {null_cols}\n"
            f"Null counts: {df[null_cols].isna().sum().to_dict()}"
        )


def validate_target_range(
    df: pd.DataFrame, target: str, min_val: float = 0, max_val: float = 500
) -> None:
    """
    Validate target variable is within expected range.

    Args:
        df: dataframe to check
        target: target column name
        min_val: minimum valid value
        max_val: maximum valid value
    """
    out_of_range = df[(df[target] < min_val) | (df[target] > max_val)]
    if len(out_of_range) > 0:
        raise ValueError(
            f"Target '{target}' has {len(out_of_range)} values outside [{min_val}, {max_val}]"
        )
