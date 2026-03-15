"""
AQI inference engine for the AirSense ML API.

Loads a persisted sklearn Pipeline and exposes a clean predict()
interface consumed by the API layer via PredictionAdapter.

Designed to be instantiated once at API startup via lifespan.py
and reused across all requests — never instantiated per request.

Responsibility: load model, run inference, return raw prediction.
Does NOT: define API schemas, handle HTTP, or transform features
beyond what the trained pipeline already encapsulates.

Pattern: Singleton-like usage via app.state.predictor in lifespan.py.
"""

from pathlib import Path

import joblib

from src.api.adapters import PredictionAdapter
from src.api.schemas import PredictionRequest, PredictionResponse
from src.core.logger import logger
from src.data import inverse_transform_target, load_config
from src.features import engineer_base_features
from src.utils.paths import get_config_path, get_model_path


class AQIPredictor:
    """Loads a trained sklearn pipeline and runs AQI inference.

    Wraps a persisted sklearn Pipeline and exposes a clean predict()
    interface. The pipeline internally handles all feature
    transformations — StandardScaler, OneHotEncoder, cyclical
    encoding — exactly as applied during training.

    Attributes:
        model_path: Resolved path to the persisted model pickle file.
        dataset_config_path: Path to the dataset YAML config file.
        model_version: Stem of the model filename used in responses.
        pipeline: Loaded sklearn Pipeline object.
        config: Loaded dataset configuration dictionary.

    Example:
        >>> predictor = AQIPredictor()
        >>> response = predictor.predict(request)
        >>> print(response.aqi_rounded)
        187
    """

    def __init__(
        self,
        model_path: Path | None = None,
        dataset_config_path: str | None = None,
    ) -> None:
        """Initialise predictor by loading model and config from disk.

        Args:
            model_path: Optional override for model file path.
                Defaults to models/best_model.pkl.
            dataset_config_path: Optional override for dataset config.
                Defaults to configs/delhi.yaml.

        Raises:
            FileNotFoundError: If model file does not exist at model_path.
                Run 'make train' to generate the model artifact.
        """
        self.model_path = model_path or get_model_path("best_model.pkl")
        self.dataset_config_path = dataset_config_path or str(
            get_config_path("delhi.yaml")
        )
        self.config = load_config(self.dataset_config_path)
        self.pipeline = self._load_pipeline()

        # Stem used in PredictionResponse for traceability
        # e.g. "best_model" or "best_model_tuned"
        self.model_version = self.model_path.stem

        logger.info(
            f"AQIPredictor initialised — "
            f"model: {self.model_version} | "
            f"path: {self.model_path}"
        )

    def _load_pipeline(self):
        """Load the persisted sklearn Pipeline from disk.

        Returns:
            Loaded sklearn Pipeline object.

        Raises:
            FileNotFoundError: If model file does not exist.
        """
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model not found at {self.model_path}. "
                "Run 'make train' to generate the model artifact."
            )

        pipeline = joblib.load(self.model_path)

        logger.debug(f"Pipeline loaded from {self.model_path}")
        return pipeline

    def predict(self, request: PredictionRequest) -> PredictionResponse:
        """Run inference on a single prediction request.

        Converts the API request to a DataFrame, applies feature
        engineering to match the training pipeline, runs the sklearn
        pipeline, inverse-transforms the log prediction, and returns
        a typed PredictionResponse via PredictionAdapter.

        Flow:
            PredictionRequest
                → PredictionAdapter.to_dataframe()
                → engineer_base_features()
                → pipeline.predict()
                → inverse_transform_target()
                → PredictionAdapter.to_response()
                → PredictionResponse

        Args:
            request: Validated PredictionRequest from the API layer.

        Returns:
            PredictionResponse with AQI prediction, category, and metadata.

        Raises:
            ValueError: If feature engineering produces unexpected output.
            RuntimeError: If pipeline prediction fails.
        """
        # Convert API request to raw DataFrame matching dataset column structure
        df = PredictionAdapter.to_dataframe(request)

        # Apply same feature engineering as training pipeline
        # target="aqi" triggers aqi_capped=0 fallback since column is absent
        df = engineer_base_features(df, target="aqi")

        # Run sklearn pipeline — handles scaling, encoding, prediction internally
        log_prediction = self.pipeline.predict(df)

        # Inverse log-transform to get AQI on original 0-500 scale
        aqi_predicted = float(inverse_transform_target(log_prediction)[0])

        return PredictionAdapter.to_response(aqi_predicted, self.model_version)
