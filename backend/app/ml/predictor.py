"""Model inference engine for house price prediction.

Loads the trained model bundle and provides prediction functionality
with confidence intervals and feature importance explanations.
"""

import os
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd

from app.core.config import get_settings
from app.core.logging import logger


class PredictionEngine:
    """Singleton engine for loading and running the trained model.

    Attributes:
        model: The trained sklearn model.
        scaler: StandardScaler used during training.
        label_encoder: LabelEncoder for location feature.
        features: List of feature column names.
        location_classes: Valid location names.
        location_stats: Per-location price statistics.
        model_metrics: Model evaluation metrics.
        feature_importance: Feature importance from training.
    """

    _instance: Optional["PredictionEngine"] = None

    def __new__(cls) -> "PredictionEngine":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.features: List[str] = []
        self.location_classes: List[str] = []
        self.location_stats: Dict[str, Any] = {}
        self.model_metrics: Dict[str, Any] = {}
        self.feature_importance: Dict[str, float] = {}

    def load_model(self, model_path: Optional[str] = None) -> None:
        """Load the trained model bundle from disk.

        Args:
            model_path: Path to the .joblib model file. Falls back to
                the configured MODEL_PATH in settings.

        Raises:
            FileNotFoundError: If the model file doesn't exist.
            RuntimeError: If the model bundle is corrupted.
        """
        if model_path is None:
            model_path = get_settings().model_path

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model file not found at: {model_path}. "
                f"Run 'python -m app.ml.train' to train the model first."
            )

        logger.info(f"Loading model from: {model_path}")
        bundle = joblib.load(model_path)

        self.model = bundle["model"]
        self.scaler = bundle["scaler"]
        self.label_encoder = bundle["label_encoder"]
        self.features = bundle["features"]
        self.location_classes = bundle["location_classes"]
        self.location_stats = bundle.get("location_stats", {})
        self.model_metrics = {
            "train": bundle.get("train_metrics", {}),
            "test": bundle.get("test_metrics", {}),
        }
        self.feature_importance = bundle.get("feature_importance", {})

        logger.info(
            f"Model loaded successfully. "
            f"Locations: {self.location_classes}, "
            f"Features: {self.features}"
        )

    def is_loaded(self) -> bool:
        """Check whether the model is loaded and ready for predictions."""
        return self.model is not None

    def predict(
        self,
        location: str,
        area_sqft: float,
        bhk: int,
        bathrooms: int,
        floor: int,
        total_floors: int,
        age_of_property: float,
        parking: int,
        lift: int,
    ) -> Dict[str, Any]:
        """Generate a price prediction with confidence interval.

        Args:
            location: Navi Mumbai location/node name.
            area_sqft: Carpet area in square feet.
            bhk: Number of bedrooms (1-6).
            bathrooms: Number of bathrooms (1-6).
            floor: Floor number (0 for ground).
            total_floors: Total floors in the building.
            age_of_property: Age in years.
            parking: 1 if parking available, 0 otherwise.
            lift: 1 if lift available, 0 otherwise.

        Returns:
            Dictionary with predicted_price, price_range, price_per_sqft,
            confidence_score, and feature_contributions.

        Raises:
            RuntimeError: If the model is not loaded.
            ValueError: If the location is not recognized.
        """
        if not self.is_loaded():
            raise RuntimeError("Model is not loaded. Call load_model() first.")

        # Validate location
        if location not in self.location_classes:
            raise ValueError(
                f"Unknown location: '{location}'. "
                f"Valid locations: {self.location_classes}"
            )

        # Encode location
        location_encoded = self.label_encoder.transform([location])[0]

        # Build feature vector
        feature_values = {
            "location": location_encoded,
            "area_sqft": area_sqft,
            "bhk": bhk,
            "bathrooms": bathrooms,
            "floor": floor,
            "total_floors": total_floors,
            "age_of_property": age_of_property,
            "parking": parking,
            "lift": lift,
        }

        input_df = pd.DataFrame([feature_values], columns=self.features)

        # Scale
        input_scaled = self.scaler.transform(input_df)

        # Predict
        predicted_price = float(self.model.predict(input_scaled)[0])

        # Estimate confidence interval using staged predictions
        # (GBR supports staged_predict for ensemble uncertainty estimation)
        staged_predictions = list(self.model.staged_predict(input_scaled))
        last_n = staged_predictions[-20:]  # Last 20 boosting iterations
        std_dev = float(np.std([p[0] for p in last_n]))

        # Confidence score based on how stable the predictions are
        # across the last boosting stages
        max_std = predicted_price * 0.15  # 15% is our max acceptable std
        confidence_score = max(0.5, min(1.0, 1.0 - (std_dev / max_std)))

        # Price range: ±8-12% based on confidence
        margin = 0.08 + (1 - confidence_score) * 0.04
        price_low = predicted_price * (1 - margin)
        price_high = predicted_price * (1 + margin)

        # Price per square foot
        price_per_sqft = predicted_price / area_sqft if area_sqft > 0 else 0

        # Location context
        loc_stats = self.location_stats.get(location, {})

        result = {
            "predicted_price": round(predicted_price, 0),
            "price_range": {
                "low": round(price_low, 0),
                "high": round(price_high, 0),
            },
            "price_per_sqft": round(price_per_sqft, 0),
            "confidence_score": round(confidence_score, 2),
            "location_context": {
                "name": location,
                "avg_price": loc_stats.get("mean_price", 0),
                "median_price": loc_stats.get("median_price", 0),
                "avg_price_per_sqft": loc_stats.get("avg_price_per_sqft", 0),
                "data_points": loc_stats.get("count", 0),
            },
            "feature_importance": self.feature_importance,
            "input_summary": {
                "location": location,
                "area_sqft": area_sqft,
                "bhk": bhk,
                "bathrooms": bathrooms,
                "floor": floor,
                "total_floors": total_floors,
                "age_of_property": age_of_property,
                "parking": bool(parking),
                "lift": bool(lift),
            },
        }

        logger.info(
            f"Prediction for {location}, {area_sqft}sqft, {bhk}BHK: "
            f"₹{predicted_price:,.0f} (confidence: {confidence_score:.2f})"
        )

        return result

    def get_locations(self) -> List[Dict[str, Any]]:
        """Return all valid locations with their statistics.

        Returns:
            List of location objects with name, stats, and price ranges.
        """
        locations = []
        for loc in sorted(self.location_classes):
            stats = self.location_stats.get(loc, {})
            locations.append({
                "name": loc,
                "count": stats.get("count", 0),
                "avg_price": stats.get("mean_price", 0),
                "median_price": stats.get("median_price", 0),
                "min_price": stats.get("min_price", 0),
                "max_price": stats.get("max_price", 0),
                "avg_price_per_sqft": stats.get("avg_price_per_sqft", 0),
            })
        return locations

    def get_model_info(self) -> Dict[str, Any]:
        """Return model metadata and performance metrics.

        Returns:
            Dictionary with model type, metrics, features, and stats.
        """
        return {
            "model_type": "Gradient Boosting Regressor",
            "features": self.features,
            "feature_importance": self.feature_importance,
            "metrics": self.model_metrics,
            "locations_count": len(self.location_classes),
            "locations": self.location_classes,
        }


# Module-level singleton
engine = PredictionEngine()
