#!/usr/bin/env python3
"""
Train ML models for stock price prediction

Usage:
    python scripts/train_model.py --symbol AAPL --model xgboost
    python scripts/train_model.py --symbols AAPL,MSFT,GOOGL --model lstm
    python scripts/train_model.py --from-portfolio --model xgboost --target returns
"""
import argparse
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import SessionLocal
from app.ml.trainer import ModelTrainer
from app.services.data_fetcher import DataFetcher
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_training_results(results: dict):
    """Pretty print training results"""
    print(f"\n{'='*70}")
    print(f"Training Results: {results['symbol']}")
    print(f"{'='*70}")
    print(f"Model Type: {results['model_type']}")
    print(f"Features: {results['n_features']}")

    if 'model_path' in results and results['model_path']:
        print(f"Model saved to: {results['model_path']}")

    print(f"\nTest Metrics:")
    metrics = results['test_metrics']
    print(f"  RMSE:      {metrics['rmse']:.6f}")
    print(f"  MAE:       {metrics['mae']:.6f}")
    print(f"  R² Score:  {metrics['r2']:.4f}")

    if 'direction_accuracy' in metrics:
        print(f"  Direction: {metrics['direction_accuracy']:.2%}")

    print()


def main():
    parser = argparse.ArgumentParser(description="Train ML models for stock prediction")

    # Symbol selection
    symbol_group = parser.add_mutually_exclusive_group(required=True)
    symbol_group.add_argument(
        "--symbol",
        type=str,
        help="Single stock symbol to train"
    )
    symbol_group.add_argument(
        "--symbols",
        type=str,
        help="Comma-separated list of stock symbols"
    )
    symbol_group.add_argument(
        "--from-portfolio",
        action="store_true",
        help="Train models for all portfolio holdings"
    )

    # Model configuration
    parser.add_argument(
        "--model",
        type=str,
        default="xgboost",
        choices=["xgboost", "lstm"],
        help="Model type (default: xgboost)"
    )
    parser.add_argument(
        "--target",
        type=str,
        default="returns",
        choices=["returns", "price", "direction"],
        help="Target variable type (default: returns)"
    )
    parser.add_argument(
        "--horizon",
        type=int,
        default=1,
        help="Prediction horizon in days (default: 1)"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=500,
        help="Days of historical data to use (default: 500)"
    )

    # Model-specific parameters
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=0.01,
        help="Learning rate (default: 0.01)"
    )
    parser.add_argument(
        "--n-estimators",
        type=int,
        default=1000,
        help="Number of estimators for XGBoost (default: 1000)"
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=7,
        help="Max depth for XGBoost (default: 7)"
    )
    parser.add_argument(
        "--hidden-size",
        type=int,
        default=128,
        help="Hidden size for LSTM (default: 128)"
    )
    parser.add_argument(
        "--num-layers",
        type=int,
        default=2,
        help="Number of LSTM layers (default: 2)"
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=100,
        help="Number of epochs for LSTM (default: 100)"
    )

    args = parser.parse_args()

    # Determine symbols
    db = SessionLocal()

    if args.from_portfolio:
        fetcher = DataFetcher(db)
        symbols = fetcher.get_symbols_from_portfolios()
        if not symbols:
            print("No portfolio holdings found")
            db.close()
            return
    elif args.symbols:
        symbols = [s.strip().upper() for s in args.symbols.split(",")]
    else:
        symbols = [args.symbol.upper()]

    print(f"{'='*70}")
    print(f"ML Model Training - {datetime.now()}")
    print(f"{'='*70}")
    print(f"Model Type: {args.model}")
    print(f"Target Type: {args.target}")
    print(f"Horizon: {args.horizon} day(s)")
    print(f"Training {len(symbols)} symbol(s)")
    print()

    # Initialize trainer
    trainer = ModelTrainer()

    # Prepare model parameters
    if args.model == 'xgboost':
        model_params = {
            'learning_rate': args.learning_rate,
            'n_estimators': args.n_estimators,
            'max_depth': args.max_depth
        }
    else:  # lstm
        model_params = {
            'learning_rate': args.learning_rate,
            'hidden_size': args.hidden_size,
            'num_layers': args.num_layers,
            'epochs': args.epochs
        }

    # Train models
    all_results = {}

    for i, symbol in enumerate(symbols, 1):
        try:
            print(f"[{i}/{len(symbols)}] Training {symbol}...")

            results = trainer.train_model(
                db,
                symbol,
                model_type=args.model,
                days=args.days,
                horizon=args.horizon,
                target_type=args.target,
                save_model=True,
                **model_params
            )

            print_training_results(results)
            all_results[symbol] = results

        except Exception as e:
            logger.error(f"Error training {symbol}: {e}")
            import traceback
            traceback.print_exc()
            all_results[symbol] = {'error': str(e)}
            continue

    db.close()

    # Print summary
    print(f"\n{'='*70}")
    print("Training Summary")
    print(f"{'='*70}")

    successful = [s for s, r in all_results.items() if 'error' not in r]
    failed = [s for s, r in all_results.items() if 'error' in r]

    print(f"Total symbols: {len(symbols)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")

    if successful:
        print(f"\nSuccessful models:")
        for symbol in successful:
            results = all_results[symbol]
            print(f"  {symbol}: RMSE={results['test_metrics']['rmse']:.6f}, "
                  f"R²={results['test_metrics']['r2']:.4f}")

    if failed:
        print(f"\nFailed models:")
        for symbol in failed:
            print(f"  {symbol}: {all_results[symbol]['error']}")

    print()


if __name__ == "__main__":
    main()
