import numpy as np
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error

from src.data import inverse_transform_target


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """
    Compute evaluation metrics on original AQI scale.
    Inputs are log-transformed — inverse transform before computing.
    """
    y_true_orig = inverse_transform_target(y_true)
    y_pred_orig = inverse_transform_target(y_pred)

    rmse = root_mean_squared_error(y_true_orig, y_pred_orig)
    mae = mean_absolute_error(y_true_orig, y_pred_orig)
    r2 = r2_score(y_true_orig, y_pred_orig)

    # RMSLE on original scale
    rmsle = root_mean_squared_error(
        np.log1p(y_true_orig), np.log1p(np.clip(y_pred_orig, 0, None))
    )

    return {
        "rmse": round(rmse, 4),
        "mae": round(mae, 4),
        "r2": round(r2, 4),
        "rmsle": round(rmsle, 4),
    }
