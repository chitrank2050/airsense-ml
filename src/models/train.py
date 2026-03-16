from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import Pipeline

from src.core import bootstrap, logger
from src.data import load_config, transform_target
from src.features.feature_pipeline import build_feature_pipeline
from src.features.preprocessing import load_and_clean
from src.monitoring.drift import save_reference_dataset
from src.utils import print_model_results, print_summary_table
from src.utils.paths import get_config_path

from .evaluate import compute_metrics
from .registry import get_models


def train(
    dataset_config_path: str = str(get_config_path("delhi.yaml")),
    model_config_path: str = str(get_config_path("model_config.yaml")),
):
    # Load configs
    model_config = load_config(model_config_path)
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

    logger.info(f"Train: {X_train.shape} | Val: {X_val.shape} | Test: {X_test.shape}")

    # Feature pipeline
    feature_pipeline = build_feature_pipeline(dataset_config)

    # Models
    models = get_models(model_config)

    # MLflow setup
    mlflow.set_tracking_uri(mlflow_cfg["tracking_uri"])
    mlflow.set_experiment(mlflow_cfg["experiment_name"])

    results: dict = {}
    best_model_name: str | None = None
    best_metric = float("inf")
    best_pipeline = None

    # Training loop
    for model_name, model in models.items():
        logger.info(f"Training {model_name} ...")

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

            print_model_results(model_name, val_metrics, test_metrics, cv_rmse)

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

    if best_model_name:
        print_summary_table(results, best_model_name)
        logger.success(f"Best model: {best_model_name} — Val RMSE: {best_metric}")
        # Monitoring reference — separate concern, imported from monitoring module
        save_reference_dataset(X_train, artifact_cfg)

    logger.success(f"Saved best model to: {best_model_path}")

    return results, best_model_name


if __name__ == "__main__":
    bootstrap()
    train()
