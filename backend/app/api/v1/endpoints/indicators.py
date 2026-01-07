"""Technical indicators endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Union

from app.core.db import get_db
from app.services.indicator_service import IndicatorService
from app.schemas.indicator import IndicatorResponse, IndicatorError

router = APIRouter()


@router.get("/{symbol}", response_model=Union[IndicatorResponse, IndicatorError])
def get_indicators(
    symbol: str,
    days: int = Query(100, ge=20, le=365, description="Days of historical data to use"),
    db: Session = Depends(get_db)
):
    """
    Get all technical indicators for a symbol

    Calculates and returns comprehensive technical analysis including:
    - **Moving Averages**: SMA (20, 50, 200), EMA (12, 26)
    - **Oscillators**: RSI (14), Stochastic (K, D)
    - **MACD**: MACD line, Signal line, Histogram
    - **Bollinger Bands**: Upper, Middle, Lower
    - **Trend**: ADX (14), ATR (14)
    - **Volume**: OBV (On-Balance Volume)
    - **Signals**: Interpreted trading signals

    **Parameters:**
    - **symbol**: Stock symbol (e.g., AAPL, GOOGL)
    - **days**: Number of days of historical data to use (20-365, default: 100)

    **Returns:**
    Complete technical analysis with current values and interpretations
    """
    result = IndicatorService.calculate_all_indicators(db, symbol, days)

    if 'error' in result:
        raise HTTPException(status_code=404, detail=result['error'])

    return result


@router.get("/{symbol}/sma", response_model=dict)
def get_sma(
    symbol: str,
    period: int = Query(20, ge=2, le=200, description="SMA period"),
    days: int = Query(100, ge=20, le=365, description="Days of historical data"),
    db: Session = Depends(get_db)
):
    """
    Get Simple Moving Average for a symbol

    **Parameters:**
    - **symbol**: Stock symbol
    - **period**: SMA period (2-200, default: 20)
    - **days**: Days of historical data (20-365, default: 100)
    """
    df = IndicatorService.get_historical_data(db, symbol, days)

    if df.empty:
        raise HTTPException(status_code=404, detail="No historical data found")

    sma = IndicatorService.calculate_sma(df, period)

    if sma.empty:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient data for SMA({period}). Need at least {period} data points."
        )

    return {
        'symbol': symbol.upper(),
        'indicator': f'SMA_{period}',
        'current_value': float(sma.iloc[-1]),
        'values': [
            {'timestamp': idx.isoformat(), 'value': float(val)}
            for idx, val in sma.dropna().items()
        ][-30:]  # Last 30 values
    }


@router.get("/{symbol}/rsi", response_model=dict)
def get_rsi(
    symbol: str,
    period: int = Query(14, ge=2, le=50, description="RSI period"),
    days: int = Query(100, ge=20, le=365, description="Days of historical data"),
    db: Session = Depends(get_db)
):
    """
    Get Relative Strength Index for a symbol

    **Parameters:**
    - **symbol**: Stock symbol
    - **period**: RSI period (2-50, default: 14)
    - **days**: Days of historical data (20-365, default: 100)

    **Interpretation:**
    - RSI > 70: Overbought
    - RSI < 30: Oversold
    - RSI 30-70: Neutral
    """
    df = IndicatorService.get_historical_data(db, symbol, days)

    if df.empty:
        raise HTTPException(status_code=404, detail="No historical data found")

    rsi = IndicatorService.calculate_rsi(df, period)

    if rsi.empty:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient data for RSI({period})"
        )

    current_rsi = float(rsi.iloc[-1])

    # Generate signal
    if current_rsi > 70:
        signal = "Overbought"
    elif current_rsi < 30:
        signal = "Oversold"
    else:
        signal = "Neutral"

    return {
        'symbol': symbol.upper(),
        'indicator': f'RSI_{period}',
        'current_value': current_rsi,
        'signal': signal,
        'values': [
            {'timestamp': idx.isoformat(), 'value': float(val)}
            for idx, val in rsi.dropna().items()
        ][-30:]  # Last 30 values
    }


@router.get("/{symbol}/macd", response_model=dict)
def get_macd(
    symbol: str,
    fast: int = Query(12, ge=2, le=50, description="Fast period"),
    slow: int = Query(26, ge=2, le=100, description="Slow period"),
    signal: int = Query(9, ge=2, le=50, description="Signal period"),
    days: int = Query(100, ge=50, le=365, description="Days of historical data"),
    db: Session = Depends(get_db)
):
    """
    Get MACD (Moving Average Convergence Divergence)

    **Parameters:**
    - **symbol**: Stock symbol
    - **fast**: Fast EMA period (default: 12)
    - **slow**: Slow EMA period (default: 26)
    - **signal**: Signal line period (default: 9)
    - **days**: Days of historical data (50-365, default: 100)
    """
    df = IndicatorService.get_historical_data(db, symbol, days)

    if df.empty:
        raise HTTPException(status_code=404, detail="No historical data found")

    macd_data = IndicatorService.calculate_macd(df, fast, slow, signal)

    if macd_data['macd'].empty:
        raise HTTPException(status_code=400, detail="Insufficient data for MACD")

    current_macd = float(macd_data['macd'].iloc[-1])
    current_signal = float(macd_data['signal'].iloc[-1])
    current_hist = float(macd_data['histogram'].iloc[-1])

    # Generate signal
    if current_macd > current_signal:
        trend_signal = "Bullish (MACD > Signal)"
    else:
        trend_signal = "Bearish (MACD < Signal)"

    return {
        'symbol': symbol.upper(),
        'indicator': f'MACD({fast},{slow},{signal})',
        'current_values': {
            'macd': current_macd,
            'signal': current_signal,
            'histogram': current_hist
        },
        'signal': trend_signal,
        'values': [
            {
                'timestamp': idx.isoformat(),
                'macd': float(macd_data['macd'].loc[idx]),
                'signal': float(macd_data['signal'].loc[idx]),
                'histogram': float(macd_data['histogram'].loc[idx])
            }
            for idx in macd_data['macd'].dropna().index
        ][-30:]  # Last 30 values
    }


@router.get("/{symbol}/bollinger", response_model=dict)
def get_bollinger_bands(
    symbol: str,
    period: int = Query(20, ge=5, le=50, description="Period"),
    std: int = Query(2, ge=1, le=3, description="Standard deviations"),
    days: int = Query(100, ge=20, le=365, description="Days of historical data"),
    db: Session = Depends(get_db)
):
    """
    Get Bollinger Bands

    **Parameters:**
    - **symbol**: Stock symbol
    - **period**: Period for middle band (default: 20)
    - **std**: Number of standard deviations (default: 2)
    - **days**: Days of historical data (20-365, default: 100)
    """
    df = IndicatorService.get_historical_data(db, symbol, days)

    if df.empty:
        raise HTTPException(status_code=404, detail="No historical data found")

    bb_data = IndicatorService.calculate_bollinger_bands(df, period, std)

    if bb_data['middle'].empty:
        raise HTTPException(status_code=400, detail="Insufficient data for Bollinger Bands")

    current_price = float(df['close'].iloc[-1])
    current_upper = float(bb_data['upper'].iloc[-1])
    current_middle = float(bb_data['middle'].iloc[-1])
    current_lower = float(bb_data['lower'].iloc[-1])

    # Generate signal
    if current_price >= current_upper:
        band_signal = "Price at upper band (overbought)"
    elif current_price <= current_lower:
        band_signal = "Price at lower band (oversold)"
    else:
        band_signal = "Price within bands"

    return {
        'symbol': symbol.upper(),
        'indicator': f'BB({period},{std})',
        'current_price': current_price,
        'current_values': {
            'upper': current_upper,
            'middle': current_middle,
            'lower': current_lower
        },
        'signal': band_signal,
        'values': [
            {
                'timestamp': idx.isoformat(),
                'upper': float(bb_data['upper'].loc[idx]),
                'middle': float(bb_data['middle'].loc[idx]),
                'lower': float(bb_data['lower'].loc[idx])
            }
            for idx in bb_data['middle'].dropna().index
        ][-30:]  # Last 30 values
    }
