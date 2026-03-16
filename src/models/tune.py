"""
Hyperparameter tuning for AirSense ML using Optuna.

Uses Bayesian optimisation (TPE sampler) to find optimal hyperparameters
for Random Forest, XGBoost, and LightGBM. Each model gets 50 trials.
Best params are logged to a separate MLflow experiment and saved as
best_model_tuned.pkl.

Responsibility: hyperparameter tuning only.
Does NOT: define models, handle data loading, or serve predictions.

Usage:
    make tune
"""

from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import optuna
import pandas as pd
from lightgbm import LGBMRegressor
from optuna.samplers import TPESampler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor

from src.core import bootstrap
from src.core.logger import logger
from src.data import inverse_transform_target, transform_target
from src.data.loader import load_config
from src.features.feature_pipeline import build_feature_pipeline
from src.features.preprocessing import load_and_clean
from src.utils.paths import get_config_path

# ─────────────────────────────────────────────────────────────────────────────
# Search spaces — one per model family
# ─────────────────────────────────────────────────────────────────────────────


def xgboost_search_space(trial: optuna.Trial) -> dict:
    """
    Optuna search space for XGBoost.

    Args:
        trial: Optuna trial object — suggests parameter values.

    Returns:
        Dictionary of hyperparameter names to suggested values.
    """
    return {
        "n_estimators": trial.suggest_int("n_estimators", 100, 600),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
        "max_depth": trial.suggest_int("max_depth", 3, 10),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
        "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
        "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 1.0, log=True),
        "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 1.0, log=True),
        "random_state": 42,
        "n_jobs": -1,
    }


def lightgbm_search_space(trial: optuna.Trial) -> dict:
    """
    Optuna search space for LightGBM.

    num_leaves is the most important LightGBM parameter —
    controls model complexity independently of max_depth.

    Args:
        trial: Optuna trial object.

    Returns:
        Dictionary of hyperparameter names to suggested values.
    """
    return {
        "n_estimators": trial.suggest_int("n_estimators", 100, 600),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
        "max_depth": trial.suggest_int("max_depth", 3, 10),
        "num_leaves": trial.suggest_int("num_leaves", 20, 150),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
        "min_child_samples": trial.suggest_int("min_child_samples", 5, 50),
        "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 1.0, log=True),
        "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 1.0, log=True),
        "random_state": 42,
        "n_jobs": -1,
        "verbose": -1,
    }


def random_forest_search_space(trial: optuna.Trial) -> dict:
    """
    Optuna search space for Random Forest.

    Fewer hyperparameters than boosting models — faster to tune.

    Args:
        trial: Optuna trial object.

    Returns:
        Dictionary of hyperparameter names to suggested values.
    """
    return {
        "n_estimators": trial.suggest_int("n_estimators", 100, 500),
        "max_depth": trial.suggest_int("max_depth", 5, 30),
        "min_samples_split": trial.suggest_int("min_samples_split", 2, 20),
        "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 10),
        "max_features": trial.suggest_categorical(
            "max_features", ["sqrt", "log2", 0.5]
        ),
        "random_state": 42,
        "n_jobs": -1,
    }


SEARCH_SPACES = {
    "xgboost": (XGBRegressor, xgboost_search_space),
    "lightgbm": (LGBMRegressor, lightgbm_search_space),
    "random_forest": (RandomForestRegressor, random_forest_search_space),
}


# ─────────────────────────────────────────────────────────────────────────────
# Objective + Study
# ─────────────────────────────────────────────────────────────────────────────


def compute_val_rmse(
    pipeline: Pipeline,
    X_val: pd.DataFrame,
    y_val: pd.Series,
) -> float:
    """
    Evaluate pipeline on validation set.
    Returns RMSE on original AQI scale (not log scale).

    Args:
        pipeline: Fitted sklearn Pipeline.
        X_val: Validation features.
        y_val: Log-transformed validation targets.

    Returns:
        RMSE on original AQI scale.
    """
    preds = pipeline.predict(X_val)
    y_true = inverse_transform_target(y_val.values)
    y_pred = inverse_transform_target(preds)
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def make_objective(
    model_class,
    search_space_fn,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    feature_pipeline,
):
    """
    Create an Optuna objective function for a given model class.

    Closure pattern — captures data splits and feature pipeline
    so the objective only receives the trial object.

    Args:
        model_class: sklearn-compatible model class.
        search_space_fn: Function that takes trial and returns params dict.
        X_train: Training features.
        y_train: Training targets.
        X_val: Validation features.
        y_val: Validation targets.
        feature_pipeline: Fitted-ready ColumnTransformer.

    Returns:
        Objective function that Optuna can call with a trial.
    """

    def objective(trial: optuna.Trial) -> float:
        params = search_space_fn(trial)
        pipeline = Pipeline(
            steps=[
                ("features", feature_pipeline),
                ("model", model_class(**params)),
            ]
        )
        pipeline.fit(X_train, y_train)
        return compute_val_rmse(pipeline, X_val, y_val)

    return objective


