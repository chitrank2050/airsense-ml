"""
Logging Configuration Module.
Configures Loguru for console and file output.
Intercepts stdlib logging to ensure consistent formatting across dependencies.
"""

import logging
import sys
from typing import Union

from loguru import logger

from src.utils.paths import PROJECT_ROOT


class InterceptHandler(logging.Handler):
    """Redirect stdlib logging (httpx, mlflow etc) through Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level: Union[str, int] = logger.level(record.levelname).name
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

    # # Silence noisy dependencies
    # for module in ["httpx", "httpcore", "urllib3"]:
    #     logging.getLogger(module).setLevel(logging.WARNING)

    # Console
    logger.add(
        sys.stdout,
        level=log_level,
        format=(
            "<green>{time:HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan> - "
            "<level>{message}</level>"
        ),
        colorize=True,
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

    # File
    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)
    logger.add(
        log_dir / "airsense.log",
        level=log_level,
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        enqueue=True,
    )
