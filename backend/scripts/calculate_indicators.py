#!/usr/bin/env python3
"""
Calculate technical indicators for stocks

Usage:
    python scripts/calculate_indicators.py --symbols AAPL,GOOGL
    python scripts/calculate_indicators.py --from-portfolio
    python scripts/calculate_indicators.py --symbols AAPL --days 200
"""
import argparse
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import SessionLocal
from app.services.indicator_service import IndicatorService
from app.services.data_fetcher import DataFetcher


def print_indicators(indicators: dict):
    """Pretty print indicators"""
    symbol = indicators['symbol']
    print(f"\n{'='*60}")
    print(f"Technical Analysis: {symbol}")
    print(f"{'='*60}")
    print(f"Timestamp: {indicators.get('timestamp', 'N/A')}")
    print(f"Data Points: {indicators['data_points']} ({indicators['period_days']} days)")
    print()

    # Current Price
    price = indicators['price']
    print(f"Current Price: ${price['current']:.2f}")
    print(f"  Open: ${price['open']:.2f} | High: ${price['high']:.2f} | Low: ${price['low']:.2f}")
    print(f"  Volume: {price['volume']:,}")
    print()

    # Moving Averages
    print("Moving Averages:")
    ma = indicators['moving_averages']
    if ma['sma_20']:
        print(f"  SMA(20):  ${ma['sma_20']:.2f}")
    if ma['sma_50']:
        print(f"  SMA(50):  ${ma['sma_50']:.2f}")
    if ma['sma_200']:
        print(f"  SMA(200): ${ma['sma_200']:.2f}")
    if ma['ema_12']:
        print(f"  EMA(12):  ${ma['ema_12']:.2f}")
    if ma['ema_26']:
        print(f"  EMA(26):  ${ma['ema_26']:.2f}")
    print()

    # Oscillators
    print("Oscillators:")
    osc = indicators['oscillators']
    if osc['rsi_14'] is not None:
        print(f"  RSI(14):       {osc['rsi_14']:.2f}")
    if osc['stoch_k'] is not None:
        print(f"  Stochastic %K: {osc['stoch_k']:.2f}")
    if osc['stoch_d'] is not None:
        print(f"  Stochastic %D: {osc['stoch_d']:.2f}")
    print()

    # MACD
    print("MACD:")
    macd = indicators['macd']
    if macd['macd'] is not None:
        print(f"  MACD:      {macd['macd']:.4f}")
    if macd['signal'] is not None:
        print(f"  Signal:    {macd['signal']:.4f}")
    if macd['histogram'] is not None:
        print(f"  Histogram: {macd['histogram']:.4f}")
    print()

    # Bollinger Bands
    print("Bollinger Bands:")
    bb = indicators['bollinger_bands']
    if bb['upper']:
        print(f"  Upper:  ${bb['upper']:.2f}")
    if bb['middle']:
        print(f"  Middle: ${bb['middle']:.2f}")
    if bb['lower']:
        print(f"  Lower:  ${bb['lower']:.2f}")
    print()

    # Trend Indicators
    print("Trend Indicators:")
    trend = indicators['trend']
    if trend['adx_14'] is not None:
        print(f"  ADX(14): {trend['adx_14']:.2f}")
    if trend['atr_14'] is not None:
        print(f"  ATR(14): ${trend['atr_14']:.2f}")
    print()

    # Volume
    print("Volume Indicators:")
    vol = indicators['volume']
    if vol['obv'] is not None:
        print(f"  OBV: {vol['obv']:,.0f}")
    print()

    # Signals
    if indicators.get('signals'):
        print("Trading Signals:")
        for key, signal in indicators['signals'].items():
            print(f"  {key.upper()}: {signal}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Calculate technical indicators")
    parser.add_argument(
        "--symbols",
        type=str,
        help="Comma-separated list of stock symbols"
    )
    parser.add_argument(
        "--from-portfolio",
        action="store_true",
        help="Calculate for all portfolio holdings"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=100,
        help="Days of historical data to use (default: 100)"
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
        print("Error: Must specify either --symbols or --from-portfolio")
        parser.print_help()
        db.close()
        return

    print(f"=== Technical Indicators ({datetime.now()}) ===")
    print(f"Calculating for {len(symbols)} symbol(s)")
    print(f"Using {args.days} days of historical data")
    print()

    for i, symbol in enumerate(symbols, 1):
        try:
            print(f"[{i}/{len(symbols)}] Processing {symbol}...")

            indicators = IndicatorService.calculate_all_indicators(
                db, symbol, args.days
            )

            if 'error' in indicators:
                print(f"  ✗ Error: {indicators['error']}")
                continue

            print_indicators(indicators)

        except Exception as e:
            print(f"  ✗ Error calculating indicators for {symbol}: {e}")
            import traceback
            traceback.print_exc()
            continue

    db.close()

    print("\n=== Done ===\n")


if __name__ == "__main__":
    main()
