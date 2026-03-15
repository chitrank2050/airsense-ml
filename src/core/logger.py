"""
Logging Configuration Module.
Configures Loguru for console and file output.
Intercepts stdlib logging to ensure consistent formatting across dependencies.
"""

import logging
import sys

from loguru import logger

from src.utils.paths import PROJECT_ROOT

from .config import settings


class InterceptHandler(logging.Handler):
    """Redirect stdlib logging (httpx, mlflow etc) through Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logger(log_level: str = "INFO") -> None:
    """
    Configure Loguru for the project.
    Call once at entry point only — main.py, never inside modules.
    """
    # Intercept stdlib logs
    logging.root.handlers = [InterceptHandler()]

    # Set the root logger level to the configured level to ensure interception works
    logging.root.setLevel(log_level)

    # Reset Loguru Configuration
    logger.remove()

    # Silence noisy dependencies
    for module in settings.LOG_SILENCE_MODULES:
        logging.getLogger(module).setLevel(logging.ERROR)

    # Console
    logger.add(
        sys.stdout,
        level=log_level,
        format=settings.LOG_FORMAT,
        colorize=True,
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

    # File
    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)
    if settings.ENABLE_LOG_FILE:
        logger.add(
            log_dir / settings.LOG_FILE_NAME,
            level=log_level,
            rotation="10 MB",
            retention=settings.LOG_FILE_RETENTION,
            compression="zip",
            format=settings.LOG_FILE_FORMAT,
            enqueue=True,
        )
