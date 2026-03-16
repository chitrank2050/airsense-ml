# Evaluation Metrics Guide

Reference for understanding model evaluation output in AirSense ML.

---

## RMSE — Root Mean Squared Error
**Lower is better. Unit: AQI points.**

Average prediction error in real terms. RMSE: 22.31 means the model
is on average 22 AQI points off from reality.

Use this as the primary metric when comparing models.

| Range | Verdict |
|---|---|
| < 20 | Excellent |
| 20–35 | Good |
| 35–50 | Acceptable |
| > 50 | Poor |

---

## R² — R-Squared
**Higher is better. Range: 0 to 1.**

Percentage of AQI variation the model explains.
R²: 0.983 = model explains 98.3% of variance.

| Range | Verdict |
|---|---|
| > 0.95 | Excellent |
| 0.90–0.95 | Good |
| 0.80–0.90 | Acceptable |
| < 0.80 | Poor |

---

## MAE — Mean Absolute Error
**Lower is better. Unit: AQI points.**

Average absolute difference between predicted and actual.
Less sensitive to outliers than RMSE.
Use alongside RMSE — if MAE << RMSE, you have large outlier errors.

---

## RMSLE — Root Mean Squared Log Error
**Lower is better. Unitless.**

Penalises percentage errors rather than absolute errors.
Important here because AQI is right-skewed — a 20 point error 
at AQI 50 is worse than at AQI 400.

---

## CV RMSE — Cross-Validation RMSE
**Lower is better. Unit: log(AQI) space.**

Computed during training on log-transformed target.
Cannot be compared directly to Val/Test RMSE.
Only use it to compare models against each other — 
lower CV RMSE = more consistent across data splits = more reliable.

---

## Model Comparison — Baseline Results

| Model | Val RMSE | R² | CV RMSE | Verdict |
|---|---|---|---|---|
| Linear Regression | 40.29 | 0.944 | 0.2525 | Weak baseline |
| Ridge | 40.29 | 0.944 | 0.2525 | Identical to linear |
| Lasso | 72.30 | 0.822 | 0.3557 | Over-regularised |
| ElasticNet | 63.40 | 0.863 | 0.3200 | Poor |
| Random Forest | **22.31** | **0.983** | 0.1846 | Winner (baseline) |
| XGBoost | 22.33 | 0.983 | 0.1832 | Virtually tied |
| LightGBM | 22.40 | 0.983 | 0.1830 | Virtually tied |

Tree models outperform linear by ~45% on RMSE.
This confirms non-linear feature interactions dominate AQI prediction.

---

## How to Pick the Best Model

1. **Lowest Val RMSE** — primary decision metric
2. **Highest R²** — confirms pattern learning, not just memorisation
3. **Val RMSE ≈ Test RMSE** — large gap = overfitting
4. **CV RMSE consistency** — high variance across folds = unstable model