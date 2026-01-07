"""Technical indicator schemas"""
from pydantic import BaseModel, Field
from typing import Optional, Dict


class PriceData(BaseModel):
    """Current price data"""
    current: float
    open: float
    high: float
    low: float
    volume: int


class MovingAverages(BaseModel):
    """Moving average indicators"""
    sma_20: Optional[float] = Field(None, description="20-day Simple Moving Average")
    sma_50: Optional[float] = Field(None, description="50-day Simple Moving Average")
    sma_200: Optional[float] = Field(None, description="200-day Simple Moving Average")
    ema_12: Optional[float] = Field(None, description="12-day Exponential Moving Average")
    ema_26: Optional[float] = Field(None, description="26-day Exponential Moving Average")


class Oscillators(BaseModel):
    """Oscillator indicators"""
    rsi_14: Optional[float] = Field(None, description="14-day Relative Strength Index")
    stoch_k: Optional[float] = Field(None, description="Stochastic %K")
    stoch_d: Optional[float] = Field(None, description="Stochastic %D")


class MACDData(BaseModel):
    """MACD indicator data"""
    macd: Optional[float] = Field(None, description="MACD line")
    signal: Optional[float] = Field(None, description="Signal line")
    histogram: Optional[float] = Field(None, description="MACD histogram")


class BollingerBands(BaseModel):
    """Bollinger Bands data"""
    upper: Optional[float] = Field(None, description="Upper band")
    middle: Optional[float] = Field(None, description="Middle band (SMA)")
    lower: Optional[float] = Field(None, description="Lower band")


class TrendIndicators(BaseModel):
    """Trend strength indicators"""
    adx_14: Optional[float] = Field(None, description="14-day Average Directional Index")
    atr_14: Optional[float] = Field(None, description="14-day Average True Range")


class VolumeIndicators(BaseModel):
    """Volume-based indicators"""
    obv: Optional[float] = Field(None, description="On-Balance Volume")


class IndicatorResponse(BaseModel):
    """Complete technical indicators response"""
    symbol: str
    timestamp: Optional[str] = None
    price: PriceData
    moving_averages: MovingAverages
    oscillators: Oscillators
    macd: MACDData
    bollinger_bands: BollingerBands
    trend: TrendIndicators
    volume: VolumeIndicators
    signals: Dict[str, str] = Field(default_factory=dict, description="Trading signals interpretation")
    data_points: int = Field(..., description="Number of data points used")
    period_days: int = Field(..., description="Period in days")


class IndicatorError(BaseModel):
    """Error response for indicators"""
    error: str
    symbol: str
    days_requested: int
