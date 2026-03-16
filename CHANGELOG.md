# Changelog

All notable changes to AirSense ML.

## [Unreleased]

### Documentation

- Update security vulnerability reporting instructions to use GitHub's built-in feature.
- Update security vulnerability reporting instructions to use GitHub's "Report a vulnerability" feature.
- Remove a comment from `warnings.py` and add `.dvc/tmp/` to `.gitignore`.
- Add new documentation for development log, tech stack, and data sources.
- Update project documentation in README.md
- Add descriptive comments to all Makefile targets for improved clarity.

### Features

- Implement path utility for centralized path management, enhance model training with detailed metric logging and joblib saving, and refine feature engineering with a feature name resetter.
- Introduce Loguru for comprehensive logging with console and file output, updating dependencies and gitignore rules.
- Add application bootstrapping to centralize initialization, logging setup, and warning suppression.
- Add graceful keyboard interrupt handling.
- Refine MLflow logging and warning suppression.
- Implement `rich`-based utilities for displaying model evaluation metrics and integrate them into the training script.
- Conditionally create the `aqi_capped` feature and integrate the `bootstrap` function call into the training script.
- Introduce a dedicated model registry module for centralizing model definitions and instantiation.
- Implement initial API structure including schemas prediction.
- Introduce API schemas for batch prediction, health, and model information.
- Introduce prediction adapter to translate between API schemas and ML pipeline data formats, and refactor schema imports to be relative.
- Add AQI prediction engine and update ruff pre-commit hook version.
- Add `api_lifespan` module and expose it in the `core` package.
- Add health check endpoint to report service and model loading status.
- Add API endpoint to retrieve model metadata and AQI category reference.
- Add v1 API endpoints for single and batch AQI predictions.
- Add initial API application file for Airsense ML.
- Add a clean environment option to the menu script and a corresponding clean target in the Makefile, along with integrating make commands for existing menu options.
- Implement centralized application configuration using pydantic-settings, externalizing API, model, and logging parameters.
- Add .env.example and refine .gitignore to ignore specific environment files.
- Make the model name configurable via settings.
- Add Dockerfile and .dockerignore, and update API host to 0.0.0.0 for containerization.
- Add FastAPI and Uvicorn dependencies, and reorganize ML/training dependencies into a new dedicated group.
- Add Bruno collection with health, model info, and single/batch prediction API requests.
- Add git-cliff for automated changelog generation and configure its settings.

### Maintenance

- Configure Dependabot to ignore specific `diskcache` versions and update `.gitignore` to exclude DVC cache and comment out old macOS icon patterns.
- Update project configuration and dependencies.
- Update project dependencies and streamline build configuration.
- Update Makefile.
- Release v
- Update Makefile.
- Release v
- Release v

### Refactor

- Extract `compute_metrics` into a new `evaluate.py` module and import it in `train.py`.

### Refactoring

- Centralize warning suppression, move metric explanations to documentation, and add `uv` lock file.
- Modularize feature pipeline and implement cyclical encoding for time-based features.
- Modularize feature pipeline construction and encoding, and enhance base feature engineering with cyclical time features.
- Consolidate data loading, transformation, and validation utilities into a new `src/data` package, enhancing data preprocessing.
- Replace local YAML configuration loading with a shared `load_config` utility.
- Adjust logger import path to its dedicated module.
- Parameterize logger configuration in `setup_logger` and remove `api_lifespan` from core exports.
- Remove `decode_meta` utility and simplify `APP_DESCRIPTION` assignment.
- Consolidate the bootstrap function into `__init__.py` with lazy imports and remove the dedicated `bootstrap.py` module.

### Build

- Add  to
- Update Makefile configuration
- Update build environment and Docker image configuration.
- Update Makefile targets and commands.


