from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import yaml
from lightgbm import LGBMRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import ElasticNet, Lasso, LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor

from src.features.feature_engineering import build_feature_pipeline
from src.features.preprocessing import (
    inverse_transform_target,
    load_and_clean,
    transform_target,
)
from src.utils.paths import get_config_path

# --- Metrics ---


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """
    Compute evaluation metrics on original AQI scale.
    Inputs are log-transformed — inverse transform before computing.
    """
    y_true_orig = inverse_transform_target(y_true)
    y_pred_orig = inverse_transform_target(y_pred)

    rmse = np.sqrt(mean_squared_error(y_true_orig, y_pred_orig))
    mae = mean_absolute_error(y_true_orig, y_pred_orig)
    r2 = r2_score(y_true_orig, y_pred_orig)

    # RMSLE on original scale
    rmsle = np.sqrt(
        mean_squared_error(
            np.log1p(y_true_orig), np.log1p(np.clip(y_pred_orig, 0, None))
        )
    )

    return {
        "rmse": round(rmse, 4),
        "mae": round(mae, 4),
        "r2": round(r2, 4),
        "rmsle": round(rmsle, 4),
    }


# --- Model Registry ---


def get_models(model_config: dict) -> dict:
    """
    Build model instances from config.
    Only returns models where enabled: true.
    """
    model_map = {
        "linear_regression": LinearRegression,
        "ridge": Ridge,
        "lasso": Lasso,
        "elastic_net": ElasticNet,
        "random_forest": RandomForestRegressor,
        "xgboost": XGBRegressor,
        "lightgbm": LGBMRegressor,
    }

    models = {}
    for name, cfg in model_config["models"].items():
        if cfg.get("enabled", True):
            cls = model_map.get(name)
            if cls:
                models[name] = cls(**cfg.get("params", {}))

    return models


# --- Training ---


def load_model_config(config_path: str) -> dict:
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def train(
    dataset_config_path: str = str(get_config_path("delhi.yaml")),
    model_config_path: str = str(get_config_path("model_config.yaml")),
):
    # Load configs
    model_config = load_model_config(model_config_path)
    train_cfg = model_config["training"]
    eval_cfg = model_config["evaluation"]
    mlflow_cfg = model_config["mlflow"]
    artifact_cfg = model_config["artifacts"]

    # Load and prepare data
    df, dataset_config = load_and_clean(dataset_config_path)
    X, y = transform_target(
        df,
        target=dataset_config["dataset"]["target"],
        log_transform=dataset_config["log_transform_target"],
    )

    # Train / val / test split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=train_cfg["test_size"],
        random_state=train_cfg["random_state"],
        shuffle=train_cfg["shuffle"],
    )

    X_train, X_val, y_train, y_val = train_test_split(
        X_train,
        y_train,
        test_size=train_cfg["val_size"],
        random_state=train_cfg["random_state"],
    )

    print(f"Train: {X_train.shape} | Val: {X_val.shape} | Test: {X_test.shape}")

    # Feature pipeline
    feature_pipeline = build_feature_pipeline(dataset_config)

    # Models
    models = get_models(model_config)

    # MLflow setup
    mlflow.set_tracking_uri(mlflow_cfg["tracking_uri"])
    mlflow.set_experiment(mlflow_cfg["experiment_name"])

    results = {}
    best_model_name = None
    best_metric = float("inf")
    best_pipeline = None

    # Training loop
    for model_name, model in models.items():
        print(f"\nTraining {model_name}...")

        with mlflow.start_run(run_name=model_name):
            # Full pipeline: feature transform + model
            full_pipeline = Pipeline(
                steps=[("features", feature_pipeline), ("model", model)]
            )

            # Train
            full_pipeline.fit(X_train, y_train)

            # Evaluate on val set
            val_preds = full_pipeline.predict(X_val)
            val_metrics = compute_metrics(y_val.values, val_preds)

            # Evaluate on test set
            test_preds = full_pipeline.predict(X_test)
            test_metrics = compute_metrics(y_test.values, test_preds)

            # Cross validation on train set
            cv_scores = cross_val_score(
                full_pipeline,
                X_train,
                y_train,
                cv=train_cfg["cv_folds"],
                scoring="neg_root_mean_squared_error",
            )
            cv_rmse = round(-cv_scores.mean(), 4)

            # Log to MLflow
            mlflow.log_params(model_config["models"][model_name].get("params", {}))
            mlflow.log_metrics({f"val_{k}": v for k, v in val_metrics.items()})
            mlflow.log_metrics({f"test_{k}": v for k, v in test_metrics.items()})
            mlflow.log_metric("cv_rmse", cv_rmse)
            mlflow.sklearn.log_model(full_pipeline, name=model_name)

            print(f"  Val  RMSE: {val_metrics['rmse']} | R2: {val_metrics['r2']}")
            print(f"  Test RMSE: {test_metrics['rmse']} | R2: {test_metrics['r2']}")
            print(f"  CV   RMSE: {cv_rmse}")

            results[model_name] = {
                "val": val_metrics,
                "test": test_metrics,
                "cv_rmse": cv_rmse,
            }

            # Track best model by primary metric on val set
            primary = val_metrics[eval_cfg["primary_metric"]]
            if primary < best_metric:
                best_metric = primary
                best_model_name = model_name
                best_pipeline = full_pipeline

    # Save best model
    model_dir = Path(artifact_cfg["model_dir"])
    model_dir.mkdir(exist_ok=True)

    best_model_path = model_dir / artifact_cfg["best_model_name"]

    # Save model using joblib
    joblib.dump(best_pipeline, best_model_path)

    print(f"\nBest model: {best_model_name}")
    print(f"Best val RMSE: {best_metric}")
    print(f"Saved to: {best_model_path}")

    return results, best_model_name
