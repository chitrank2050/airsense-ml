"""
AirSense ML — unified command-line entry point.

Provides a single interface for all ML pipeline operations.
The API is run separately via api/app.py.

Usage:
    make train
    make tune
    uv run python -m src.main train --dataset-config configs/delhi.yaml
    uv run python -m src.main tune --n-trials 100
"""

import sys

from src.core import bootstrap, logger
from src.models.train import train


def main():
    """Parse CLI arguments and dispatch to the correct pipeline command.

    Commands:
        train — run full training pipeline across all enabled models
        tune  — run Optuna hyperparameter tuning for tree ensemble models
    """

    # Start the application
    logger.info("Starting AirSense ML")

    # Train the model
    train()


if __name__ == "__main__":
    try:
        bootstrap()
        main()
    except KeyboardInterrupt:
        # Catch the hard interrupt from the terminal to prevent ugly tracebacks
        logger.warning("🛑 AirSense ML interrupted by user (KeyboardInterrupt).")
        sys.exit(0)
