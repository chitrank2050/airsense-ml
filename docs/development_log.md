# Development Log

## [✅ Complete] Phase 1 — Data & Training Pipeline

- Config-driven data pipeline supporting multiple datasets via YAML
- Automated leakage detection and schema validation
- Cyclical encoding for time features (hour, month, day of week)
- 7 models trained and compared: Linear, Ridge, Lasso, ElasticNet, Random Forest, XGBoost, LightGBM
- MLflow experiment tracking with full metrics logging
- DVC data versioning
- Modular project structure across preprocessing, feature engineering, encoding, and pipeline assembly

## [✅ Complete] Phase 2 — API & Docker

- FastAPI inference API with /v1/predict, /v1/predict/batch, /v1/health, /v1/model/info
- Pydantic request/response schemas with full validation
- Adapter pattern decoupling API layer from inference layer
- Versioned routing (/v1) ready for /v2 expansion
- Multi-stage Docker build — optimised ~400MB image
- Bruno API collection with automated tests
- Centralised config via pydantic-settings + .env files
- Structured logging via Loguru with stdlib interception

## [📋 Planned] Phase 3 — Deployment

- Deploy to Render (free tier) — live public URL
- Evidently data drift monitoring
- MkDocs documentation site hosted on GitHub Pages

## [📋 Planned] Phase 4 — Hyperparameter Tuning

- Optuna Bayesian optimisation across Random Forest, XGBoost, LightGBM
- 50 trials per model, TPE sampler
- Separate MLflow experiment for tuning runs
- Best tuned model saved as best_model_tuned.pkl

## [📋 Planned] Phase 5 — Production Hardening

- Prefect pipeline orchestration and scheduling
- Parquet data storage replacing CSV
- Multi-city expansion (Mumbai)
- Real-time data ingestion via OpenAQ API
- Multi-target prediction (PM2.5 + NO2 simultaneously)

## [📋 Planned] Phase 6 — Frontend + LLM

- Next.js frontend
- Map visualisation with zoom-based AQI markers
- LLM chatbot — "What will AQI be in Okhla next week?"
- Recommendation system based on user searches