from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def build_feature_pipeline(config: dict) -> ColumnTransformer:
    """
    Build feature pipeline from config definition.
    Column names come from config, not hardcoded.

    Args:
        config: loaded yaml config dict

    Returns:
        ColumnTransformer ready to fit
    """
    features = config["features"]

    numerical_pipeline = Pipeline(steps=[("scaler", StandardScaler())])

    categorical_pipeline = Pipeline(
        steps=[("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]
    )

    return ColumnTransformer(
        transformers=[
            ("numerical", numerical_pipeline, features["numerical"]),
            ("categorical", categorical_pipeline, features["categorical"]),
            ("ordinal", "passthrough", features["ordinal"]),
        ],
        remainder="drop",  # silently drops anything not listed — safety net
    )
