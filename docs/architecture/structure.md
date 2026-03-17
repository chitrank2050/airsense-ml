# Project Structure

Every folder and file has a single responsibility. Nothing is arbitrary.

---

## Top-level

```
airsense-ml/
├── api/            # FastAPI application — top-level for clean separation
├── bruno/          # API client collection — executable requests, not docs
├── configs/        # YAML configuration — dataset and model parameters
├── data/           # Data files — tracked by DVC, never committed to git
├── docs/           # MkDocs source — this documentation
├── models/         # Trained model artifacts — tracked by DVC
├── notebooks/      # EDA exploration — never imported by src/
├── scripts/        # Dev tooling — interactive Makefile menus
├── src/            # Core ML logic and shared utilities
├── tests/          # Test suite
├── .env.example    # Environment variable template
├── Dockerfile      # Multi-stage production build
├── Makefile        # All project commands
└── pyproject.toml  # Package definition and dependencies
```

---

## `api/` — HTTP Layer
 
 ```
 api/
 ├── adapters/           # Translates between API schemas and ML pipeline
 │   └── prediction_adapter.py
 ├── schemas/            # Pydantic request/response contracts
 │   ├── prediction.py   # PredictionRequest, PredictionResponse
 │   ├── batch.py        # BatchPredictionRequest, BatchPredictionResponse
 │   ├── health.py       # HealthResponse
 │   └── model_info.py   # ModelInfoResponse
 ├── v1/                 # Versioned route handlers
 │   ├── predict.py      # POST /v1/predict, POST /v1/predict/batch
 │   ├── health.py       # GET /v1/health
 │   └── model_info.py   # GET /v1/model/info
 └── app.py              # FastAPI app factory — wires everything together
 ```
 
 ---
 
 ## `src/` — ML Logic & Core

```
src/
├── core/                   # Application foundation — base layer, no ML logic
│   ├── config.py           # All settings via pydantic-settings
│   ├── logger.py           # Loguru setup, stdlib interception
│   ├── api_lifespan.py     # FastAPI lifespan — loads model at startup
│   └── __init__.py         # bootstrap() — logger + warnings init
│
├── data/                   # Data loading and validation
│   ├── loader.py           # load_config, load_raw, drop_leakage
│   └── validator.py        # validate_features, validate_no_nulls, validate_target_range
│
├── features/               # Feature engineering and transformation
│   ├── preprocessing.py        # transform_target, load_and_clean orchestration
│   ├── feature_engineering.py  # cyclical time encoding, aqi_capped flag
│   ├── encoding.py             # sklearn numerical + categorical pipelines
│   └── pipeline.py             # ColumnTransformer assembly from config
│
├── models/                 # ML model logic
│   ├── registry.py         # MODEL_MAP — all model classes in one place
│   ├── evaluate.py         # compute_metrics → ModelMetrics (Pydantic)
│   ├── train.py            # Training orchestration + MLflow logging
│   ├── predict.py          # AQIPredictor — loads model, runs inference
│   └── tune.py             # Optuna hyperparameter tuning
│
└── utils/                  # Shared utilities
    ├── paths.py                  # PROJECT_ROOT, path helpers
    ├── warnings.py               # Centralised warning suppression registry
    └── model_results_display.py  # Rich terminal tables for training output
```

---

## `configs/`

```
configs/
├── delhi.yaml              # Delhi-specific dataset config
│                           # Controls: features, leakage cols, target, filepath
├── model_config.yaml       # Training config
│                           # Controls: models, hyperparams, splits, MLflow
└── model_config.prod.yaml  # Production training config
                            # XGBoost + LightGBM only — memory-optimised
```

Adding a new city (e.g. Mumbai) requires only `configs/mumbai.yaml` — zero code changes.

---

## `data/`

```
data/
├── raw/        # Original source data — never modified, DVC tracked
├── processed/  # Cleaned and validated data
└── features/   # Engineered feature sets (Parquet — planned)
```

Raw data is never committed to git. DVC pointer files (`data/raw.dvc`) are committed instead. Anyone cloning the repo runs `dvc pull` to get the data.

---

## `models/`

```
models/
├── best_model.pkl          # Best model from local training (Random Forest)
└── best_model_prod.pkl     # Best memory-safe model for deployment (LightGBM)
```

Both are gitignored via `*.pkl` and tracked by DVC.

---

## `bruno/`

```
bruno/
├── bruno.json              # Collection manifest
├── health.bru              # GET /v1/health
├── model_info.bru          # GET /v1/model/info
├── predict_single.bru      # POST /v1/predict — Delhi winter morning
├── predict_batch.bru       # POST /v1/predict/batch — 3 stations
└── environments/
    ├── local.bru           # baseUrl = http://localhost:8000
    └── production.bru      # baseUrl = https://your-deployed-url (gitignored)
```

---

## What Goes Where — Decision Rules

| Content | Location | Reason |
|---|---|---|
| HTTP routes | `api/v1/` | Transport layer only |
| Request/response shapes | `api/schemas/` | Single contract source |
| Schema ↔ pipeline translation | `api/adapters/` | Decouples API from ML |
| Model loading + inference | `src/models/predict.py` | ML layer, not API layer |
| Feature transformations | `src/features/` | Reused by train and inference |
| Column names, target | `configs/*.yaml` | Config, not code |
| App settings, ports | `src/core/config.py` | Single settings source |
| Exploration code | `notebooks/` | Never imported by src/ |
| Generated artifacts | `models/`, `data/` | DVC tracked, not git |