import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


class FeatureNameResetter(BaseEstimator, TransformerMixin):
    """
    Resets feature names after ColumnTransformer.
    Fixes LightGBM warning about missing feature names.
    """

    def fit(self, _, y=None):
        self.fitted_ = True
        return self

    def transform(self, x):
        if hasattr(x, "toarray"):
            x = x.toarray()
        return pd.DataFrame(x).values


def build_numerical_pipeline() -> Pipeline:
    """StandardScaler for continuous numerical features."""
    return Pipeline(steps=[("scaler", StandardScaler())])


def build_categorical_pipeline() -> Pipeline:
    """OneHotEncoder for categorical features."""
    return Pipeline(
        steps=[
            (
                "encoder",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=False,
                ),
            )
        ]
    )
