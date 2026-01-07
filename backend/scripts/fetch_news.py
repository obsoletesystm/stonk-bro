#!/usr/bin/env python3
"""
Fetch news and analyze sentiment

Usage:
    python scripts/fetch_news.py --symbols AAPL,MSFT
    python scripts/fetch_news.py --from-portfolio
    python scripts/fetch_news.py --symbols GOOGL --days 14
"""
import argparse
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import SessionLocal
from app.services.news_fetcher import NewsFetcher
from app.services.data_fetcher import DataFetcher
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Fetch news and analyze sentiment")

    # Symbol selection
    symbol_group = parser.add_mutually_exclusive_group(required=True)
    symbol_group.add_argument(
        "--symbols",
        type=str,
        help="Comma-separated list of stock symbols"
    )
    symbol_group.add_argument(
        "--from-portfolio",
        action="store_true",
        help="Fetch news for all portfolio holdings"
    )

    # Fetch configuration
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Days of news to fetch (default: 7)"
    )
    parser.add_argument(
        "--no-sentiment",
        action="store_true",
        help="Skip sentiment analysis"
    )
    parser.add_argument(
        "--use-newsapi",
        action="store_true",
        help="Use NewsAPI (requires API key)"
    )

    args = parser.parse_args()

    # Determine symbols
    db = SessionLocal()

    if args.from_portfolio:
        data_fetcher = DataFetcher(db)
        symbols = data_fetcher.get_symbols_from_portfolios()
        if not symbols:
            print("No portfolio holdings found")
            db.close()
            return
    else:
        symbols = [s.strip().upper() for s in args.symbols.split(",")]

    print(f"{'='*70}")
    print(f"News Fetching - {datetime.now()}")
    print(f"{'='*70}")
    print(f"Symbols: {', '.join(symbols)}")
    print(f"Days: {args.days}")
    print(f"Sentiment Analysis: {not args.no_sentiment}")
    print()

    # Initialize fetcher
    fetcher = NewsFetcher(db)

    try:
        # Fetch news
        if args.use_newsapi:
            print("Fetching from NewsAPI...")
            articles = fetcher.fetch_from_newsapi(symbols=symbols, days=args.days)
        else:
            print("Using mock news for testing...")
            articles = fetcher.fetch_mock_news(symbols, count=min(len(symbols) * 5, 50))

        if not articles:
            print("No articles fetched")
            db.close()
            return

        print(f"Fetched {len(articles)} articles")
        print()

        # Save articles with sentiment analysis
        print("Saving articles and analyzing sentiment...")
        saved = fetcher.save_articles_with_sentiment(
            articles,
            analyze_sentiment=not args.no_sentiment
        )

        print(f"✓ Saved {saved} new articles")
        print()

        # Update sentiment history
        print("Updating sentiment history...")
        for symbol in symbols:
            fetcher.update_sentiment_history(symbol)
            print(f"✓ Updated sentiment history for {symbol}")

        print()
        print("=== Summary ===")
        print(f"Total articles fetched: {len(articles)}")
        print(f"New articles saved: {saved}")
        print(f"Symbols processed: {len(symbols)}")

        if not args.no_sentiment:
            # Print sentiment summary for each symbol
            from app.services.news_service import NewsService

            print()
            print("=== Sentiment Summary ===")
            for symbol in symbols:
                summary = NewsService.get_sentiment_summary(db, symbol, args.days)

                if summary['total_articles'] > 0:
                    print(f"\n{symbol}:")
                    print(f"  Total Articles: {summary['total_articles']}")
                    print(f"  Avg Sentiment: {summary['avg_sentiment']:.3f}")
                    print(f"  Positive: {summary['positive_count']} ({summary['positive_ratio']:.1%})")
                    print(f"  Negative: {summary['negative_count']} ({summary['negative_ratio']:.1%})")
                    print(f"  Trend: {summary['sentiment_trend']}")

    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

    print()


if __name__ == "__main__":
    main()
