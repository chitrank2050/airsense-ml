# Model Training

AirSense ML trains 7 models in a single pipeline run and automatically selects the best performer.

---

## Running Training

```bash
make train
```

Trains all 7 models, logs everything to MLflow, saves the best model to `models/best_model.pkl`.

For production-optimised training (XGBoost + LightGBM only):

```bash
make train-prod
```

---

## Models

Two families are trained — linear models as interpretable baselines, tree ensembles for performance.

### Linear Family

| Model | Purpose | Key Parameter |
|---|---|---|
| Linear Regression | Raw baseline — no regularisation | None |
| Ridge | L2 regularisation — handles multicollinearity | `alpha` |
| Lasso | L1 regularisation — automatic feature selection | `alpha` |
| ElasticNet | Combined L1+L2 | `alpha`, `l1_ratio` |

Linear models establish the performance floor. If tree models don't significantly outperform linear models, it suggests the relationship is mostly linear and simpler models are sufficient.

### Tree Ensemble Family

| Model | Strength | Memory |
|---|---|---|
| Random Forest | Stable, parallel trees, interpretable importance | ~400MB |
| XGBoost | Sequential boosting, speed + accuracy | ~50MB |
| LightGBM | Fastest, leaf-wise growth, best for large data | ~15MB |

Tree models handle non-linear interactions automatically — they learn "high humidity + low wind + winter = severe AQI" without manual feature engineering.

---

## Why Tree Models Outperform Linear by 45%

AQI is not a linear function of weather. The relationship depends on combinations:

- High humidity + low wind speed + winter → severe smog
- High temperature + monsoon season → pollution washout
- Night hours + residential areas → different baseline than daytime

Linear models can only learn `AQI = a*temperature + b*humidity + ...`. They cannot learn "if temperature AND humidity AND season interact in this specific way". Tree models split on combinations of features, learning exactly these patterns.

**Baseline results:**

| Model | Val RMSE | R² |
|---|---|---|
| Linear Regression | 41.28 | 0.942 |
| Random Forest | **22.23** | **0.983** |

Random Forest reduces error by **46%** over linear regression.

---

## MLflow Experiment Tracking

Every training run logs:

- **Parameters** — model hyperparameters from config
- **Metrics** — `val_rmse`, `val_r2`, `val_mae`, `val_rmsle`, `test_rmse`, `test_r2`, `cv_rmse`
- **Artifacts** — the full serialised pipeline (features + model)

View all runs:

```bash
make mlflow
# Open http://127.0.0.1:5000
```

Experiments are stored in `mlruns.db` (SQLite). Never commit this file — it's gitignored.

---

## Model Selection

The best model is selected by **lowest validation RMSE** — not test RMSE.

Test set is held out completely and used only for final reporting. Using test RMSE for selection would leak test information into the model choice.

```python
# Primary metric from model_config.yaml
primary_metric: rmse

# Selection logic in train.py
if val_metrics.rmse < best_metric:
    best_metric = val_metrics.rmse
    best_model_name = model_name
    best_pipeline = full_pipeline
```

---

## Cross-Validation

5-fold cross-validation runs on the training set for each model. This gives a more reliable estimate of generalisation than a single train/val split.

CV RMSE is reported in log space (the model is trained on `log1p(AQI)`) — it cannot be directly compared to Val/Test RMSE which is reported on the original AQI scale.

Use CV RMSE only to compare model consistency across folds — lower CV RMSE means more stable performance.

---

## Serialisation

The full sklearn `Pipeline` object (feature transformer + model) is saved with `joblib`:

```
models/best_model.pkl
```

The pipeline contains everything needed for inference:
- `ColumnTransformer` with fitted `StandardScaler` and `OneHotEncoder`
- Fitted model (Random Forest, XGBoost, or LightGBM)

This guarantees that inference applies identical transformations to training — no training/serving skew.

---

## Configuration

All training parameters are in `configs/model_config.yaml`:

```yaml
training:
  test_size: 0.2
  val_size: 0.1
  random_state: 42
  cv_folds: 5
  shuffle: true

models:
  random_forest:
    enabled: true
    params:
      n_estimators: 200
      max_depth: 15
      ...

evaluation:
  primary_metric: rmse

mlflow:
  experiment_name: airsense-aqi-regression
  tracking_uri: sqlite:///mlruns.db

artifacts:
  model_dir: models/
  best_model_name: best_model_tuned.pkl
```

To disable a model, set `enabled: false`. To change hyperparameters, update `params`. No code changes required.