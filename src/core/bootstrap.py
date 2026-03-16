"""
This file contains the bootloader for the application.
"""

from src.utils.warnings import suppress_known_warnings

from .config import settings
from .logger import logger, setup_logger


def bootstrap() -> None:
    """Initializes the application by setting up logging and other services."""

    setup_logger(
        log_level=settings.LOG_LEVEL,
        log_format=settings.LOG_FORMAT,
        enable_file=settings.ENABLE_LOG_FILE,
        log_file_name=settings.LOG_FILE_NAME,
        log_file_retention=settings.LOG_FILE_RETENTION,
        log_file_format=settings.LOG_FILE_FORMAT,
        silence_modules=settings.LOG_SILENCE_MODULES,
    )
    suppress_known_warnings()

    logger.info("✅ Application bootstrapped successfully.")
