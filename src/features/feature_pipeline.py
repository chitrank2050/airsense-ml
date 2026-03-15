from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from .feature_encoding import (
    FeatureNameResetter,
    build_categorical_pipeline,
    build_numerical_pipeline,
)


def build_feature_pipeline(config: dict) -> Pipeline:
    """
    Assemble full feature transformation pipeline from config.
    Column names come from config — never hardcoded.

    Args:
        config: loaded yaml config dict

    Returns:
        Fitted-ready sklearn Pipeline
    """
    features = config["features"]

    column_transformer = ColumnTransformer(
        transformers=[
            ("numerical", build_numerical_pipeline(), features["numerical"]),
            ("categorical", build_categorical_pipeline(), features["categorical"]),
            ("ordinal", "passthrough", features["ordinal"]),
        ],
        # silently drops anything not listed — safety net
        remainder="drop",
    )

    return Pipeline(
        steps=[
            ("transformer", column_transformer),
            ("name_resetter", FeatureNameResetter()),
        ]
    )
