# airsense-ml
AirSense ML is a production-grade regression system that predicts Air Quality Index (AQI) and individual pollutant levels (PM2.5, NO2, etc.) for a target city.

## Project Overview
| Attribute        | Value                                                         |
|------------------|---------------------------------------------------------------|
| Problem Type     | Regression (continuous output)                                |
| Target Variables | AQI score (primary) + PM2.5, NO2, PM10 (secondary)            |
| Initial Scope    | Single city (Delhi — relevant + data-rich)                    |
| Future Scope     | Multi-city, real-time ingestion                               |

## Project Structure
```text
airsense-ml/
├── data/
│   ├── raw/              # Original data, never modified
│   ├── processed/        # Cleaned, validated data
│   └── features/         # Engineered feature sets (Parquet)
├── configs/
│   ├── delhi.yaml        # City-specific config
│   └── model_config.yaml # Model hyperparameters
├── src/
│   ├── data/
│   │   ├── loader.py     # Data ingestion
│   │   └── validator.py  # Great Expectations schema checks
│   ├── features/
│   │   ├── preprocessing.py    # Cleaning, imputation
│   │   ├── feature_engineering.py # New features, interactions
│   │   └── encoding.py         # Categorical encoding
│   ├── models/
│   │   ├── train.py      # Training loop
│   │   ├── predict.py    # Inference logic
│   │   └── evaluate.py   # RMSE, RMSLE, R2, feature importance
│   ├── pipelines/
│   │   ├── training_pipeline.py   # End-to-end train flow
│   │   └── inference_pipeline.py  # Prediction flow
│   ├── api/
│   │   └── app.py        # FastAPI endpoints
│   └── utils/
│       ├── metrics.py    # Custom metric functions
│       └── logger.py     # Structured logging
├── models/               # Saved model artifacts (MLflow manages these)
├── notebooks/            # Exploration only — never production code
├── tests/                # Unit tests per module
├── Dockerfile
├── pyproject.toml        # uv manages this
├── .dvc/                 # DVC config
└── README.md
```