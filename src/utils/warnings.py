import warnings
from typing import TypedDict

from src.core.logger import logger


class WarningEntry(TypedDict):
    message: str
    category: type[Warning]
    reason: str


# Registry of all suppressed warnings in the project.
SUPPRESSED_WARNINGS: list[WarningEntry] = [
    {
        "message": r".*X does not have valid feature names.*",
        "category": UserWarning,
        "reason": "LightGBM/sklearn interoperability issue during CV folds. Cosmetic only.",
    },
    {
        "message": r".*Saving scikit-learn models in the pickle.*",
        "category": UserWarning,
        "reason": "MLflow pickle safety warning. Models used internally only.",
    },
    {
        "message": r".*Failed to resolve installed pip version.*",
        "category": UserWarning,
        "reason": "MLflow conda environment warning. Project does not use conda.",
    },
]


def suppress_known_warnings() -> None:
    """Suppress all known/acknowledged warnings in one call."""
    for entry in SUPPRESSED_WARNINGS:
        logger.info(f"⚠️ Suppressing warning: {entry['reason']}")
        warnings.filterwarnings(
            "ignore",
            message=entry["message"],
            category=entry["category"],
        )
