"""Prediction service for making stock predictions using trained models"""
import os
import json
import glob
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session

from app.ml.features import FeatureEngineering
from app.ml.models.lstm_model import LSTMPredictor
from app.ml.models.xgboost_model import XGBoostPredictor

logger = logging.getLogger(__name__)


class ModelRegistry:
    """Registry for managing trained models"""

    def __init__(self, model_dir: str = "/app/ml/artifacts"):
        """
        Args:
            model_dir: Directory containing model files
        """
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)

    def list_models(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all available models

        Args:
            symbol: Filter by symbol (optional)

        Returns:
            List of model metadata dictionaries
        """
        pattern = f"{symbol}_*.json" if symbol else "*.json"
        metadata_files = glob.glob(os.path.join(self.model_dir, pattern))

        models = []
        for metadata_file in metadata_files:
            if '_metadata.json' in metadata_file:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    models.append(metadata)

        # Sort by timestamp (newest first)
        models.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        return models

    def get_latest_model(
        self,
        symbol: str,
        model_type: Optional[str] = None,
        target_type: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get the latest model for a symbol

        Args:
            symbol: Stock symbol
            model_type: Filter by model type (optional)
            target_type: Filter by target type (optional)

        Returns:
            Model metadata or None
        """
        models = self.list_models(symbol)

        # Filter by model type and target type
        if model_type:
            models = [m for m in models if m.get('model_type') == model_type]
        if target_type:
            models = [m for m in models if m.get('target_type') == target_type]

        return models[0] if models else None

    def load_model(self, model_path: str, model_type: str):
        """
        Load a model from file

        Args:
            model_path: Path to model file
            model_type: Type of model ('xgboost' or 'lstm')

        Returns:
            Loaded model object
        """
        if model_type.lower() == 'xgboost':
            model = XGBoostPredictor()
            model.load_model(model_path)
        elif model_type.lower() == 'lstm':
            model = LSTMPredictor(input_size=1)  # Will be overridden by load
            model.load_model(model_path)
        else:
            raise ValueError(f"Unknown model type: {model_type}")

        logger.info(f"Loaded {model_type} model from {model_path}")
        return model


class PredictionService:
    """Service for making stock price predictions"""

    def __init__(self, model_dir: str = "/app/ml/artifacts"):
        """
        Args:
            model_dir: Directory containing model files
        """
        self.registry = ModelRegistry(model_dir)
        self.model_cache = {}  # Cache loaded models

    def _prepare_features(
        self,
        db: Session,
        symbol: str,
        days: int,
        horizon: int,
        target_type: str
    ) -> pd.DataFrame:
        """
        Prepare features for prediction

        Args:
            db: Database session
            symbol: Stock symbol
            days: Days of historical data
            horizon: Prediction horizon
            target_type: Type of target

        Returns:
            DataFrame with features
        """
        df = FeatureEngineering.create_all_features(
            db, symbol, days, horizon, target_type
        )

        if df.empty:
            raise ValueError(f"No data available for {symbol}")

        return df

    def predict(
        self,
        db: Session,
        symbol: str,
        model_type: str = 'xgboost',
        target_type: str = 'returns',
        horizon: int = 1,
        days: int = 500
    ) -> Dict[str, Any]:
        """
        Make prediction for a symbol

        Args:
            db: Database session
            symbol: Stock symbol
            model_type: Type of model to use
            target_type: Type of prediction
            horizon: Prediction horizon in days
            days: Days of historical data to use

        Returns:
            Dictionary with prediction results
        """
        # Get latest model
        model_metadata = self.registry.get_latest_model(
            symbol, model_type, target_type
        )

        if not model_metadata:
            raise ValueError(
                f"No {model_type} model found for {symbol} "
                f"with target_type={target_type}"
            )

        model_path = model_metadata['model_path']

        # Load model (use cache if available)
        cache_key = f"{symbol}_{model_type}_{target_type}"
        if cache_key not in self.model_cache:
            model = self.registry.load_model(model_path, model_type)
            self.model_cache[cache_key] = model
        else:
            model = self.model_cache[cache_key]

        # Prepare features
        df = self._prepare_features(db, symbol, days, horizon, target_type)

        # Get feature columns from metadata
        feature_cols = model_metadata['features']

        # Scale features
        X = df[feature_cols].values
        X_scaled, scaler = FeatureEngineering.scale_features(
            pd.DataFrame(X, columns=feature_cols),
            feature_cols=feature_cols
        )
        X_scaled = X_scaled[feature_cols].values

        # Make prediction on the most recent data
        if model_type.lower() == 'lstm':
            # For LSTM, need enough sequence length
            sequence_length = model.sequence_length
            if len(X_scaled) < sequence_length:
                raise ValueError(
                    f"Not enough data for LSTM prediction. "
                    f"Need at least {sequence_length} samples"
                )
            prediction = model.predict(X_scaled)[-1]  # Latest prediction
        else:
            # For XGBoost, predict on last row
            prediction = model.predict(X_scaled[-1:].reshape(1, -1))[0]

        # Get current price
        current_price = float(df['close'].iloc[-1])

        # Interpret prediction based on target type
        result = {
            'symbol': symbol,
            'model_type': model_type,
            'target_type': target_type,
            'horizon': horizon,
            'current_price': current_price,
            'prediction': float(prediction),
            'timestamp': datetime.now().isoformat(),
            'model_metadata': {
                'trained_at': model_metadata.get('timestamp'),
                'test_rmse': model_metadata.get('test_metrics', {}).get('rmse'),
                'test_r2': model_metadata.get('test_metrics', {}).get('r2')
            }
        }

        # Add interpretation
        if target_type == 'returns':
            predicted_price = current_price * (1 + prediction)
            result['predicted_price'] = float(predicted_price)
            result['predicted_return'] = float(prediction * 100)  # As percentage
            result['direction'] = 'UP' if prediction > 0 else 'DOWN'
        elif target_type == 'price':
            result['predicted_price'] = float(prediction)
            result['predicted_return'] = float((prediction - current_price) / current_price * 100)
            result['direction'] = 'UP' if prediction > current_price else 'DOWN'
        elif target_type == 'direction':
            result['direction'] = 'UP' if prediction > 0.5 else 'DOWN'
            result['confidence'] = float(abs(prediction - 0.5) * 2)  # 0-1 scale

        return result

    def predict_multiple_horizons(
        self,
        db: Session,
        symbol: str,
        horizons: List[int] = [1, 5, 10, 20],
        model_type: str = 'xgboost',
        target_type: str = 'returns'
    ) -> Dict[str, Any]:
        """
        Make predictions for multiple time horizons

        Args:
            db: Database session
            symbol: Stock symbol
            horizons: List of prediction horizons
            model_type: Type of model to use
            target_type: Type of prediction

        Returns:
            Dictionary with multi-horizon predictions
        """
        predictions = {}

        for horizon in horizons:
            try:
                pred = self.predict(
                    db, symbol, model_type, target_type, horizon
                )
                predictions[f'{horizon}d'] = pred
            except Exception as e:
                logger.warning(f"Could not predict {horizon}-day for {symbol}: {e}")
                predictions[f'{horizon}d'] = {'error': str(e)}

        return {
            'symbol': symbol,
            'model_type': model_type,
            'target_type': target_type,
            'predictions': predictions,
            'timestamp': datetime.now().isoformat()
        }

    def get_model_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get information about available models for a symbol

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary with model information
        """
        models = self.registry.list_models(symbol)

        return {
            'symbol': symbol,
            'models_available': len(models),
            'models': [
                {
                    'model_type': m['model_type'],
                    'target_type': m['target_type'],
                    'horizon': m['horizon'],
                    'trained_at': m['timestamp'],
                    'test_rmse': m.get('test_metrics', {}).get('rmse'),
                    'test_r2': m.get('test_metrics', {}).get('r2'),
                    'n_features': m['n_features']
                }
                for m in models
            ]
        }
