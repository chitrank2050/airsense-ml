# Development Log

This file contains the development log of the project.

## [✅ Complete] Phase 1 — Data & Training Pipeline

- Config-driven data pipeline supporting multiple datasets via YAML
- Automated leakage detection and schema validation
- Cyclical encoding for time features (hour, month, day of week)
- 7 models trained and compared: Linear, Ridge, Lasso, ElasticNet, Random Forest, XGBoost, LightGBM
- MLflow experiment tracking with full metrics logging
- DVC data versioning
- Modular project structure across preprocessing, feature engineering, encoding, and pipeline assembly

## [🔄 In Progress] Phase 2 — Hyperparameter Tuning

- Optuna Bayesian optimisation across Random Forest, XGBoost, LightGBM
- 50 trials per model, TPE sampler
- Separate MLflow experiment for tuning runs
- Best tuned model saved as best_model_tuned.pkl
- Retrained on train+val combined for maximum data usage

## [ ⌛ Not Started] Phase 3 — API & Deployment

- FastAPI inference endpoint with /predict, /health, /model/info
- Docker containerisation
- Deploy to Render (free tier) — live public URL
- Evidently data drift monitoring
- MkDocs documentation site

## [ ⌛ Not Started] Phase 4 — Production Hardening

- Prefect pipeline orchestration and scheduling
- Parquet data storage replacing CSV
- Multi-city expansion (Mumbai)
- Real-time data ingestion via OpenAQ API
- Multi-target prediction (PM2.5 + NO2 simultaneously)