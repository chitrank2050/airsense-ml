"""
Unit tests for data loading and preprocessing logic.

These tests ensure data integrity invariants hold true, such as
guaranteeing no target leakage during feature preparation.
"""

import pandas as pd

from src.data.loader import drop_leakage


def test_drop_leakage():
    """
    Verify that leakage columns are successfully dropped from the DataFrame.
    """
    # Arrange: create a dummy dataframe with features and known leakage columns
    df = pd.DataFrame(
        {
            "feature1": [1, 2],
            "feature2": [3, 4],
            "leak1": [5, 6],
            "leak2": [7, 8],
        }
    )
    leakage_cols = ["leak1", "leak2", "not_exist"]

    # Act: drop leakage columns
    df_cleaned = drop_leakage(df, leakage_cols)

    # Assert: only valid features remain
    assert "leak1" not in df_cleaned.columns
    assert "leak2" not in df_cleaned.columns
    assert "feature1" in df_cleaned.columns
    assert "feature2" in df_cleaned.columns
    assert len(df_cleaned.columns) == 2
