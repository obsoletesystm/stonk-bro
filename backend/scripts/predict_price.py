#!/usr/bin/env python3
"""
Make stock price predictions using trained models

Usage:
    python scripts/predict_price.py --symbol AAPL
    python scripts/predict_price.py --symbol MSFT --model lstm --horizon 5
    python scripts/predict_price.py --symbols AAPL,GOOGL,MSFT --multi-horizon
"""
import argparse
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import SessionLocal
from app.ml.prediction_service import PredictionService
import logging

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def print_prediction(result: dict):
    """Pretty print prediction result"""
    print(f"\n{'='*70}")
    print(f"Prediction: {result['symbol']}")
    print(f"{'='*70}")
    print(f"Model: {result['model_type']} ({result['target_type']})")
    print(f"Horizon: {result['horizon']} day(s)")
    print(f"Timestamp: {result['timestamp']}")
    print()

    print(f"Current Price: ${result['current_price']:.2f}")

    if 'predicted_price' in result:
        print(f"Predicted Price: ${result['predicted_price']:.2f}")

    if 'predicted_return' in result:
        sign = '+' if result['predicted_return'] >= 0 else ''
        print(f"Predicted Return: {sign}{result['predicted_return']:.2f}%")

    if 'direction' in result:
        print(f"Direction: {result['direction']}")

    if 'confidence' in result:
        print(f"Confidence: {result['confidence']:.1%}")

    # Model info
    metadata = result.get('model_metadata', {})
    if metadata:
        print(f"\nModel Info:")
        if metadata.get('trained_at'):
            print(f"  Trained: {metadata['trained_at']}")
        if metadata.get('test_rmse'):
            print(f"  Test RMSE: {metadata['test_rmse']:.6f}")
        if metadata.get('test_r2'):
            print(f"  Test R²: {metadata['test_r2']:.4f}")

    print()


def print_multi_horizon(result: dict):
    """Pretty print multi-horizon predictions"""
    print(f"\n{'='*70}")
    print(f"Multi-Horizon Predictions: {result['symbol']}")
    print(f"{'='*70}")
    print(f"Model: {result['model_type']} ({result['target_type']})")
    print(f"Timestamp: {result['timestamp']}")
    print()

    predictions = result['predictions']

    for horizon, pred in predictions.items():
        if 'error' in pred:
            print(f"{horizon.upper():8s}: Error - {pred['error']}")
        else:
            price = pred.get('predicted_price', 0)
            ret = pred.get('predicted_return', 0)
            direction = pred.get('direction', '')
            sign = '+' if ret >= 0 else ''

            print(f"{horizon.upper():8s}: ${price:.2f} ({sign}{ret:.2f}%) [{direction}]")

    print()


def main():
    parser = argparse.ArgumentParser(description="Make stock price predictions")

    parser.add_argument(
        "--symbol",
        type=str,
        help="Single stock symbol"
    )
    parser.add_argument(
        "--symbols",
        type=str,
        help="Comma-separated list of stock symbols"
    )
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
        "--multi-horizon",
        action="store_true",
        help="Predict for multiple horizons (1, 5, 10, 20 days)"
    )

    args = parser.parse_args()

    if not args.symbol and not args.symbols:
        parser.error("Must specify --symbol or --symbols")

    # Determine symbols
    if args.symbols:
        symbols = [s.strip().upper() for s in args.symbols.split(",")]
    else:
        symbols = [args.symbol.upper()]

    print(f"{'='*70}")
    print(f"Stock Price Prediction - {datetime.now()}")
    print(f"{'='*70}\n")

    # Initialize prediction service
    db = SessionLocal()
    predictor = PredictionService()

    for symbol in symbols:
        try:
            if args.multi_horizon:
                result = predictor.predict_multiple_horizons(
                    db, symbol, [1, 5, 10, 20], args.model, args.target
                )
                print_multi_horizon(result)
            else:
                result = predictor.predict(
                    db, symbol, args.model, args.target, args.horizon
                )
                print_prediction(result)

        except ValueError as e:
            print(f"\n✗ Error for {symbol}: {e}\n")
        except Exception as e:
            print(f"\n✗ Unexpected error for {symbol}: {e}\n")
            import traceback
            traceback.print_exc()

    db.close()


if __name__ == "__main__":
    main()
