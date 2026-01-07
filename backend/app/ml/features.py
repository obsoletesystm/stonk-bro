"""Feature engineering for ML models"""
import pandas as pd
import numpy as np
from typing import Optional, List
from sqlalchemy.orm import Session

from app.services.indicator_service import IndicatorService


class FeatureEngineering:
    """Feature engineering for stock price prediction"""

    @staticmethod
    def create_price_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Create price-based features

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with additional price features
        """
        features = df.copy()

        # Returns
        features['returns'] = features['close'].pct_change()
        features['log_returns'] = np.log(features['close'] / features['close'].shift(1))

        # Price changes
        features['price_change'] = features['close'] - features['close'].shift(1)
        features['price_change_pct'] = features['price_change'] / features['close'].shift(1) * 100

        # High-Low spread
        features['hl_spread'] = features['high'] - features['low']
        features['hl_spread_pct'] = features['hl_spread'] / features['close'] * 100

        # Open-Close spread
        features['oc_spread'] = features['close'] - features['open']
        features['oc_spread_pct'] = features['oc_spread'] / features['open'] * 100

        # Volume changes
        features['volume_change'] = features['volume'].pct_change()
        features['volume_ma_ratio'] = features['volume'] / features['volume'].rolling(20).mean()

        # Price position in daily range
        features['price_position'] = (features['close'] - features['low']) / (features['high'] - features['low'])

        return features

    @staticmethod
    def create_momentum_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Create momentum-based features

        Args:
            df: DataFrame with price data

        Returns:
            DataFrame with momentum features
        """
        features = df.copy()

        # Rate of Change (ROC) for different periods
        for period in [1, 5, 10, 20]:
            features[f'roc_{period}'] = (
                (features['close'] - features['close'].shift(period)) /
                features['close'].shift(period) * 100
            )

        # Momentum
        features['momentum_5'] = features['close'] - features['close'].shift(5)
        features['momentum_10'] = features['close'] - features['close'].shift(10)

        # Williams %R
        high_14 = features['high'].rolling(14).max()
        low_14 = features['low'].rolling(14).min()
        features['williams_r'] = -100 * ((high_14 - features['close']) / (high_14 - low_14))

        return features

    @staticmethod
    def create_volatility_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Create volatility-based features

        Args:
            df: DataFrame with price data

        Returns:
            DataFrame with volatility features
        """
        features = df.copy()

        # Historical volatility (std of returns)
        for period in [5, 10, 20, 30]:
            returns = features['close'].pct_change()
            features[f'volatility_{period}'] = returns.rolling(period).std() * np.sqrt(252)

        # Parkinson's volatility (using high-low)
        features['parkinson_vol'] = np.sqrt(
            (1 / (4 * np.log(2))) *
            ((np.log(features['high'] / features['low'])) ** 2).rolling(20).mean()
        ) * np.sqrt(252)

        # Average True Range percentage
        features['atr_pct'] = IndicatorService.calculate_atr(df, 14) / features['close'] * 100

        return features

    @staticmethod
    def create_technical_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Create features from technical indicators

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with technical indicator features
        """
        features = df.copy()

        # Moving Averages
        for period in [5, 10, 20, 50, 200]:
            sma = IndicatorService.calculate_sma(df, period)
            features[f'sma_{period}'] = sma
            features[f'price_to_sma_{period}'] = (features['close'] - sma) / sma * 100

        # Exponential Moving Averages
        for period in [12, 26, 50]:
            ema = IndicatorService.calculate_ema(df, period)
            features[f'ema_{period}'] = ema
            features[f'price_to_ema_{period}'] = (features['close'] - ema) / ema * 100

        # RSI
        rsi = IndicatorService.calculate_rsi(df, 14)
        features['rsi_14'] = rsi
        features['rsi_oversold'] = (rsi < 30).astype(int)
        features['rsi_overbought'] = (rsi > 70).astype(int)

        # MACD
        macd_data = IndicatorService.calculate_macd(df)
        features['macd'] = macd_data['macd']
        features['macd_signal'] = macd_data['signal']
        features['macd_histogram'] = macd_data['histogram']
        features['macd_positive'] = (macd_data['macd'] > macd_data['signal']).astype(int)

        # Bollinger Bands
        bb_data = IndicatorService.calculate_bollinger_bands(df, 20, 2)
        features['bb_upper'] = bb_data['upper']
        features['bb_middle'] = bb_data['middle']
        features['bb_lower'] = bb_data['lower']
        features['bb_width'] = (bb_data['upper'] - bb_data['lower']) / bb_data['middle']
        features['bb_position'] = (features['close'] - bb_data['lower']) / (bb_data['upper'] - bb_data['lower'])

        # Stochastic
        stoch_data = IndicatorService.calculate_stochastic(df, 14, 3)
        features['stoch_k'] = stoch_data['k']
        features['stoch_d'] = stoch_data['d']

        # ADX
        features['adx_14'] = IndicatorService.calculate_adx(df, 14)

        # OBV
        features['obv'] = IndicatorService.calculate_obv(df)
        features['obv_ma_ratio'] = features['obv'] / features['obv'].rolling(20).mean()

        return features

    @staticmethod
    def create_lagged_features(df: pd.DataFrame, columns: List[str], lags: List[int]) -> pd.DataFrame:
        """
        Create lagged features for time series

        Args:
            df: DataFrame with features
            columns: Column names to create lags for
            lags: List of lag periods

        Returns:
            DataFrame with lagged features
        """
        features = df.copy()

        for col in columns:
            if col in features.columns:
                for lag in lags:
                    features[f'{col}_lag_{lag}'] = features[col].shift(lag)

        return features

    @staticmethod
    def create_target_variable(df: pd.DataFrame, horizon: int = 1, target_type: str = 'returns') -> pd.DataFrame:
        """
        Create target variable for prediction

        Args:
            df: DataFrame with price data
            horizon: Number of days ahead to predict
            target_type: Type of target ('returns', 'price', 'direction')

        Returns:
            DataFrame with target variable
        """
        features = df.copy()

        if target_type == 'returns':
            # Predict future returns
            features['target'] = features['close'].pct_change(horizon).shift(-horizon)
        elif target_type == 'price':
            # Predict future price
            features['target'] = features['close'].shift(-horizon)
        elif target_type == 'direction':
            # Predict price direction (up=1, down=0)
            future_returns = features['close'].pct_change(horizon).shift(-horizon)
            features['target'] = (future_returns > 0).astype(int)

        return features

    @staticmethod
    def create_all_features(
        db: Session,
        symbol: str,
        days: int = 500,
        horizon: int = 1,
        target_type: str = 'returns'
    ) -> pd.DataFrame:
        """
        Create complete feature set for ML model

        Args:
            db: Database session
            symbol: Stock symbol
            days: Days of historical data
            horizon: Prediction horizon in days
            target_type: Type of target variable

        Returns:
            DataFrame with all features and target
        """
        # Get historical data
        df = IndicatorService.get_historical_data(db, symbol, days)

        if df.empty:
            return pd.DataFrame()

        # Create all feature sets
        df = FeatureEngineering.create_price_features(df)
        df = FeatureEngineering.create_momentum_features(df)
        df = FeatureEngineering.create_volatility_features(df)
        df = FeatureEngineering.create_technical_features(df)

        # Create lagged features for key indicators
        lag_columns = ['close', 'volume', 'returns', 'rsi_14', 'macd_histogram']
        df = FeatureEngineering.create_lagged_features(df, lag_columns, [1, 2, 3, 5])

        # Create target variable
        df = FeatureEngineering.create_target_variable(df, horizon, target_type)

        # Drop rows with NaN values
        df = df.dropna()

        return df

    @staticmethod
    def get_feature_columns(exclude_target: bool = True) -> List[str]:
        """
        Get list of feature column names

        Args:
            exclude_target: Whether to exclude target and raw OHLCV columns

        Returns:
            List of feature column names
        """
        # Base columns to exclude
        exclude_cols = ['open', 'high', 'low', 'close', 'volume']

        if exclude_target:
            exclude_cols.append('target')

        return exclude_cols

    @staticmethod
    def scale_features(
        train_df: pd.DataFrame,
        test_df: Optional[pd.DataFrame] = None,
        feature_cols: Optional[List[str]] = None
    ) -> tuple:
        """
        Scale features using StandardScaler

        Args:
            train_df: Training DataFrame
            test_df: Test DataFrame (optional)
            feature_cols: Feature columns to scale

        Returns:
            Tuple of (scaled_train, scaled_test, scaler) or (scaled_train, scaler)
        """
        from sklearn.preprocessing import StandardScaler

        if feature_cols is None:
            # Get all numeric columns except target
            feature_cols = train_df.select_dtypes(include=[np.number]).columns.tolist()
            if 'target' in feature_cols:
                feature_cols.remove('target')

        scaler = StandardScaler()

        # Fit and transform training data
        train_scaled = train_df.copy()
        train_scaled[feature_cols] = scaler.fit_transform(train_df[feature_cols])

        if test_df is not None:
            # Transform test data
            test_scaled = test_df.copy()
            test_scaled[feature_cols] = scaler.transform(test_df[feature_cols])
            return train_scaled, test_scaled, scaler

        return train_scaled, scaler
