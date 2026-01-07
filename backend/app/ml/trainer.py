"""Model training pipeline"""
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, Optional
from datetime import datetime
import logging
import os
import json
from sqlalchemy.orm import Session

from app.ml.features import FeatureEngineering
from app.ml.models.lstm_model import LSTMPredictor
from app.ml.models.xgboost_model import XGBoostPredictor

logger = logging.getLogger(__name__)


class ModelTrainer:
    """Pipeline for training stock prediction models"""

    def __init__(
        self,
        model_dir: str = "/app/ml/artifacts",
        test_size: float = 0.2,
        val_size: float = 0.1,
        random_state: int = 42
    ):
        """
        Args:
            model_dir: Directory to save models
            test_size: Proportion of data for testing
            val_size: Proportion of training data for validation
            random_state: Random seed
        """
        self.model_dir = model_dir
        self.test_size = test_size
        self.val_size = val_size
        self.random_state = random_state

        # Create model directory if it doesn't exist
        os.makedirs(model_dir, exist_ok=True)

    def prepare_data(
        self,
        df: pd.DataFrame,
        target_col: str = 'target'
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, list]:
        """
        Split and prepare data for training

        Args:
            df: DataFrame with features and target
            target_col: Name of target column

        Returns:
            Tuple of (X_train, X_val, X_test, y_train, y_val, y_test, feature_cols)
        """
        # Get feature columns (exclude target and non-feature columns)
        exclude_cols = ['target', 'open', 'high', 'low', 'close', 'volume']
        feature_cols = [col for col in df.columns if col not in exclude_cols]

        # Extract features and target
        X = df[feature_cols].values
        y = df[target_col].values

        # Time series split (maintain temporal order)
        n_samples = len(X)
        test_idx = int(n_samples * (1 - self.test_size))
        train_val_idx = int(test_idx * (1 - self.val_size))

        X_train = X[:train_val_idx]
        X_val = X[train_val_idx:test_idx]
        X_test = X[test_idx:]

        y_train = y[:train_val_idx]
        y_val = y[train_val_idx:test_idx]
        y_test = y[test_idx:]

        logger.info(f"Data split - Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
        logger.info(f"Number of features: {len(feature_cols)}")

        return X_train, X_val, X_test, y_train, y_val, y_test, feature_cols

    def train_xgboost(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray,
        **kwargs
    ) -> XGBoostPredictor:
        """
        Train XGBoost model

        Args:
            X_train: Training features
            y_train: Training targets
            X_val: Validation features
            y_val: Validation targets
            **kwargs: Additional parameters for XGBoostPredictor

        Returns:
            Trained XGBoostPredictor
        """
        logger.info("Training XGBoost model...")

        model = XGBoostPredictor(**kwargs)
        model.train(X_train, y_train, X_val, y_val, verbose=True)

        return model

    def train_lstm(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray,
        input_size: int,
        **kwargs
    ) -> LSTMPredictor:
        """
        Train LSTM model

        Args:
            X_train: Training features
            y_train: Training targets
            X_val: Validation features
            y_val: Validation targets
            input_size: Number of input features
            **kwargs: Additional parameters for LSTMPredictor

        Returns:
            Trained LSTMPredictor
        """
        logger.info("Training LSTM model...")

        model = LSTMPredictor(input_size=input_size, **kwargs)
        model.train(X_train, y_train, X_val, y_val, verbose=True)

        return model

    def train_model(
        self,
        db: Session,
        symbol: str,
        model_type: str = 'xgboost',
        days: int = 500,
        horizon: int = 1,
        target_type: str = 'returns',
        save_model: bool = True,
        **model_params
    ) -> Dict[str, Any]:
        """
        Complete training pipeline for a symbol

        Args:
            db: Database session
            symbol: Stock symbol
            model_type: Type of model ('xgboost' or 'lstm')
            days: Days of historical data
            horizon: Prediction horizon
            target_type: Type of target ('returns', 'price', 'direction')
            save_model: Whether to save the trained model
            **model_params: Additional model parameters

        Returns:
            Dictionary with training results
        """
        logger.info(f"Starting training pipeline for {symbol}")
        logger.info(f"Model type: {model_type}, Horizon: {horizon}, Target: {target_type}")

        # Create features
        df = FeatureEngineering.create_all_features(
            db, symbol, days, horizon, target_type
        )

        if df.empty:
            raise ValueError(f"No data available for {symbol}")

        logger.info(f"Created {len(df)} samples with {len(df.columns)} features")

        # Prepare data
        X_train, X_val, X_test, y_train, y_val, y_test, feature_cols = \
            self.prepare_data(df)

        # Scale features
        X_train_scaled, X_val_scaled, scaler = FeatureEngineering.scale_features(
            pd.DataFrame(X_train, columns=feature_cols),
            pd.DataFrame(X_val, columns=feature_cols),
            feature_cols
        )
        X_test_scaled, _ = FeatureEngineering.scale_features(
            pd.DataFrame(X_test, columns=feature_cols),
            test_df=None,
            feature_cols=feature_cols
        )

        # Convert back to arrays
        X_train_scaled = X_train_scaled[feature_cols].values
        X_val_scaled = X_val_scaled[feature_cols].values
        X_test_scaled = X_test_scaled[feature_cols].values

        # Train model
        if model_type.lower() == 'xgboost':
            model = self.train_xgboost(
                X_train_scaled, y_train,
                X_val_scaled, y_val,
                **model_params
            )
        elif model_type.lower() == 'lstm':
            model = self.train_lstm(
                X_train_scaled, y_train,
                X_val_scaled, y_val,
                input_size=len(feature_cols),
                **model_params
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")

        # Evaluate on test set
        test_metrics = model.evaluate(X_test_scaled, y_test)
        logger.info(f"Test metrics: {test_metrics}")

        # Save model if requested
        if save_model:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_filename = f"{symbol}_{model_type}_{target_type}_{timestamp}.pkl"
            model_path = os.path.join(self.model_dir, model_filename)

            model.save_model(model_path)

            # Save metadata
            metadata = {
                'symbol': symbol,
                'model_type': model_type,
                'target_type': target_type,
                'horizon': horizon,
                'days': days,
                'features': feature_cols,
                'n_features': len(feature_cols),
                'train_samples': len(X_train),
                'val_samples': len(X_val),
                'test_samples': len(X_test),
                'test_metrics': test_metrics,
                'timestamp': timestamp,
                'model_path': model_path
            }

            metadata_path = model_path.replace('.pkl', '_metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"Model saved to {model_path}")
            logger.info(f"Metadata saved to {metadata_path}")

            # Get feature importance for XGBoost
            if model_type.lower() == 'xgboost':
                importance_df = model.get_feature_importance(feature_cols, top_n=20)
                logger.info(f"\nTop 20 Features:\n{importance_df}")

                importance_path = model_path.replace('.pkl', '_importance.csv')
                importance_df.to_csv(importance_path, index=False)

        return {
            'symbol': symbol,
            'model_type': model_type,
            'test_metrics': test_metrics,
            'n_features': len(feature_cols),
            'model_path': model_path if save_model else None
        }

    def train_multiple_symbols(
        self,
        db: Session,
        symbols: list,
        model_type: str = 'xgboost',
        **kwargs
    ) -> Dict[str, Dict[str, Any]]:
        """
        Train models for multiple symbols

        Args:
            db: Database session
            symbols: List of stock symbols
            model_type: Type of model
            **kwargs: Additional parameters

        Returns:
            Dictionary mapping symbols to training results
        """
        results = {}

        for symbol in symbols:
            try:
                logger.info(f"\n{'='*60}")
                logger.info(f"Training model for {symbol}")
                logger.info(f"{'='*60}")

                result = self.train_model(db, symbol, model_type, **kwargs)
                results[symbol] = result

                logger.info(f"✓ {symbol}: RMSE={result['test_metrics']['rmse']:.6f}, "
                           f"R²={result['test_metrics']['r2']:.4f}")

            except Exception as e:
                logger.error(f"✗ Error training {symbol}: {e}")
                results[symbol] = {'error': str(e)}

        return results
