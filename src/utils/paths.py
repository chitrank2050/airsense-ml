from pathlib import Path

# Always points to project root regardless of where you run from
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def get_config_path(filename: str) -> Path:
    return PROJECT_ROOT / "configs" / filename


def get_data_path(*parts: str) -> Path:
    return PROJECT_ROOT / "data" / Path(*parts)


def get_model_path(*parts: str) -> Path:
    return PROJECT_ROOT / "models" / Path(*parts)
