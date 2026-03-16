"""
Central configuration module for AirSense ML.

Defines application settings using Pydantic BaseSettings.
Settings are resolved in this priority order:
    1. Environment variables (e.g. API_PORT=9000 make api)
    2. .env.<ENV> file       (e.g. .env.dev, .env.prod)
    3. Default values below

Responsibility: single source of truth for all runtime configuration.
Does NOT: load models, handle requests, or define ML pipeline logic.

Usage:
    from src.core.config import settings

    app = FastAPI(title=settings.API_TITLE)
"""

import os
from importlib.metadata import metadata
from typing import ClassVar, Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.utils.decode_meta import decode_meta

# Read package metadata from pyproject.toml — single source of truth
_meta = metadata("airsense-ml")


class _Settings(BaseSettings):
    """Application settings with environment variable override support.

    All fields can be overridden via environment variables or .env files.
    Field names are case-insensitive when read from environment.

    Example:
        >>> import os
        >>> os.environ["API_PORT"] = "9000"
        >>> from src.core.config import settings
        >>> settings.API_PORT
        9000
    """

    # ----------------------------------------------------------------
    # 📦  Application metadata — sourced from pyproject.toml
    # ----------------------------------------------------------------
    APP_NAME: str = _meta["Name"].replace("-", " ").title()
    APP_VERSION: str = _meta["Version"]
    APP_DESCRIPTION: str = decode_meta(_meta["Summary"])

    # ----------------------------------------------------------------
    # 🌐  API
    # ----------------------------------------------------------------
    # FastAPI settings
    API_DOCS_URL: str = "/docs"
    API_REDOC_URL: str = "/redoc"
    API_OPENAPI_URL: str = "/openapi.json"
    API_TITLE: str = "AirSense ML API"
    API_DESCRIPTION: str = (
        "Production-grade Air Quality Index prediction API for Delhi. "
        "Predicts AQI and pollution category from weather and location features."
    )
    API_VERSION: str = "1.0.0"

    # API Server settings
    API_PREFIX: str = "/v1"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True  # reload on file change — dev only, override in .env.prod
    API_DEBUG: bool = False  # always opt-in to debug; never default True

    # API Middleware settings
    API_ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]
    API_ALLOW_CREDENTIALS: bool = True
    API_ALLOWED_METHODS: list[str] = ["*"]
    API_ALLOWED_HEADERS: list[str] = ["*"]

    # ----------------------------------------------------------------
    # 🤖  Model
    # ----------------------------------------------------------------
    MODEL_NAME: str = "best_model.pkl"
    MODEL_DIR: str = "models"
    DATASET_CONFIG: str = "configs/delhi.yaml"
    MODEL_CONFIG: str = "configs/model_config.yaml"

    # ----------------------------------------------------------------
    # ⚙️  Environment
    # ----------------------------------------------------------------
    ENV: ClassVar[str] = os.getenv("ENV", "dev")
    ENV_FILE: ClassVar[str] = f".env.{ENV}"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ----------------------------------------------------------------
    # 📝  Logging
    # ----------------------------------------------------------------
    LOG_SILENCE_MODULES: list[str] = [
        "mlflow.sklearn",
        "mlflow.utils.environment",
        "mlflow.models.model",
    ]
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FORMAT: str = (
        "<green>{time:HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan> - "
        "<level>{message}</level>"
    )
    ENABLE_LOG_FILE: bool = False
    LOG_FILE_NAME: str = "airsense.log"
    LOG_FILE_RETENTION: str = "30 days"
    LOG_FILE_FORMAT: str = (
        "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}"
    )

    # ----------------------------------------------------------------
    # ✅  Validators
    # ----------------------------------------------------------------
    @field_validator("API_PORT")
    @classmethod
    def port_must_be_valid(cls, v: int) -> int:
        """Validate API_PORT is within valid TCP port range.

        Args:
            v: Port number to validate.

        Returns:
            Validated port number.

        Raises:
            ValueError: If port is outside 1-65535 range.
        """
        if not (1 <= v <= 65535):
            raise ValueError(f"API_PORT must be between 1 and 65535, got {v}")
        return v


# Singleton — import this everywhere, never instantiate _Settings directly
settings = _Settings()
