# Architecture Overview

AirSense ML is structured as a layered ML system — each layer has a single responsibility and strict import direction.

---

## System Overview

```
┌─────────────────────────────────────────────────────┐
│                   Data Layer                         │
│   Raw CSV → Loader → Validator → Feature Engineering │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│                 Training Layer                       │
│   sklearn Pipeline → 7 Models → MLflow → Best Model │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│                  Inference Layer                     │
│   AQIPredictor → PredictionAdapter → Response       │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│                    API Layer                         │
│   FastAPI → /v1 Routes → Pydantic Schemas           │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│                 Container Layer                      │
│   Docker (multi-stage, linux/amd64) → Docker Hub    │
└─────────────────────────────────────────────────────┘
```

---

## Dependency Direction

The most important architectural rule — imports flow strictly downward. No layer imports from a layer above it:

```
Level 0 — imports nothing from src
    src/core/config.py
    src/core/logger.py
    src/utils/paths.py

Level 1 — imports from Level 0 only
    src/utils/warnings.py
    src/core/__init__.py

Level 2 — imports from Level 0 + 1
    src/data/loader.py
    src/data/validator.py
    src/features/*

Level 3 — imports from Level 0, 1, 2
    src/models/*

Level 4 — imports from everything below
    api/*
```

Violating this rule creates circular imports. Every circular import we encountered during development was caused by a Level N module importing from Level N+1.

---

## Key Design Patterns

### Config-driven pipeline

No hardcoded column names, model parameters, or file paths in code. Everything flows from YAML:

```
configs/delhi.yaml          → data pipeline
configs/model_config.yaml   → training pipeline
.env.dev / .env.prod        → application settings
```

Adding a new city requires only a new YAML file — zero code changes.

### Adapter pattern (API ↔ Inference)

`PredictionRequest` (API schema) never touches `AQIPredictor` directly. The adapter translates between them:

```
PredictionRequest → PredictionAdapter.to_dataframe() → AQIPredictor
AQIPredictor      → PredictionAdapter.to_response()  → PredictionResponse
```

This means the API contract and the ML pipeline can evolve independently.

### sklearn Pipeline objects

Feature transformations are encapsulated in sklearn `Pipeline` and `ColumnTransformer` objects — not applied as raw functions. This means:

- The same transformations are guaranteed at training and inference time
- No training/serving skew
- The full pipeline (features + model) is serialised as a single artifact

### Singleton predictor

`AQIPredictor` is instantiated once at API startup via FastAPI's lifespan context manager and stored on `app.state`. All requests share the same loaded model — no per-request model loading overhead.

---

## Data Flow — Training

```
1. load_config("configs/delhi.yaml")
2. load_raw(config)                  — reads CSV
3. engineer_base_features(df)        — cyclical encoding, aqi_capped
4. drop_leakage(df, config)          — removes PM2.5, NO2 etc
5. validate_features(df, config)     — raises if columns missing
6. transform_target(df)              — log1p(AQI), separate X and y
7. train_test_split                  — 80/10/10 train/val/test
8. build_feature_pipeline(config)    — ColumnTransformer
9. Pipeline(features + model).fit()  — for each of 7 models
10. compute_metrics(val, test)       — RMSE, R², MAE, RMSLE
11. mlflow.log_metrics/params/model  — per run
12. joblib.dump(best_pipeline)       — models/best_model.pkl
```

## Data Flow — Inference

```
1. POST /v1/predict (JSON body)
2. Pydantic validates PredictionRequest
3. request.app.state.predictor.predict(body)
4. PredictionAdapter.to_dataframe(request)   — single-row DataFrame
5. engineer_base_features(df, target="aqi")  — same as training
6. pipeline.predict(df)                      — log-scale prediction
7. inverse_transform_target(prediction)      — expm1 → AQI scale
8. PredictionAdapter.to_response(aqi, version)
9. PredictionResponse returned as JSON
```

---

## Configuration Architecture

```
pyproject.toml          — package metadata, dependency groups
configs/delhi.yaml      — dataset-specific: features, leakage, target
configs/model_config.yaml — training: models, hyperparams, MLflow, artifacts
.env.example            — template for all environment variables
.env.dev                — local overrides (gitignored)
.env.prod               — production overrides (gitignored)
src/core/config.py      — pydantic-settings reads .env, exposes settings singleton
```

All runtime configuration is accessible via `from src.core import settings`.