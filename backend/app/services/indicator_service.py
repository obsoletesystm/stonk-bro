"""Technical indicator calculation service"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from app.models.stock import StockQuote


class IndicatorService:
    """Service for calculating technical indicators"""

    @staticmethod
    def get_historical_data(
        db: Session,
        symbol: str,
        days: int = 100,
        end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Get historical data as DataFrame for indicator calculation

        Args:
            db: Database session
            symbol: Stock symbol
            days: Number of days of historical data
            end_date: End date (defaults to now)

        Returns:
            DataFrame with OHLCV data
        """
        if end_date is None:
            end_date = datetime.now()

        start_date = end_date - timedelta(days=days)

        # Query stock quotes
        quotes = db.query(StockQuote).filter(
            and_(
                StockQuote.symbol == symbol.upper(),
                StockQuote.timestamp >= start_date,
                StockQuote.timestamp <= end_date
            )
        ).order_by(StockQuote.timestamp).all()

        if not quotes:
            return pd.DataFrame()

        # Convert to DataFrame
        data = {
            'timestamp': [q.timestamp for q in quotes],
            'open': [float(q.open) for q in quotes],
            'high': [float(q.high) for q in quotes],
            'low': [float(q.low) for q in quotes],
            'close': [float(q.close) for q in quotes],
            'volume': [int(q.volume) for q in quotes],
        }

        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        return df

    @staticmethod
    def calculate_sma(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """Calculate Simple Moving Average"""
        if df.empty or len(df) < period:
            return pd.Series()
        return df['close'].rolling(window=period).mean()

    @staticmethod
    def calculate_ema(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """Calculate Exponential Moving Average"""
        if df.empty or len(df) < period:
            return pd.Series()
        return df['close'].ewm(span=period, adjust=False).mean()

    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        if df.empty or len(df) < period + 1:
            return pd.Series()

        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence)

        Returns:
            dict with 'macd', 'signal', 'histogram' keys
        """
        if df.empty or len(df) < slow:
            return {'macd': pd.Series(), 'signal': pd.Series(), 'histogram': pd.Series()}

        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()

        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line

        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }

    @staticmethod
    def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20, std: int = 2) -> Dict[str, pd.Series]:
        """
        Calculate Bollinger Bands

        Returns:
            dict with 'upper', 'middle', 'lower' keys
        """
        if df.empty or len(df) < period:
            return {'upper': pd.Series(), 'middle': pd.Series(), 'lower': pd.Series()}

        middle = df['close'].rolling(window=period).mean()
        std_dev = df['close'].rolling(window=period).std()

        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)

        return {
            'upper': upper,
            'middle': middle,
            'lower': lower
        }

    @staticmethod
    def calculate_stochastic(df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Dict[str, pd.Series]:
        """
        Calculate Stochastic Oscillator

        Returns:
            dict with 'k' and 'd' keys
        """
        if df.empty or len(df) < k_period:
            return {'k': pd.Series(), 'd': pd.Series()}

        low_min = df['low'].rolling(window=k_period).min()
        high_max = df['high'].rolling(window=k_period).max()

        k = 100 * ((df['close'] - low_min) / (high_max - low_min))
        d = k.rolling(window=d_period).mean()

        return {
            'k': k,
            'd': d
        }

    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range (volatility indicator)"""
        if df.empty or len(df) < period + 1:
            return pd.Series()

        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())

        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()

        return atr

    @staticmethod
    def calculate_adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average Directional Index (trend strength)"""
        if df.empty or len(df) < period * 2:
            return pd.Series()

        # Calculate +DM and -DM
        high_diff = df['high'].diff()
        low_diff = -df['low'].diff()

        plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
        minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)

        # Calculate ATR
        atr = IndicatorService.calculate_atr(df, period)

        # Calculate +DI and -DI
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)

        # Calculate DX and ADX
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()

        return adx

    @staticmethod
    def calculate_obv(df: pd.DataFrame) -> pd.Series:
        """Calculate On-Balance Volume"""
        if df.empty:
            return pd.Series()

        obv = pd.Series(index=df.index, dtype=float)
        obv.iloc[0] = df['volume'].iloc[0]

        for i in range(1, len(df)):
            if df['close'].iloc[i] > df['close'].iloc[i - 1]:
                obv.iloc[i] = obv.iloc[i - 1] + df['volume'].iloc[i]
            elif df['close'].iloc[i] < df['close'].iloc[i - 1]:
                obv.iloc[i] = obv.iloc[i - 1] - df['volume'].iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i - 1]

        return obv

    @staticmethod
    def calculate_all_indicators(
        db: Session,
        symbol: str,
        days: int = 100
    ) -> Dict[str, Any]:
        """
        Calculate all technical indicators for a symbol

        Args:
            db: Database session
            symbol: Stock symbol
            days: Days of historical data to use

        Returns:
            Dictionary with all indicators
        """
        df = IndicatorService.get_historical_data(db, symbol, days)

        if df.empty:
            return {
                'error': 'No historical data found',
                'symbol': symbol,
                'days_requested': days
            }

        # Get latest values (most recent data point)
        latest_idx = df.index[-1]

        # Calculate all indicators
        sma_20 = IndicatorService.calculate_sma(df, 20)
        sma_50 = IndicatorService.calculate_sma(df, 50)
        sma_200 = IndicatorService.calculate_sma(df, 200)
        ema_12 = IndicatorService.calculate_ema(df, 12)
        ema_26 = IndicatorService.calculate_ema(df, 26)
        rsi = IndicatorService.calculate_rsi(df, 14)
        macd_data = IndicatorService.calculate_macd(df)
        bb_data = IndicatorService.calculate_bollinger_bands(df)
        stoch_data = IndicatorService.calculate_stochastic(df)
        atr = IndicatorService.calculate_atr(df)
        adx = IndicatorService.calculate_adx(df)
        obv = IndicatorService.calculate_obv(df)

        # Helper to safely get latest value
        def get_latest(series: pd.Series) -> Optional[float]:
            if series.empty:
                return None
            val = series.iloc[-1]
            return None if pd.isna(val) else float(val)

        result = {
            'symbol': symbol.upper(),
            'timestamp': latest_idx.isoformat() if latest_idx else None,
            'price': {
                'current': float(df['close'].iloc[-1]),
                'open': float(df['open'].iloc[-1]),
                'high': float(df['high'].iloc[-1]),
                'low': float(df['low'].iloc[-1]),
                'volume': int(df['volume'].iloc[-1])
            },
            'moving_averages': {
                'sma_20': get_latest(sma_20),
                'sma_50': get_latest(sma_50),
                'sma_200': get_latest(sma_200),
                'ema_12': get_latest(ema_12),
                'ema_26': get_latest(ema_26)
            },
            'oscillators': {
                'rsi_14': get_latest(rsi),
                'stoch_k': get_latest(stoch_data['k']),
                'stoch_d': get_latest(stoch_data['d'])
            },
            'macd': {
                'macd': get_latest(macd_data['macd']),
                'signal': get_latest(macd_data['signal']),
                'histogram': get_latest(macd_data['histogram'])
            },
            'bollinger_bands': {
                'upper': get_latest(bb_data['upper']),
                'middle': get_latest(bb_data['middle']),
                'lower': get_latest(bb_data['lower'])
            },
            'trend': {
                'adx_14': get_latest(adx),
                'atr_14': get_latest(atr)
            },
            'volume': {
                'obv': get_latest(obv)
            },
            'data_points': len(df),
            'period_days': days
        }

        # Add interpretations
        result['signals'] = IndicatorService._generate_signals(result)

        return result

    @staticmethod
    def _generate_signals(indicators: Dict[str, Any]) -> Dict[str, str]:
        """Generate trading signals based on indicators"""
        signals = {}

        # RSI signals
        rsi = indicators['oscillators'].get('rsi_14')
        if rsi is not None:
            if rsi > 70:
                signals['rsi'] = 'Overbought (>70)'
            elif rsi < 30:
                signals['rsi'] = 'Oversold (<30)'
            else:
                signals['rsi'] = 'Neutral'

        # MACD signal
        macd = indicators['macd'].get('macd')
        signal = indicators['macd'].get('signal')
        if macd is not None and signal is not None:
            if macd > signal:
                signals['macd'] = 'Bullish (MACD > Signal)'
            else:
                signals['macd'] = 'Bearish (MACD < Signal)'

        # Bollinger Bands
        price = indicators['price']['current']
        bb_upper = indicators['bollinger_bands'].get('upper')
        bb_lower = indicators['bollinger_bands'].get('lower')
        if bb_upper is not None and bb_lower is not None:
            if price >= bb_upper:
                signals['bollinger'] = 'Overbought (at upper band)'
            elif price <= bb_lower:
                signals['bollinger'] = 'Oversold (at lower band)'
            else:
                signals['bollinger'] = 'Neutral'

        # Trend (ADX)
        adx = indicators['trend'].get('adx_14')
        if adx is not None:
            if adx > 25:
                signals['trend'] = 'Strong trend (ADX > 25)'
            elif adx < 20:
                signals['trend'] = 'Weak trend (ADX < 20)'
            else:
                signals['trend'] = 'Moderate trend'

        # Moving Average crossover
        sma_20 = indicators['moving_averages'].get('sma_20')
        sma_50 = indicators['moving_averages'].get('sma_50')
        if sma_20 is not None and sma_50 is not None:
            if sma_20 > sma_50:
                signals['ma_crossover'] = 'Bullish (20 > 50)'
            else:
                signals['ma_crossover'] = 'Bearish (20 < 50)'

        return signals
