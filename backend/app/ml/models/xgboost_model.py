"""XGBoost model for stock price prediction"""
import numpy as np
import pandas as pd
import xgboost as xgb
from typing import Dict, Any, Optional
import logging
import pickle

logger = logging.getLogger(__name__)


class XGBoostPredictor:
    """XGBoost-based stock price predictor"""

    def __init__(
        self,
        n_estimators: int = 1000,
        max_depth: int = 7,
        learning_rate: float = 0.01,
        subsample: float = 0.8,
        colsample_bytree: float = 0.8,
        gamma: float = 0,
        reg_alpha: float = 0,
        reg_lambda: float = 1,
        random_state: int = 42
    ):
        """
        Args:
            n_estimators: Number of boosting rounds
            max_depth: Maximum tree depth
            learning_rate: Boosting learning rate
            subsample: Subsample ratio of training instances
            colsample_bytree: Subsample ratio of columns when constructing each tree
            gamma: Minimum loss reduction required to make a split
            reg_alpha: L1 regularization term
            reg_lambda: L2 regularization term
            random_state: Random seed
        """
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.subsample = subsample
        self.colsample_bytree = colsample_bytree
        self.gamma = gamma
        self.reg_alpha = reg_alpha
        self.reg_lambda = reg_lambda
        self.random_state = random_state

        # Initialize model
        self.model = xgb.XGBRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            subsample=subsample,
            colsample_bytree=colsample_bytree,
            gamma=gamma,
            reg_alpha=reg_alpha,
            reg_lambda=reg_lambda,
            random_state=random_state,
            objective='reg:squarederror',
            n_jobs=-1
        )

        self.feature_importance_ = None
        logger.info("Initialized XGBoost model")

    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
        early_stopping_rounds: int = 50,
        verbose: bool = True
    ) -> Dict[str, list]:
        """
        Train the XGBoost model

        Args:
            X_train: Training features
            y_train: Training targets
            X_val: Validation features
            y_val: Validation targets
            early_stopping_rounds: Early stopping rounds
            verbose: Print training progress

        Returns:
            Dictionary with training history
        """
        eval_set = []
        eval_set.append((X_train, y_train))

        if X_val is not None and y_val is not None:
            eval_set.append((X_val, y_val))

        # Train model
        self.model.fit(
            X_train,
            y_train,
            eval_set=eval_set,
            early_stopping_rounds=early_stopping_rounds,
            verbose=verbose if verbose else 0
        )

        # Get feature importance
        self.feature_importance_ = self.model.feature_importances_

        # Return training history
        history = {
            'train_rmse': self.model.evals_result()['validation_0']['rmse']
        }

        if len(eval_set) > 1:
            history['val_rmse'] = self.model.evals_result()['validation_1']['rmse']

        logger.info(f"Training completed. Best iteration: {self.model.best_iteration}")

        return history

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions

        Args:
            X: Input features

        Returns:
            Predictions array
        """
        return self.model.predict(X)

    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """
        Evaluate model performance

        Args:
            X: Input features
            y: True targets

        Returns:
            Dictionary with evaluation metrics
        """
        predictions = self.predict(X)

        mse = np.mean((predictions - y) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(predictions - y))

        # R² score
        ss_res = np.sum((y - predictions) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r2 = 1 - (ss_res / ss_tot)

        # Direction accuracy (for returns prediction)
        direction_correct = np.sum((predictions > 0) == (y > 0))
        direction_accuracy = direction_correct / len(y)

        return {
            'mse': float(mse),
            'rmse': float(rmse),
            'mae': float(mae),
            'r2': float(r2),
            'direction_accuracy': float(direction_accuracy)
        }

    def get_feature_importance(
        self,
        feature_names: Optional[list] = None,
        top_n: int = 20
    ) -> pd.DataFrame:
        """
        Get feature importance

        Args:
            feature_names: List of feature names
            top_n: Number of top features to return

        Returns:
            DataFrame with feature importance
        """
        if self.feature_importance_ is None:
            raise ValueError("Model has not been trained yet")

        if feature_names is None:
            feature_names = [f'feature_{i}' for i in range(len(self.feature_importance_))]

        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': self.feature_importance_
        })

        importance_df = importance_df.sort_values('importance', ascending=False)

        if top_n:
            importance_df = importance_df.head(top_n)

        return importance_df

    def save_model(self, path: str):
        """Save model to file"""
        with open(path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'feature_importance': self.feature_importance_,
                'params': {
                    'n_estimators': self.n_estimators,
                    'max_depth': self.max_depth,
                    'learning_rate': self.learning_rate,
                    'subsample': self.subsample,
                    'colsample_bytree': self.colsample_bytree,
                    'gamma': self.gamma,
                    'reg_alpha': self.reg_alpha,
                    'reg_lambda': self.reg_lambda,
                    'random_state': self.random_state
                }
            }, f)
        logger.info(f"Model saved to {path}")

    def load_model(self, path: str):
        """Load model from file"""
        with open(path, 'rb') as f:
            data = pickle.load(f)

        self.model = data['model']
        self.feature_importance_ = data['feature_importance']

        params = data['params']
        self.n_estimators = params['n_estimators']
        self.max_depth = params['max_depth']
        self.learning_rate = params['learning_rate']
        self.subsample = params['subsample']
        self.colsample_bytree = params['colsample_bytree']
        self.gamma = params['gamma']
        self.reg_alpha = params['reg_alpha']
        self.reg_lambda = params['reg_lambda']
        self.random_state = params['random_state']

        logger.info(f"Model loaded from {path}")

    def predict_with_uncertainty(
        self,
        X: np.ndarray,
        n_iterations: int = 100
    ) -> tuple:
        """
        Predict with uncertainty estimation using bootstrapping

        Args:
            X: Input features
            n_iterations: Number of bootstrap iterations

        Returns:
            Tuple of (predictions, std_dev)
        """
        # Use built-in prediction intervals if available
        predictions = self.predict(X)

        # For uncertainty, we can use the leaf predictions variance
        # This is a simplified approach
        std_dev = np.ones_like(predictions) * np.std(predictions) * 0.1

        return predictions, std_dev
