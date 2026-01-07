#!/usr/bin/env python3
"""
Generate test stock data for indicator testing

Usage:
    python scripts/generate_test_data.py
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import SessionLocal
from app.models.stock import StockQuote


def generate_realistic_prices(base_price: float, days: int, volatility: float = 0.02):
    """Generate realistic OHLCV data with trends and volatility"""
    prices = []
    current_price = base_price

    for i in range(days):
        # Add some trending behavior
        trend = random.gauss(0.001, 0.003)  # Slight upward bias

        # Daily price movement
        daily_change = random.gauss(trend, volatility)
        current_price *= (1 + daily_change)

        # Generate OHLC
        day_volatility = abs(random.gauss(0, volatility * 0.5))
        high = current_price * (1 + day_volatility)
        low = current_price * (1 - day_volatility)
        open_price = random.uniform(low, high)
        close_price = current_price

        # Generate volume (more volume on volatile days)
        base_volume = 10_000_000
        volume = int(base_volume * (1 + abs(daily_change) * 10) * random.uniform(0.5, 1.5))

        prices.append({
            'open': round(open_price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(close_price, 2),
            'volume': volume
        })

    return prices


def create_test_data():
    """Create test data for multiple symbols"""
    db = SessionLocal()

    test_symbols = {
        'AAPL': {'base_price': 180.0, 'days': 250},
        'MSFT': {'base_price': 380.0, 'days': 250},
        'GOOGL': {'base_price': 140.0, 'days': 250},
        'TSLA': {'base_price': 250.0, 'days': 250},
        'NVDA': {'base_price': 500.0, 'days': 250},
    }

    print("=== Generating Test Data ===\n")

    total_records = 0
    end_date = datetime.now()

    for symbol, config in test_symbols.items():
        print(f"Generating {symbol}...")

        # Delete existing data for this symbol
        db.query(StockQuote).filter(StockQuote.symbol == symbol).delete()

        # Generate prices
        prices = generate_realistic_prices(
            config['base_price'],
            config['days'],
            volatility=0.02
        )

        # Create quotes
        records = []
        for i, price_data in enumerate(prices):
            timestamp = end_date - timedelta(days=config['days'] - i)

            quote = StockQuote(
                symbol=symbol,
                timestamp=timestamp,
                open=price_data['open'],
                high=price_data['high'],
                low=price_data['low'],
                close=price_data['close'],
                volume=price_data['volume']
            )
            records.append(quote)

        # Bulk insert
        db.bulk_save_objects(records)
        db.commit()

        print(f"  ✓ Created {len(records)} records")
        print(f"    Price range: ${min(p['low'] for p in prices):.2f} - ${max(p['high'] for p in prices):.2f}")
        print(f"    Date range: {records[0].timestamp.date()} to {records[-1].timestamp.date()}")
        print()

        total_records += len(records)

    db.close()

    print("=== Summary ===")
    print(f"Total records created: {total_records}")
    print(f"Symbols: {len(test_symbols)}")
    print(f"Ready for indicator testing!\n")


if __name__ == "__main__":
    create_test_data()
