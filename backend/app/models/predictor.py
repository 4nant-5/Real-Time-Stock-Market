"""
ML Model wrapper — loads the trained model and makes predictions.
"""
import os
import joblib
import numpy as np
from app.config import MODEL_PATH, SCALER_PATH
from app.utils.logger import setup_logger

logger = setup_logger("predictor")


class StockPredictor:
    """Wraps the trained RandomForest model for inference."""

    def __init__(self):
        self.model = None
        self.scaler = None
        self._loaded = False

    def load(self):
        """Load the trained model and scaler from disk."""
        model_path = os.path.abspath(MODEL_PATH)
        scaler_path = os.path.abspath(SCALER_PATH)

        if not os.path.exists(model_path):
            logger.error(f"Model file not found: {model_path}")
            logger.error("Run 'python training/train_model.py' first!")
            return False

        if not os.path.exists(scaler_path):
            logger.error(f"Scaler file not found: {scaler_path}")
            return False

        try:
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            self._loaded = True
            logger.info("✓ Model and scaler loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def predict(self, features: np.ndarray) -> float:
        """
        Predict the next price given a feature vector.

        Args:
            features: Scaled feature array (1, n_features)

        Returns:
            Predicted price as float
        """
        if not self._loaded:
            logger.error("Model not loaded — call load() first")
            return 0.0

        try:
            prediction = self.model.predict(features)
            return float(prediction[0])
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return 0.0

    def generate_signal(self, predicted_price: float, current_price: float) -> str:
        """
        Generate a trading signal based on predicted vs current price.

        Returns: 'BUY', 'SELL', or 'HOLD'
        """
        if current_price <= 0:
            return "HOLD"

        change_pct = ((predicted_price - current_price) / current_price) * 100

        if change_pct > 0.5:
            return "BUY"
        elif change_pct < -0.5:
            return "SELL"
        else:
            return "HOLD"

    def get_confidence(self, features: np.ndarray) -> float:
        """
        Estimate prediction confidence using tree variance.

        Returns: Confidence score 0.0 to 1.0
        """
        if not self._loaded:
            return 0.0

        try:
            # Get predictions from all trees
            tree_predictions = np.array([
                tree.predict(features)[0]
                for tree in self.model.estimators_
            ])

            # Lower variance = higher confidence
            std = np.std(tree_predictions)
            mean = np.mean(tree_predictions)

            # Normalize: coefficient of variation → confidence
            if mean == 0:
                return 0.5

            cv = std / abs(mean)
            confidence = max(0.0, min(1.0, 1.0 - cv * 10))
            return round(confidence, 3)

        except Exception:
            return 0.5


# Singleton instance
predictor = StockPredictor()
