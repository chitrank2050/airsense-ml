import warnings

# Registry of all suppressed warnings in the project.
SUPPRESSED_WARNINGS = [
    {
        "message": "X does not have valid feature names",
        "category": UserWarning,
        "reason": "LightGBM/sklearn interoperability issue during CV folds. Cosmetic only, does not affect results.",
    },
    {
        "message": "Saving scikit-learn models in the pickle",
        "category": UserWarning,
        "reason": "MLflow pickle safety warning. Acknowledged — models are for internal use only.",
    },
    {
        "message": "Failed to resolve installed pip version",
        "category": UserWarning,
        "reason": "MLflow conda env warning. Not using conda in this project.",
    },
]


def suppress_known_warnings() -> None:
    """
    Suppress all known/acknowledged warnings in one call.
    Call this at the top of any entry point (train.py, api/app.py etc).

    To add a new suppression:
        1. Add an entry to SUPPRESSED_WARNINGS above
        2. Include message, category, and reason
        3. Never suppress inline with warnings.filterwarnings outside this file
    """
    for entry in SUPPRESSED_WARNINGS:
        warnings.filterwarnings(
            "ignore",
            message=entry["message"],
            category=entry["category"],
        )
