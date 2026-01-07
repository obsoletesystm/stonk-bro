#!/usr/bin/env python3
"""
Fetch historical stock data

Usage:
    python scripts/fetch_historical_data.py --symbols AAPL,GOOGL,MSFT --years 5
    python scripts/fetch_historical_data.py --from-portfolio --years 2
    python scripts/fetch_historical_data.py --symbols AAPL --period max
"""
import argparse
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import SessionLocal
from app.services.data_fetcher import DataFetcher


def main():
    parser = argparse.ArgumentParser(description="Fetch historical stock data")
    parser.add_argument(
        "--symbols",
        type=str,
        help="Comma-separated list of stock symbols (e.g., AAPL,GOOGL,MSFT)"
    )
    parser.add_argument(
        "--from-portfolio",
        action="store_true",
        help="Fetch data for all symbols in portfolio holdings"
    )
    parser.add_argument(
        "--years",
        type=int,
        default=1,
        help="Number of years of history to fetch (default: 1)"
    )
    parser.add_argument(
        "--period",
        type=str,
        help="Period to fetch (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)"
    )
    parser.add_argument(
        "--source",
        type=str,
        default="yfinance",
        choices=["yfinance", "alpha_vantage"],
        help="Data source (default: yfinance)"
    )

    args = parser.parse_args()

    # Determine symbols to fetch
    symbols = []

    if args.from_portfolio:
        db = SessionLocal()
        fetcher = DataFetcher(db)
        symbols = fetcher.get_symbols_from_portfolios()
        db.close()

        if not symbols:
            print("No symbols found in portfolio holdings")
            print("Add holdings first or specify --symbols")
            return

        print(f"Found {len(symbols)} symbols in portfolio: {', '.join(symbols)}")

    elif args.symbols:
        symbols = [s.strip().upper() for s in args.symbols.split(",")]

    else:
        print("Error: Must specify either --symbols or --from-portfolio")
        parser.print_help()
        return

    # Determine period
    if args.period:
        period = args.period
    else:
        # Convert years to period
        year_to_period = {
            1: "1y",
            2: "2y",
            5: "5y",
            10: "10y"
        }
        period = year_to_period.get(args.years, f"{args.years}y")

    print(f"\n=== Fetching Historical Data ===")
    print(f"Source: {args.source}")
    print(f"Period: {period}")
    print(f"Symbols: {len(symbols)}")
    print("")

    # Fetch data for each symbol
    db = SessionLocal()
    fetcher = DataFetcher(db)

    total_saved = 0

    for i, symbol in enumerate(symbols, 1):
        print(f"\n[{i}/{len(symbols)}] Processing {symbol}...")

        try:
            count = fetcher.fetch_and_save(symbol, period=period, source=args.source)
            total_saved += count
            print(f"✓ {symbol}: Saved {count} records")

        except Exception as e:
            print(f"✗ {symbol}: Error - {e}")
            continue

    db.close()

    print(f"\n=== Summary ===")
    print(f"Total records saved: {total_saved}")
    print(f"Symbols processed: {len(symbols)}")
    print(f"Average records per symbol: {total_saved / len(symbols) if symbols else 0:.0f}")
    print("")


if __name__ == "__main__":
    main()
