# AirSense ML

> Production-grade Air Quality Index regression system for Delhi — trained pipeline, modular feature engineering, and a FastAPI inference API.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![Docker](https://img.shields.io/badge/Docker-ready-blue)
![MLflow](https://img.shields.io/badge/MLflow-tracked-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Version](https://img.shields.io/badge/version-0.4.0-brightgreen)

---

## Links

| | URL |
|---|---|
| 🌐 Live API | [Live API](https://airsense-ml-production.up.railway.app) |
| 📊 API Docs | [API Docs](https://airsense-ml-production.up.railway.app/docs) |
| 🐳 Docker Image | [Image](https://hub.docker.com/r/chitrank2050/airsense-ml) |
| 📚 Documentation | [Project Documentation](https://chitrank2050.github.io/airsense-ml/) |
| 👤 Portfolio | [About me](https://chitrankagnihotri.com) |

---

## What It Does

AirSense ML predicts Air Quality Index (AQI) for Delhi from weather and location features — temperature, humidity, wind speed, visibility, station, and time. It is not a Kaggle notebook. It is an end-to-end ML system built to production engineering standards.

**Prediction input:**
```json
{
  "station": "IGI Airport",
  "season": "Winter",
  "temperature": 14.5,
  "humidity": 82.0,
  "wind_speed": 3.2,
  "visibility": 2.1,
  "month": 1,
  "hour": 8,
  "day_of_week": "Monday"
}
```

**Prediction output:**
```json
{
  "aqi_predicted": 451.05,
  "aqi_rounded": 451,
  "category": "Severe",
  "model_version": "best_model",
  "prediction_timestamp": "2026-03-16T03:34:55Z"
}
```

---

## Architecture

```
Raw CSV (Delhi AQI 2020–2025)
    ↓
Data Loader + Validator          src/data/
    ↓
Feature Engineering              src/features/
    Cyclical encoding (hour, month, day_of_week)
    AQI ceiling flag (aqi_capped)
    ↓
sklearn ColumnTransformer        src/features/pipeline.py
    StandardScaler (numerical)
    OneHotEncoder (categorical)
    Passthrough (ordinal)
    ↓
Model Training (7 models)        src/models/train.py
    Linear, Ridge, Lasso, ElasticNet
    Random Forest, XGBoost, LightGBM
    ↓
MLflow Experiment Tracking       mlruns.db
    ↓
Best Model Saved                 models/best_model.pkl
    ↓
FastAPI Inference API            api/
    POST /v1/predict
    POST /v1/predict/batch
    GET  /v1/health
    GET  /v1/model/info
    ↓
Docker Container → Docker Hub
```

---

## Model Results

| Model | Val RMSE | R² | CV RMSE | |
|---|---|---|---|---|
| Linear Regression | 41.28 | 0.942 | 0.242 | baseline |
| Ridge | 41.28 | 0.942 | 0.242 | identical to linear |
| Lasso | 62.75 | 0.866 | 0.334 | over-regularised |
| ElasticNet | 56.41 | 0.892 | 0.303 | poor |
| Random Forest | **22.23** | **0.983** | 0.184 | ★ best |
| XGBoost | 22.24 | 0.983 | 0.183 | tied |
| LightGBM | 22.27 | 0.983 | 0.183 | tied |

Tree models outperform linear by **~45% on RMSE**. The non-linear interactions between season, hour, temperature, and AQI cannot be learned by linear models without manual feature engineering.

> See [Evaluation Metrics](https://chitrank2050.github.io/airsense-ml/ml/metrics/) for full metric explanations.

---

## Quickstart

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) — `brew install uv`
- [Docker](https://www.docker.com/) — for containerised deployment

### Local Setup

```bash
# Clone
git clone https://github.com/chitrank2050/airsense-ml.git
cd airsense-ml

# Create virtual environment
make init

# Install all dependencies (including training group)
uv sync --all-groups

# Download dataset — place Delhi AQI CSV in data/raw/
# https://www.kaggle.com/datasets/sohails07/delhi-weather-and-aqi-dataset-2025
```

```bash
make train
```

Trains 7 models, logs metrics to MLflow, and saves the best model to `models/best_model.pkl`. Use the interactive menu `make ml` (planned) or `make train` for the full suite.

### View Experiment Results

```bash
make mlflow
# Open http://127.0.0.1:5000
```

### Run API Locally

```bash
make api
# Open http://127.0.0.1:8000/docs
```

### Run with Docker

```bash
# Pull from Docker Hub
docker pull chitrank2050/airsense-ml:latest
docker run -p 8000:8000 chitrank2050/airsense-ml:latest

# Or build locally
make docker-build
make docker-run

# Test
make test

# Manage with Docker (interactive)
make docker
```

---

## API Reference

All endpoints are versioned under `/v1`.

### `POST /v1/predict`

Predict AQI for a single location and time.

**Request body:**

| Field | Type | Constraints | Description |
|---|---|---|---|
| `station` | string | required | Monitoring station name |
| `season` | string | required | Winter / Summer / Monsoon / Post-Monsoon |
| `latitude` | float | required | Station latitude |
| `longitude` | float | required | Station longitude |
| `temperature` | float | required | Celsius |
| `humidity` | float | 0–100 | Relative humidity % |
| `wind_speed` | float | ≥ 0 | km/h |
| `visibility` | float | ≥ 0 | km |
| `day` | int | 1–31 | Day of month |
| `month` | int | 1–12 | Month number |
| `hour` | int | 0–23 | Hour of day (24h) |
| `day_of_week` | string | required | Full day name e.g. Monday |
| `is_weekend` | int | 0 or 1 | 1 if weekend |

**Response:**

| Field | Type | Description |
|---|---|---|
| `aqi_predicted` | float | Raw predicted AQI |
| `aqi_rounded` | int | AQI clipped to 0–500 |
| `category` | string | CPCB category label |
| `model_version` | string | Model used |
| `prediction_timestamp` | string | UTC ISO timestamp |

### `POST /v1/predict/batch`

Up to 100 predictions in a single call. Wrap requests in `{"requests": [...]}`.

### `GET /v1/health`

Returns `{"status": "healthy", "model_loaded": true, ...}`.

### `GET /v1/model/info`

Returns model version, paths, and CPCB AQI category reference.

---

## AQI Categories (CPCB India)

| Range | Category |
|---|---|
| 0–50 | Good |
| 51–100 | Satisfactory |
| 101–200 | Moderate |
| 201–300 | Poor |
| 301–400 | Very Poor |
| 401–500 | Severe |

---

## Project Structure

```
airsense-ml/
├── bruno/                    # API client collection (Bruno)
├── configs/
│   ├── delhi.yaml            # Dataset config — features, leakage, target
│   ├── model_config.yaml     # Model params, training config, MLflow settings
│   └── model_config.prod.yaml # Production config — memory-optimised models
├── data/
│   ├── raw/                  # Original data — never modified, tracked by DVC
│   ├── processed/            # Cleaned data
│   └── features/             # Engineered feature sets
├── docs/                     # MkDocs documentation source
├── models/                   # Saved model artifacts (tracked by DVC)
├── notebooks/                # EDA only — never imported by src/
├── scripts/                  # Dev tooling (interactive menu)
├── api/                      # FastAPI application
│   ├── adapters/             # Adapter pattern — API schema ↔ predictor
│   ├── schemas/              # Pydantic request/response schemas (v1)
│   ├── v1/                   # Versioned route handlers
│   └── app.py                # FastAPI application factory
├── src/
│   ├── core/
│   │   ├── config.py         # Pydantic settings — single source of truth
│   │   ├── logger.py         # Loguru setup, stdlib interception
│   │   ├── api_lifespan.py   # FastAPI lifespan — model loading
│   │   └── __init__.py       # bootstrap() entry point
│   ├── data/
│   │   ├── loader.py         # load_config, load_raw, drop_leakage
│   │   └── validator.py      # validate_features, validate_no_nulls
│   ├── features/
│   │   ├── preprocessing.py       # transform_target, load_and_clean
│   │   ├── feature_engineering.py # cyclical encoding, aqi_capped
│   │   ├── encoding.py            # sklearn numerical/categorical pipelines
│   │   └── pipeline.py            # ColumnTransformer assembly
│   ├── models/
│   │   ├── registry.py       # MODEL_MAP, get_models, get_model_class
│   │   ├── evaluate.py       # compute_metrics → ModelMetrics (Pydantic)
│   │   ├── train.py          # Training orchestration + MLflow logging
│   │   ├── predict.py        # AQIPredictor — inference engine
│   │   └── tune.py           # Optuna hyperparameter tuning
│   └── utils/
│       ├── paths.py                 # PROJECT_ROOT, get_config_path, get_model_path
│       ├── warnings.py              # Centralised warning suppression registry
│       └── model_results_display.py # Rich tables for training output
├── tests/
├── .env.example              # Environment config template
├── Dockerfile                # Multi-stage, optimised production image (~400MB)
├── pyproject.toml            # uv manages dependencies
└── Makefile                  # All commands — make help
```

---

## Make Commands

```bash
make help           # Show all commands

# Setup
make init           # Create virtual environment
make install        # Install all dependencies

# ML Pipeline
make dev            # Run full pipeline
make train          # Train all 7 models
make tune           # Hyperparameter tuning (Optuna)
make mlflow         # Start MLflow UI

# API
make api            # Start FastAPI server locally

# Interactive Menus
make docker         # Manage Docker (build, run, push, deploy, logs...)
make airflow        # Manage Airflow orchestration (up, down, logs)
make docs           # Manage MkDocs (build, deploy, serve)
make git            # Manage Git (changelog, tag, release)
make db             # Manage Database (migrate, revision, rollback)

# Quality & Maintenance
make lint           # Ruff check
make format         # Ruff format
make test           # Run pytest suite
make tree           # Print project structure
make obliviate      # Interactive clean menu (cache, venv, models...)
```

---

## Tech Stack

| Layer | Tool | Why |
|---|---|---|
| Package Manager | uv | Fast, PEP 517, lockfile reproducibility |
| Data Versioning | DVC | Git for data — reproducible pipelines |
| Feature Engineering | scikit-learn Pipelines | Prevents training/serving skew |
| Experiment Tracking | MLflow | Metrics, params, artifacts per run |
| Models | scikit-learn, XGBoost, LightGBM | Linear baseline → tree ensemble |
| API | FastAPI | Async, Pydantic validation, auto docs |
| Config | pydantic-settings | Type-safe, env var override |
| Logging | Loguru | Structured, stdlib interception |
| Containerisation | Docker (multi-stage) | Reproducible, ~400MB image |
| Registry | Docker Hub | Public image hosting |
| API Client | Bruno | Git-native, no cloud account |
| Documentation | MkDocs + Material | Static site on GitHub Pages |
| Code Quality | Ruff | Linter + formatter, fast |
| Changelog | git-cliff | Conventional commit changelog |

> See [Tech Stack](https://chitrank2050.github.io/airsense-ml/development/tech_stack/) for full local vs production comparison.

---

## Configuration

All configuration is driven by YAML files and environment variables — no hardcoded values.

**Dataset config** (`configs/delhi.yaml`) — controls which columns are features, which are leakage, and the target variable. Adding a new city requires only a new YAML file.

**Model config** (`configs/model_config.yaml`) — controls train/val/test split, model hyperparameters, MLflow experiment name, and artifact paths.

**Environment** (`.env.dev` / `.env.prod`) — controls API host, port, log level, model name, and CORS origins. Copy `.env.example` to get started.

---

## Known Limitations

- `aqi_capped` feature defaults to `0` at inference time — the model may slightly underestimate AQI during peak winter pollution events (Oct–Feb) where true AQI exceeds 500.
- Single city (Delhi) — multi-city expansion planned for Phase 6.
- Weather-only features — real-time pollutant data integration planned for Phase 6.
- Random Forest model (best performer at 22.23 RMSE) is 216MB on disk — requires 400MB+ RAM when loaded. Use `make train-prod` for a memory-optimised LightGBM model for deployment on free-tier hosting.

---

## Roadmap

- [x] Phase 1 — Data pipeline, feature engineering, 7-model training, MLflow tracking
- [x] Phase 2 — FastAPI inference API, Docker, Bruno collection, Docker Hub
- [x] Phase 3 — MkDocs docs, PostgreSQL + Supabase, prediction logging, Evidently monitoring, Railway deployment, rate limiting
- [ ] Phase 4 — Optuna hyperparameter tuning
- [ ] Phase 5 — Tests, security hardening
- [ ] Phase 6 — Multi-city expansion, real-time OpenAQ ingestion
- [ ] Phase 7 — Next.js frontend, map visualisation, LLM chatbot

> See [Development Log](https://chitrank2050.github.io/airsense-ml/development/log/) for detailed phase progress.

---

## Data

Dataset: [Delhi NCR Air Quality & Pollution Dataset 2020–2025](https://www.kaggle.com/datasets/sohails07/delhi-weather-and-aqi-dataset-2025) via Kaggle.

201,664 rows × 25 columns. Hourly readings across multiple Delhi stations. 22.5% of AQI values are capped at 500 — concentrated in October–February winter smog season.

> See [Data Sources](https://chitrank2050.github.io/airsense-ml/data/sources/) for full source list.

---

## Contributing

This is a learning project built in public. Issues and PRs are welcome.

---

## License

MIT — see [LICENCE](LICENCE).