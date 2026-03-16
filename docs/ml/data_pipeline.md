# Data Pipeline

The data pipeline transforms raw CSV data into a clean, validated feature matrix ready for model training or inference.

---

## Overview

```
Raw CSV
    ↓
load_raw()              — read CSV from path in config
    ↓
engineer_base_features() — cyclical encoding, aqi_capped flag
    ↓
drop_leakage()          — remove AQI component columns
    ↓
validate_features()     — schema check against config
    ↓
validate_no_nulls()     — confirm no missing values in numerical cols
    ↓
validate_target_range() — confirm AQI within 0–500
    ↓
transform_target()      — log1p(AQI), separate X and y
    ↓
build_feature_pipeline() — ColumnTransformer (scale, encode, passthrough)
```

---

## Config-driven Design

Column names are never hardcoded. Everything comes from `configs/delhi.yaml`:

```yaml
dataset:
  filepath: data/raw/kaggle_delhi_ncr_aqi_dataset.csv
  target: aqi

leakage_cols:
  - pm25
  - pm10
  - no2
  - so2
  - co
  - o3
  - aqi_category
  - datetime
  - date
  - year
  - city

features:
  numerical:
    - temperature
    - humidity
    - wind_speed
    - visibility
    - latitude
    - longitude
    - dow_sin
    - dow_cos
    - hour_sin
    - hour_cos
    - month_sin
    - month_cos
  categorical:
    - season
    - station
  ordinal:
    - day
    - is_weekend
    - aqi_capped

log_transform_target: true
```

Adding a new city requires only a new YAML file with different column mappings.

---

## Leakage Removal

PM2.5, PM10, NO2, SO2, CO, O3 are the components used to calculate AQI. They are dropped before training because:

1. They are mathematically derived from AQI — training on them would be reverse-engineering a formula
2. They are not available at inference time — you cannot predict AQI from pollutants you don't yet know

This forces the model to learn from genuine weather predictors, making it useful for actual forecasting.

---

## Data Validation

Three validation checks run before any model sees data:

**1. Feature schema validation**
Confirms all expected columns from config exist in the dataframe. Raises `ValueError` with the exact missing columns if any are absent.

**2. Null value check**
Confirms no missing values in numerical feature columns. The Delhi AQI dataset has zero missing values — this check guards against future data sources.

**3. Target range validation**
Confirms AQI values are within the valid 0–500 CPCB range. Values outside this range indicate data quality issues.

---

## Target Transformation

AQI is right-skewed — most days are moderate, but severe winter pollution events create a long tail. Raw AQI distribution:

```
Mean:   266
Median: 232
Mode:   500 (22.5% of rows — sensor ceiling)
Skew:   0.19
```

Log-transforming with `np.log1p()` produces near-normal distribution (skew: -0.49), which improves linear model performance and stabilises tree model training.

At inference time, predictions are reverse-transformed with `np.expm1()` back to the original AQI scale.

---

## The aqi_capped Flag

22.5% of AQI values in the dataset are exactly 500 — the maximum recordable value. These are not true 500 readings but sensor ceiling hits during severe winter pollution.

The `aqi_capped` feature flags these rows so the model learns to recognise the ceiling pattern:

```python
df["aqi_capped"] = (df["aqi"] == 500).astype(int)
```

The capped values are concentrated in October–February — Delhi's winter smog season.

**At inference time**, `aqi_capped` defaults to `0` since the true AQI is unknown. This means the model may slightly underestimate during peak winter events. Removing this feature entirely causes RMSE to increase by ~3 points — so the signal is real despite the inference limitation.

---

## Train / Validation / Test Split

```
Full dataset: 201,664 rows
    ↓
Test set (20%):  40,333 rows  — held out completely until final evaluation
    ↓
Remaining 80%: 161,331 rows
    ↓
Validation set (10% of 80%): 16,134 rows  — used for model selection
Training set (remaining):   145,197 rows  — used for fitting
```

Split uses `shuffle=True` and `random_state=42` for reproducibility.