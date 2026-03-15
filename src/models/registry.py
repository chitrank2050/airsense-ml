from lightgbm import LGBMRegressor
from sklearn.base import BaseEstimator
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import ElasticNet, Lasso, LinearRegression, Ridge
from xgboost import XGBRegressor

MODEL_MAP: dict[str, type[BaseEstimator]] = {
    "linear_regression": LinearRegression,
    "ridge": Ridge,
    "lasso": Lasso,
    "elastic_net": ElasticNet,
    "random_forest": RandomForestRegressor,
    "xgboost": XGBRegressor,
    "lightgbm": LGBMRegressor,
}


def get_models(model_config: dict) -> dict[str, BaseEstimator]:
    """
    Instantiate models from config.
    Only returns models where enabled: true.
    """
    models = {}
    for name, cfg in model_config["models"].items():
        if cfg.get("enabled", True):
            cls = MODEL_MAP.get(name)
            if cls:
                models[name] = cls(**cfg.get("params", {}))
    return models


def get_model_class(name: str) -> type[BaseEstimator]:
    """Return model class by name. Used by tune.py."""
    if name not in MODEL_MAP:
        raise ValueError(f"Unknown model: {name}. Available: {list(MODEL_MAP.keys())}")
    return MODEL_MAP[name]
