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
