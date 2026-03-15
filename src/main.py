from src.models.train import train
from src.utils.warnings import suppress_known_warnings

# suppress known warnings
suppress_known_warnings()


def main():
    train()


if __name__ == "__main__":
    main()
