"""
This file contains the bootloader for the application.
"""

from src.utils.warnings import suppress_known_warnings

from .logger import logger, setup_logger


def bootstrap() -> None:
    """Initializes the application by setting up logging and other services."""

    setup_logger()
    suppress_known_warnings()

    logger.info("✅ Application bootstrapped successfully.")
