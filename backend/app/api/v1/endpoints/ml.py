"""ML prediction endpoints"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.db import get_db
from app.ml.prediction_service import PredictionService
from app.ml.trainer import ModelTrainer
from app.ml.backtest import Backtester
from app.ml.features import FeatureEngineering
from app.schemas import ml as ml_schemas
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
prediction_service = PredictionService()
model_trainer = ModelTrainer()


@router.get("/{symbol}/predict", response_model=ml_schemas.PredictionResponse)
def predict_stock(
    symbol: str,
    model_type: str = 'xgboost',
    target_type: str = 'returns',
    horizon: int = 1,
    db: Session = Depends(get_db)
):
    """
    Make a price prediction for a stock

    Args:
        symbol: Stock symbol
        model_type: Type of model ('xgboost' or 'lstm')
        target_type: Type of prediction ('returns', 'price', 'direction')
        horizon: Prediction horizon in days
        db: Database session

    Returns:
        Prediction result
    """
    try:
        result = prediction_service.predict(
            db, symbol, model_type, target_type, horizon
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error making prediction for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/predict/multi-horizon", response_model=ml_schemas.MultiHorizonPrediction)
def predict_multi_horizon(
    symbol: str,
    model_type: str = 'xgboost',
    target_type: str = 'returns',
    db: Session = Depends(get_db)
):
    """
    Make predictions for multiple time horizons

    Args:
        symbol: Stock symbol
        model_type: Type of model
        target_type: Type of prediction
        db: Database session

    Returns:
        Multi-horizon predictions
    """
    try:
        result = prediction_service.predict_multiple_horizons(
            db, symbol, [1, 5, 10, 20], model_type, target_type
        )
        return result
    except Exception as e:
        logger.error(f"Error making multi-horizon prediction for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/models", response_model=ml_schemas.ModelListResponse)
def get_models(symbol: str):
    """
    Get information about available models for a symbol

    Args:
        symbol: Stock symbol

    Returns:
        List of available models
    """
    try:
        result = prediction_service.get_model_info(symbol)
        return result
    except Exception as e:
        logger.error(f"Error getting models for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{symbol}/train", response_model=ml_schemas.TrainingResponse)
def train_model(
    symbol: str,
    request: ml_schemas.TrainingRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Train a new model for a symbol

    Args:
        symbol: Stock symbol
        request: Training configuration
        background_tasks: Background tasks handler
        db: Database session

    Returns:
        Training result
    """
    try:
        # For long training, could run in background
        # For now, run synchronously
        result = model_trainer.train_model(
            db,
            symbol,
            model_type=request.model_type,
            days=request.days,
            horizon=request.horizon,
            target_type=request.target_type,
            save_model=True
        )

        return {
            **result,
            'message': f"Model trained successfully for {symbol}"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error training model for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{symbol}/backtest", response_model=ml_schemas.BacktestResponse)
def run_backtest(
    symbol: str,
    model_type: str = 'xgboost',
    target_type: str = 'returns',
    horizon: int = 1,
    strategy: str = 'simple',
    threshold: float = 0.0,
    db: Session = Depends(get_db)
):
    """
    Run backtest for a trained model

    Args:
        symbol: Stock symbol
        model_type: Type of model
        target_type: Type of prediction
        horizon: Prediction horizon
        strategy: Trading strategy
        threshold: Strategy threshold
        db: Database session

    Returns:
        Backtest results
    """
    try:
        # Get model
        model_metadata = prediction_service.registry.get_latest_model(
            symbol, model_type, target_type
        )

        if not model_metadata:
            raise HTTPException(
                status_code=404,
                detail=f"No model found for {symbol}"
            )

        # Load model
        model = prediction_service.registry.load_model(
            model_metadata['model_path'],
            model_type
        )

        # Prepare data
        df = FeatureEngineering.create_all_features(
            db, symbol, 500, horizon, target_type
        )

        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data for {symbol}")

        # Get features
        feature_cols = model_metadata['features']
        X = df[feature_cols].values
        y = df['target'].values
        prices = df['close'].values

        # Scale features
        X_scaled, _ = FeatureEngineering.scale_features(
            pd.DataFrame(X, columns=feature_cols),
            feature_cols=feature_cols
        )
        X_scaled = X_scaled[feature_cols].values

        # Make predictions
        predictions = model.predict(X_scaled)

        # Align arrays (account for sequence length if LSTM)
        if model_type.lower() == 'lstm':
            seq_len = model.sequence_length
            predictions_aligned = predictions[:len(y) - seq_len]
            y_aligned = y[seq_len:]
            prices_aligned = prices[seq_len:]
        else:
            predictions_aligned = predictions
            y_aligned = y
            prices_aligned = prices

        # Run backtest
        backtester = Backtester()
        result = backtester.run_backtest(
            predictions_aligned,
            y_aligned,
            prices_aligned,
            strategy=strategy,
            threshold=threshold
        )

        # Remove detailed returns from response (can be large)
        result_clean = {
            'symbol': symbol,
            'strategy': result['strategy'],
            'strategy_params': result['strategy_params'],
            'metrics': result['metrics']
        }

        return result_clean

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running backtest for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/feature-importance", response_model=ml_schemas.FeatureImportanceResponse)
def get_feature_importance(
    symbol: str,
    model_type: str = 'xgboost',
    target_type: str = 'returns',
    top_n: int = 20
):
    """
    Get feature importance for a trained XGBoost model

    Args:
        symbol: Stock symbol
        model_type: Type of model (must be 'xgboost')
        target_type: Type of prediction
        top_n: Number of top features to return

    Returns:
        Feature importance data
    """
    if model_type.lower() != 'xgboost':
        raise HTTPException(
            status_code=400,
            detail="Feature importance only available for XGBoost models"
        )

    try:
        # Get model
        model_metadata = prediction_service.registry.get_latest_model(
            symbol, model_type, target_type
        )

        if not model_metadata:
            raise HTTPException(
                status_code=404,
                detail=f"No {model_type} model found for {symbol}"
            )

        # Load model
        model = prediction_service.registry.load_model(
            model_metadata['model_path'],
            model_type
        )

        # Get feature importance
        feature_cols = model_metadata['features']
        importance_df = model.get_feature_importance(feature_cols, top_n)

        return {
            'symbol': symbol,
            'model_type': model_type,
            'top_features': importance_df.to_dict('records')
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting feature importance for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Add pandas import for backtest endpoint
import pandas as pd
