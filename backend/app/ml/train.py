"""Model training pipeline for house price prediction.

Trains a Gradient Boosting Regressor on cleaned Navi Mumbai
real estate data and exports the model with all preprocessing
artifacts needed for inference.
"""

import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import json
from pathlib import Path
from typing import Any, Dict

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_absolute_percentage_error,
    mean_squared_error,
    median_absolute_error,
    r2_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

from app.ml.preprocessing import (
    get_feature_columns,
    get_target_column,
    preprocess_dataset,
)
from app.core.logging import logger


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Compute comprehensive regression metrics.

    Args:
        y_true: Actual target values.
        y_pred: Predicted target values.

    Returns:
        Dictionary of metric names to values.
    """
    return {
        "r2_score": round(r2_score(y_true, y_pred), 4),
        "rmse": round(np.sqrt(mean_squared_error(y_true, y_pred)), 2),
        "mae": round(mean_absolute_error(y_true, y_pred), 2),
        "mape": round(mean_absolute_percentage_error(y_true, y_pred) * 100, 2),
        "median_ae": round(median_absolute_error(y_true, y_pred), 2),
    }


def train_model(data_path: str, output_dir: str = "models") -> Dict[str, Any]:
    """Train the house price prediction model end-to-end.

    Steps:
        1. Load and preprocess raw CSV data
        2. Encode categorical features (location)
        3. Scale numerical features
        4. Train Gradient Boosting Regressor
        5. Evaluate on holdout test set
        6. Save model, scaler, and encoder as a single joblib bundle

    Args:
        data_path: Path to the raw CSV dataset.
        output_dir: Directory to save the trained model artifacts.

    Returns:
        Dictionary containing training results and metrics.
    """
    logger.info(f"Loading data from: {data_path}")
    raw_df = pd.read_csv(data_path)

    # Preprocess
    df, prep_stats = preprocess_dataset(raw_df)

    features = get_feature_columns()
    target = get_target_column()

    X = df[features].copy()
    y = df[target].copy()

    # Encode location (categorical)
    label_encoder = LabelEncoder()
    X["location"] = label_encoder.fit_transform(X["location"])

    location_classes = label_encoder.classes_.tolist()
    logger.info(f"Location classes: {location_classes}")

    # Train/test split (80/20, stratified isn't applicable for regression
    # but we use a fixed random state for reproducibility)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    logger.info(f"Train size: {len(X_train)}, Test size: {len(X_test)}")

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(
        scaler.fit_transform(X_train), columns=features, index=X_train.index
    )
    X_test_scaled = pd.DataFrame(
        scaler.transform(X_test), columns=features, index=X_test.index
    )

    # Train Gradient Boosting Regressor
    model = GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.1,
        max_depth=5,
        min_samples_split=5,
        min_samples_leaf=3,
        subsample=0.9,
        random_state=42,
        validation_fraction=0.1,
        n_iter_no_change=15,
        tol=1e-4,
    )

    logger.info("Training Gradient Boosting Regressor...")
    model.fit(X_train_scaled, y_train)

    # Evaluate
    y_pred_train = model.predict(X_train_scaled)
    y_pred_test = model.predict(X_test_scaled)

    train_metrics = compute_metrics(y_train.values, y_pred_train)
    test_metrics = compute_metrics(y_test.values, y_pred_test)

    logger.info(f"Train metrics: {train_metrics}")
    logger.info(f"Test metrics:  {test_metrics}")

    # Feature importance
    feature_importance = dict(
        zip(features, model.feature_importances_.round(4).tolist())
    )
    logger.info(f"Feature importance: {feature_importance}")

    # Price statistics per location (for frontend display)
    location_stats = {}
    for loc in df["location"].unique():
        loc_data = df[df["location"] == loc]["actual_price"]
        location_stats[loc] = {
            "count": int(len(loc_data)),
            "mean_price": round(float(loc_data.mean()), 0),
            "median_price": round(float(loc_data.median()), 0),
            "min_price": round(float(loc_data.min()), 0),
            "max_price": round(float(loc_data.max()), 0),
            "avg_price_per_sqft": round(
                float(
                    (df[df["location"] == loc]["actual_price"]
                     / df[df["location"] == loc]["area_sqft"]).mean()
                ),
                0,
            ),
        }

    # Save model bundle
    os.makedirs(output_dir, exist_ok=True)
    model_bundle = {
        "model": model,
        "scaler": scaler,
        "label_encoder": label_encoder,
        "features": features,
        "target": target,
        "location_classes": location_classes,
        "location_stats": location_stats,
        "train_metrics": train_metrics,
        "test_metrics": test_metrics,
        "feature_importance": feature_importance,
        "preprocessing_stats": prep_stats,
    }

    model_path = os.path.join(output_dir, "house_price_model.joblib")
    joblib.dump(model_bundle, model_path)
    logger.info(f"Model saved to: {model_path}")

    # Also save metadata as JSON for easy inspection
    metadata = {
        "model_type": "GradientBoostingRegressor",
        "features": features,
        "target": target,
        "location_classes": location_classes,
        "train_metrics": train_metrics,
        "test_metrics": test_metrics,
        "feature_importance": feature_importance,
        "location_stats": location_stats,
        "dataset_stats": {
            "original_rows": prep_stats["original_rows"],
            "cleaned_rows": prep_stats["cleaned_rows"],
            "locations": prep_stats["locations"],
        },
    }

    metadata_path = os.path.join(output_dir, "model_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Metadata saved to: {metadata_path}")

    return {
        "model_path": model_path,
        "train_metrics": train_metrics,
        "test_metrics": test_metrics,
        "feature_importance": feature_importance,
        "location_stats": location_stats,
    }


if __name__ == "__main__":
    # When run directly, train from the project data directory
    project_root = Path(__file__).parent.parent.parent
    data_file = project_root.parent / "navi_mumbai_real_estate_uncleaned_2500.csv"
    model_dir = project_root / "models"

    if not data_file.exists():
        logger.error(f"Data file not found: {data_file}")
        sys.exit(1)

    results = train_model(str(data_file), str(model_dir))
    print("\n=== Training Complete ===")
    print(f"Model saved to: {results['model_path']}")
    print(f"Test R²:   {results['test_metrics']['r2_score']}")
    print(f"Test RMSE: {results['test_metrics']['rmse']}")
    print(f"Test MAPE: {results['test_metrics']['mape']}%")
    print(f"Test MAE:  {results['test_metrics']['mae']}")
