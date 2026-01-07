#!/usr/bin/env python3
"""
Update daily stock prices for portfolio holdings

This script should be run daily after market close (5 PM ET)
via cron job to keep prices up to date.

Usage:
    python scripts/update_daily_prices.py
    python scripts/update_daily_prices.py --symbols AAPL,GOOGL
"""
import argparse
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import SessionLocal
from app.services.data_fetcher import DataFetcher


def main():
    parser = argparse.ArgumentParser(description="Update daily stock prices")
    parser.add_argument(
        "--symbols",
        type=str,
        help="Comma-separated list of symbols to update (default: all portfolio holdings)"
    )
    parser.add_argument(
        "--source",
        type=str,
        default="yfinance",
        choices=["yfinance", "alpha_vantage"],
        help="Data source (default: yfinance)"
    )

    args = parser.parse_args()

    db = SessionLocal()
    fetcher = DataFetcher(db)

    # Determine symbols
    if args.symbols:
        symbols = [s.strip().upper() for s in args.symbols.split(",")]
    else:
        symbols = fetcher.get_symbols_from_portfolios()

        if not symbols:
            print("No portfolio holdings found")
            print("Nothing to update")
            db.close()
            return

    print(f"=== Daily Price Update ===")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Source: {args.source}")
    print(f"Symbols to update: {len(symbols)}")
    print(f"Symbols: {', '.join(symbols)}")
    print("")

    total_saved = 0
    failed = []

    for i, symbol in enumerate(symbols, 1):
        print(f"[{i}/{len(symbols)}] Updating {symbol}...", end=" ")

        try:
            # Fetch last 5 days to ensure we have the latest
            count = fetcher.fetch_and_save(symbol, period="5d", source=args.source)
            total_saved += count
            print(f"✓ ({count} records)")

        except Exception as e:
            print(f"✗ Error: {e}")
            failed.append(symbol)
            continue

    db.close()

    print(f"\n=== Summary ===")
    print(f"Successfully updated: {len(symbols) - len(failed)}/{len(symbols)}")
    print(f"Total records saved: {total_saved}")

    if failed:
        print(f"Failed symbols: {', '.join(failed)}")
        sys.exit(1)
    else:
        print("All updates successful")
        sys.exit(0)


if __name__ == "__main__":
    main()
