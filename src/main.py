from src.core import bootstrap, logger
from src.models.train import train


def main():
    """Main entry point for the application."""
    # Bootstrap the application
    bootstrap()

    # Start the application
    logger.info("Starting AirSense ML")

    # Train the model
    train()


if __name__ == "__main__":
    # Run the main function
    main()
