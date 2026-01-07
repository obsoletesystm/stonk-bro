#!/usr/bin/env python3
"""
Backfill missing stock data

Identifies gaps in historical data and fills them.

Usage:
    python scripts/backfill_data.py --symbols AAPL --start-date 2020-01-01
    python scripts/backfill_data.py --from-portfolio --start-date 2023-01-01
"""
import argparse
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import SessionLocal
from app.services.data_fetcher import DataFetcher
from app.models.stock import StockQuote
from sqlalchemy import func


def get_data_gaps(db, symbol: str, start_date: datetime) -> list:
    """
    Identify gaps in historical data

    Returns list of date ranges with missing data
    """
    # Get all dates we have
    dates = db.query(StockQuote.timestamp).filter(
        StockQuote.symbol == symbol,
        StockQuote.timestamp >= start_date
    ).order_by(StockQuote.timestamp).all()

    if not dates:
        return [(start_date, datetime.now())]

    dates = [d[0].date() for d in dates]

    # Find gaps (more than 5 days between records, accounting for weekends)
    gaps = []
    for i in range(len(dates) - 1):
        current = dates[i]
        next_date = dates[i + 1]
        diff = (next_date - current).days

        # If gap is more than 7 days (likely missing data)
        if diff > 7:
            gaps.append((current, next_date))

    return gaps


def main():
    parser = argparse.ArgumentParser(description="Backfill missing stock data")
    parser.add_argument(
        "--symbols",
        type=str,
        help="Comma-separated list of stock symbols"
    )
    parser.add_argument(
        "--from-portfolio",
        action="store_true",
        help="Backfill data for all portfolio holdings"
    )
    parser.add_argument(
        "--start-date",
        type=str,
        required=True,
        help="Start date for backfill (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--source",
        type=str,
        default="yfinance",
        choices=["yfinance", "alpha_vantage"],
        help="Data source (default: yfinance)"
    )

    args = parser.parse_args()

    # Parse start date
    try:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    except ValueError:
        print(f"Invalid date format: {args.start_date}")
        print("Use YYYY-MM-DD format (e.g., 2020-01-01)")
        return

    # Determine symbols
    db = SessionLocal()
    fetcher = DataFetcher(db)

    if args.from_portfolio:
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

    print(f"=== Backfilling Data ===")
    print(f"Start date: {start_date.date()}")
    print(f"Source: {args.source}")
    print(f"Symbols: {len(symbols)}")
    print("")

    total_backfilled = 0

    for i, symbol in enumerate(symbols, 1):
        print(f"\n[{i}/{len(symbols)}] Analyzing {symbol}...")

        # Check current data coverage
        count = db.query(func.count()).select_from(StockQuote).filter(
            StockQuote.symbol == symbol,
            StockQuote.timestamp >= start_date
        ).scalar()

        print(f"  Current records: {count}")

        # Get gaps
        gaps = get_data_gaps(db, symbol, start_date)

        if gaps:
            print(f"  Found {len(gaps)} gap(s)")
            for gap_start, gap_end in gaps:
                print(f"    Gap: {gap_start} to {gap_end}")

        # Fetch full period to fill gaps
        print(f"  Fetching data from {start_date.date()} to now...")

        try:
            # Calculate period
            days_diff = (datetime.now() - start_date).days

            if days_diff <= 30:
                period = "1mo"
            elif days_diff <= 90:
                period = "3mo"
            elif days_diff <= 180:
                period = "6mo"
            elif days_diff <= 365:
                period = "1y"
            elif days_diff <= 730:
                period = "2y"
            elif days_diff <= 1825:
                period = "5y"
            else:
                period = "max"

            saved = fetcher.fetch_and_save(symbol, period=period, source=args.source)
            total_backfilled += saved

            print(f"  ✓ Backfilled {saved} records")

        except Exception as e:
            print(f"  ✗ Error: {e}")
            continue

    db.close()

    print(f"\n=== Summary ===")
    print(f"Total records backfilled: {total_backfilled}")
    print(f"Symbols processed: {len(symbols)}")
    print("")


if __name__ == "__main__":
    main()
