"""Backtesting framework for evaluating trading strategies based on ML predictions"""
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session

from app.ml.features import FeatureEngineering

logger = logging.getLogger(__name__)


class Backtester:
    """Backtest trading strategies using ML model predictions"""

    def __init__(
        self,
        initial_capital: float = 10000.0,
        transaction_cost: float = 0.001,  # 0.1% per trade
        slippage: float = 0.0005  # 0.05%
    ):
        """
        Args:
            initial_capital: Starting capital
            transaction_cost: Transaction cost as fraction of trade value
            slippage: Slippage as fraction of trade value
        """
        self.initial_capital = initial_capital
        self.transaction_cost = transaction_cost
        self.slippage = slippage

    def simple_strategy(
        self,
        predictions: np.ndarray,
        prices: np.ndarray,
        threshold: float = 0.0
    ) -> np.ndarray:
        """
        Simple long-only strategy based on predictions

        Args:
            predictions: Array of predicted returns
            prices: Array of actual prices
            threshold: Minimum predicted return to enter position

        Returns:
            Array of positions (1 = long, 0 = cash)
        """
        positions = np.zeros(len(predictions))

        # Buy when predicted return > threshold
        positions[predictions > threshold] = 1

        return positions

    def threshold_strategy(
        self,
        predictions: np.ndarray,
        prices: np.ndarray,
        buy_threshold: float = 0.01,
        sell_threshold: float = -0.01
    ) -> np.ndarray:
        """
        Strategy with buy/sell thresholds

        Args:
            predictions: Array of predicted returns
            prices: Array of actual prices
            buy_threshold: Threshold to buy
            sell_threshold: Threshold to sell

        Returns:
            Array of positions
        """
        positions = np.zeros(len(predictions))
        current_position = 0

        for i in range(len(predictions)):
            if current_position == 0 and predictions[i] > buy_threshold:
                current_position = 1
            elif current_position == 1 and predictions[i] < sell_threshold:
                current_position = 0

            positions[i] = current_position

        return positions

    def calculate_returns(
        self,
        positions: np.ndarray,
        actual_returns: np.ndarray
    ) -> pd.DataFrame:
        """
        Calculate strategy returns

        Args:
            positions: Array of positions (1 = long, 0 = cash)
            actual_returns: Array of actual returns

        Returns:
            DataFrame with returns analysis
        """
        # Calculate strategy returns (with costs)
        position_changes = np.diff(positions, prepend=0)
        trade_costs = np.abs(position_changes) * (self.transaction_cost + self.slippage)

        strategy_returns = positions * actual_returns - trade_costs

        # Calculate cumulative returns
        cumulative_returns = (1 + strategy_returns).cumprod()
        buy_hold_returns = (1 + actual_returns).cumprod()

        df = pd.DataFrame({
            'position': positions,
            'actual_return': actual_returns,
            'strategy_return': strategy_returns,
            'cumulative_return': cumulative_returns,
            'buy_hold_return': buy_hold_returns
        })

        return df

    def calculate_metrics(
        self,
        returns_df: pd.DataFrame,
        trading_days_per_year: int = 252
    ) -> Dict[str, float]:
        """
        Calculate performance metrics

        Args:
            returns_df: DataFrame with returns
            trading_days_per_year: Trading days per year for annualization

        Returns:
            Dictionary with performance metrics
        """
        strategy_returns = returns_df['strategy_return'].values
        actual_returns = returns_df['actual_return'].values

        # Total return
        total_return = returns_df['cumulative_return'].iloc[-1] - 1
        buy_hold_return = returns_df['buy_hold_return'].iloc[-1] - 1

        # Annualized return
        n_days = len(strategy_returns)
        years = n_days / trading_days_per_year
        annualized_return = (1 + total_return) ** (1 / years) - 1

        # Annualized volatility
        volatility = strategy_returns.std() * np.sqrt(trading_days_per_year)

        # Sharpe ratio (assuming 0 risk-free rate)
        sharpe_ratio = annualized_return / volatility if volatility > 0 else 0

        # Maximum drawdown
        cumulative = returns_df['cumulative_return'].values
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()

        # Win rate
        winning_trades = np.sum(strategy_returns > 0)
        total_trades = np.sum(np.diff(returns_df['position'].values, prepend=0) != 0) / 2
        win_rate = winning_trades / len(strategy_returns) if len(strategy_returns) > 0 else 0

        # Average win/loss
        wins = strategy_returns[strategy_returns > 0]
        losses = strategy_returns[strategy_returns < 0]
        avg_win = wins.mean() if len(wins) > 0 else 0
        avg_loss = losses.mean() if len(losses) > 0 else 0

        # Profit factor
        total_wins = wins.sum() if len(wins) > 0 else 0
        total_losses = abs(losses.sum()) if len(losses) > 0 else 0
        profit_factor = total_wins / total_losses if total_losses > 0 else 0

        # Calmar ratio (return / max drawdown)
        calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0

        return {
            'total_return': float(total_return),
            'buy_hold_return': float(buy_hold_return),
            'excess_return': float(total_return - buy_hold_return),
            'annualized_return': float(annualized_return),
            'volatility': float(volatility),
            'sharpe_ratio': float(sharpe_ratio),
            'max_drawdown': float(max_drawdown),
            'calmar_ratio': float(calmar_ratio),
            'win_rate': float(win_rate),
            'avg_win': float(avg_win),
            'avg_loss': float(avg_loss),
            'profit_factor': float(profit_factor),
            'total_trades': int(total_trades),
            'n_days': int(n_days)
        }

    def run_backtest(
        self,
        predictions: np.ndarray,
        actual_returns: np.ndarray,
        prices: np.ndarray,
        strategy: str = 'simple',
        **strategy_params
    ) -> Dict[str, Any]:
        """
        Run complete backtest

        Args:
            predictions: Array of predicted returns
            actual_returns: Array of actual returns
            prices: Array of prices
            strategy: Strategy type ('simple', 'threshold')
            **strategy_params: Strategy-specific parameters

        Returns:
            Dictionary with backtest results
        """
        logger.info(f"Running backtest with {strategy} strategy")

        # Generate positions based on strategy
        if strategy == 'simple':
            positions = self.simple_strategy(
                predictions, prices,
                threshold=strategy_params.get('threshold', 0.0)
            )
        elif strategy == 'threshold':
            positions = self.threshold_strategy(
                predictions, prices,
                buy_threshold=strategy_params.get('buy_threshold', 0.01),
                sell_threshold=strategy_params.get('sell_threshold', -0.01)
            )
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

        # Calculate returns
        returns_df = self.calculate_returns(positions, actual_returns)

        # Calculate metrics
        metrics = self.calculate_metrics(returns_df)

        logger.info(f"Backtest complete - Total Return: {metrics['total_return']:.2%}, "
                   f"Sharpe: {metrics['sharpe_ratio']:.2f}")

        return {
            'strategy': strategy,
            'strategy_params': strategy_params,
            'metrics': metrics,
            'returns_df': returns_df.to_dict('records')
        }

    def walk_forward_validation(
        self,
        db: Session,
        symbol: str,
        model,
        feature_cols: List[str],
        train_window: int = 252,
        test_window: int = 63,
        horizon: int = 1
    ) -> Dict[str, Any]:
        """
        Walk-forward validation

        Args:
            db: Database session
            symbol: Stock symbol
            model: Trained model object
            feature_cols: List of feature columns
            train_window: Training window size (days)
            test_window: Test window size (days)
            horizon: Prediction horizon

        Returns:
            Dictionary with walk-forward results
        """
        logger.info(f"Running walk-forward validation for {symbol}")

        # Get data
        days = train_window + test_window * 5  # Get extra data for multiple windows
        df = FeatureEngineering.create_all_features(
            db, symbol, days, horizon, 'returns'
        )

        if df.empty or len(df) < train_window + test_window:
            raise ValueError(f"Insufficient data for walk-forward validation")

        all_predictions = []
        all_actuals = []
        all_prices = []
        window_metrics = []

        start_idx = train_window
        while start_idx + test_window <= len(df):
            # Get train and test data
            train_df = df.iloc[start_idx - train_window:start_idx]
            test_df = df.iloc[start_idx:start_idx + test_window]

            # Prepare features
            X_train = train_df[feature_cols].values
            y_train = train_df['target'].values
            X_test = test_df[feature_cols].values
            y_test = test_df['target'].values

            # Scale
            X_train_scaled, X_test_scaled, _ = FeatureEngineering.scale_features(
                pd.DataFrame(X_train, columns=feature_cols),
                pd.DataFrame(X_test, columns=feature_cols),
                feature_cols
            )

            X_train_scaled = X_train_scaled[feature_cols].values
            X_test_scaled = X_test_scaled[feature_cols].values

            # Retrain model on rolling window
            model.train(X_train_scaled, y_train, verbose=False)

            # Predict
            predictions = model.predict(X_test_scaled)

            # Store results
            all_predictions.extend(predictions)
            all_actuals.extend(y_test)
            all_prices.extend(test_df['close'].values)

            # Calculate window metrics
            metrics = model.evaluate(X_test_scaled, y_test)
            window_metrics.append(metrics)

            # Move window
            start_idx += test_window

        # Run backtest on combined predictions
        backtest_result = self.run_backtest(
            np.array(all_predictions),
            np.array(all_actuals),
            np.array(all_prices),
            strategy='simple',
            threshold=0.0
        )

        return {
            'symbol': symbol,
            'n_windows': len(window_metrics),
            'avg_window_rmse': float(np.mean([m['rmse'] for m in window_metrics])),
            'avg_window_r2': float(np.mean([m['r2'] for m in window_metrics])),
            'backtest_metrics': backtest_result['metrics'],
            'window_metrics': window_metrics
        }