# ─────────────────────────────────────────────────────────────────────────────
# Main tuning function
# ─────────────────────────────────────────────────────────────────────────────


def tune(
    dataset_config_path: str = str(get_config_path("delhi.yaml")),
    model_config_path: str = str(get_config_path("model_config.yaml")),
    n_trials: int = 50,
) -> tuple[str, dict, float]:
    """
    Run Optuna hyperparameter tuning for all tree ensemble models.

    Trains XGBoost, LightGBM, and Random Forest with Bayesian optimisation.
    Logs all trials to a separate MLflow experiment.
    Saves the best tuned model as best_model_tuned.pkl.

    Args:
        dataset_config_path: Path to dataset YAML config.
        model_config_path: Path to model YAML config.
        n_trials: Number of Optuna trials per model. Default 50.

    Returns:
        Tuple of (best_model_name, best_params, best_val_rmse).
    """
    model_config = load_config(model_config_path)
    train_cfg = model_config["training"]
    mlflow_cfg = model_config["mlflow"]
    artifact_cfg = model_config["artifacts"]

    # Load data
    df, dataset_config = load_and_clean(dataset_config_path)
    X, y = transform_target(
        df,
        target=dataset_config["dataset"]["target"],
        log_transform=dataset_config["log_transform_target"],
    )

    # Same splits as train.py — reproducibility
    X_train, X_test, y_train, _ = train_test_split(
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

    logger.info(
        f"Tuning splits — "
        f"Train: {X_train.shape} | Val: {X_val.shape} | Test: {X_test.shape}"
    )

    feature_pipeline = build_feature_pipeline(dataset_config)

    # MLflow — separate experiment from baseline training
    mlflow.set_tracking_uri(mlflow_cfg["tracking_uri"])
    mlflow.set_experiment(f"{mlflow_cfg['experiment_name']}-tuning")

    # Silence Optuna's own logs — we handle output
    optuna.logging.set_verbosity(optuna.logging.WARNING)

    best_overall_rmse = float("inf")
    best_overall_name = None
    best_overall_params = {}

    for model_name, (model_class, search_space_fn) in SEARCH_SPACES.items():
        logger.info(f"Tuning {model_name} — {n_trials} trials")

        study = optuna.create_study(
            direction="minimize",
            sampler=TPESampler(seed=42),
            study_name=f"{model_name}_study",
        )

        study.optimize(
            make_objective(
                model_class,
                search_space_fn,
                X_train,
                y_train,
                X_val,
                y_val,
                feature_pipeline,
            ),
            n_trials=n_trials,
            show_progress_bar=True,
        )

        best_params = study.best_params
        best_rmse = study.best_value

        logger.success(
            f"{model_name} — best val RMSE: {best_rmse:.4f} | trials: {n_trials}"
        )

        # Log best trial to MLflow
        with mlflow.start_run(run_name=f"{model_name}_tuned"):
            mlflow.log_params(best_params)
            mlflow.log_metric("best_val_rmse", best_rmse)
            mlflow.log_metric("n_trials", n_trials)

        if best_rmse < best_overall_rmse:
            best_overall_rmse = best_rmse
            best_overall_name = model_name
            best_overall_params = best_params

    # Retrain best model on train + val combined
    logger.info(
        f"Best model overall: {best_overall_name} — RMSE {best_overall_rmse:.4f}"
    )
    logger.info("Retraining on train + val combined...")

    model_class, _ = SEARCH_SPACES[best_overall_name]  # type: ignore[index]
    best_model = model_class(**best_overall_params)

    final_pipeline = Pipeline(
        steps=[
            ("features", build_feature_pipeline(dataset_config)),
            ("model", best_model),
        ]
    )

    X_trainval = pd.concat([X_train, X_val])
    y_trainval = pd.concat([y_train, y_val])
    final_pipeline.fit(X_trainval, y_trainval)

    # Save tuned model
    model_dir = Path(artifact_cfg["model_dir"])
    model_dir.mkdir(exist_ok=True)
    tuned_model_path = model_dir / "best_model_tuned.pkl"

    joblib.dump(final_pipeline, tuned_model_path)

    logger.success(f"Tuned model saved to {tuned_model_path}")
    logger.success(
        f"Baseline RMSE: 22.23 → Tuned RMSE: {best_overall_rmse:.4f} "
        f"({'improved' if best_overall_rmse < 22.23 else 'no improvement'})"
    )

    # Guard — proves to type checker that best_overall_name is str not None
    assert best_overall_name is not None, "No models tuned — SEARCH_SPACES is empty"
    assert isinstance(best_overall_params, dict)

    return best_overall_name, best_overall_params, best_overall_rmse


if __name__ == "__main__":
    bootstrap()
    tune()
