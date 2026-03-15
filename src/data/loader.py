import pandas as pd
import yaml

from src.utils.paths import PROJECT_ROOT


def load_config(config_path: str) -> dict:
    """Load dataset config from yaml file."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def drop_leakage(df: pd.DataFrame, leakage_cols: list[str]) -> pd.DataFrame:
    """Drop leakage columns defined in config."""
    cols_to_drop = [c for c in leakage_cols if c in df.columns]
    return df.copy().drop(columns=cols_to_drop)


def load_raw(config: dict) -> pd.DataFrame:
    """
    Load raw CSV from path defined in config.

    Args:
        config: loaded yaml config dict

    Returns:
        Raw dataframe
    """
    filepath = PROJECT_ROOT / config["dataset"]["filepath"]
    return pd.read_csv(filepath)
