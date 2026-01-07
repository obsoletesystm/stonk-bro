"""Pydantic schemas for ML endpoints"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class ModelMetadata(BaseModel):
    """Model metadata"""
    trained_at: Optional[str] = None
    test_rmse: Optional[float] = None
    test_r2: Optional[float] = None


class PredictionResponse(BaseModel):
    """Single prediction response"""
    symbol: str
    model_type: str
    target_type: str
    horizon: int
    current_price: float
    prediction: float
    predicted_price: Optional[float] = None
    predicted_return: Optional[float] = None
    direction: Optional[str] = None
    confidence: Optional[float] = None
    timestamp: str
    model_metadata: ModelMetadata


class MultiHorizonPrediction(BaseModel):
    """Multi-horizon prediction response"""
    symbol: str
    model_type: str
    target_type: str
    predictions: Dict[str, Any]
    timestamp: str


class ModelInfo(BaseModel):
    """Information about a trained model"""
    model_type: str
    target_type: str
    horizon: int
    trained_at: str
    test_rmse: Optional[float] = None
    test_r2: Optional[float] = None
    n_features: int


class ModelListResponse(BaseModel):
    """List of available models"""
    symbol: str
    models_available: int
    models: List[ModelInfo]


class TrainingRequest(BaseModel):
    """Request to train a model"""
    symbol: str
    model_type: str = Field(default='xgboost', pattern='^(xgboost|lstm)$')
    target_type: str = Field(default='returns', pattern='^(returns|price|direction)$')
    horizon: int = Field(default=1, ge=1, le=30)
    days: int = Field(default=500, ge=100, le=2000)


class TrainingResponse(BaseModel):
    """Training result"""
    symbol: str
    model_type: str
    test_metrics: Dict[str, float]
    n_features: int
    model_path: Optional[str] = None
    message: str = "Model trained successfully"


class BacktestMetrics(BaseModel):
    """Backtest performance metrics"""
    total_return: float
    buy_hold_return: float
    excess_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    calmar_ratio: float
    win_rate: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    total_trades: int
    n_days: int


class BacktestResponse(BaseModel):
    """Backtest result"""
    symbol: str
    strategy: str
    strategy_params: Dict[str, Any]
    metrics: BacktestMetrics
    message: str = "Backtest completed successfully"


class FeatureImportance(BaseModel):
    """Feature importance data"""
    feature: str
    importance: float


class FeatureImportanceResponse(BaseModel):
    """Feature importance response"""
    symbol: str
    model_type: str
    top_features: List[FeatureImportance]
