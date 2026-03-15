import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


class FeatureNameResetter(BaseEstimator, TransformerMixin):
    """
    Resets feature names after ColumnTransformer.
    Fixes LightGBM warning about missing feature names.
    """

    def fit(self, X, y=None):
        self.fitted_ = True  # add this line
        return self

    def transform(self, X):
        if hasattr(X, "toarray"):
            X = X.toarray()
        return pd.DataFrame(X).values


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

    column_transformer = ColumnTransformer(
        transformers=[
            ("numerical", numerical_pipeline, features["numerical"]),
            ("categorical", categorical_pipeline, features["categorical"]),
            ("ordinal", "passthrough", features["ordinal"]),
        ],
        remainder="drop",  # silently drops anything not listed — safety net
    )

    return Pipeline(
        steps=[
            ("transformer", column_transformer),
            ("name_resetter", FeatureNameResetter()),
        ]
    )
