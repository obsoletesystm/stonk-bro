#!/usr/bin/env python3
"""
Test RSS news aggregator implementation.

This script validates:
1. feedparser library installation
2. RSS feed parsing
3. Stock content filtering
4. Database storage in raw_content table
5. Multiple feed aggregation

Usage: python test_news_aggregator.py [--no-filter] [--limit N]
"""
import sys
import argparse
from datetime import datetime

from app.core.db import SessionLocal
from app.services.news_aggregator import get_news_aggregator
from app.models.sentiment import RawContent, ScrapedSource, SourceType

# Test colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_section(title):
    """Print a section header"""
    print(f"\n{BLUE}{'=' * 70}{RESET}")
    print(f"{BLUE}{title}{RESET}")
    print(f"{BLUE}{'=' * 70}{RESET}\n")


def print_success(message):
    """Print success message"""
    print(f"{GREEN}✓{RESET} {message}")


def print_error(message):
    """Print error message"""
    print(f"{RED}✗{RESET} {message}")


def print_warning(message):
    """Print warning message"""
    print(f"{YELLOW}⚠{RESET} {message}")


def print_info(message):
    """Print info message"""
    print(f"  {message}")


def test_feedparser_import():
    """Test feedparser library is installed"""
    print_section("1. Testing feedparser Library")

    try:
        import feedparser
        print_success("feedparser library imported successfully")
        print_info(f"feedparser version: {feedparser.__version__}")
        return True
    except ImportError as e:
        print_error(f"feedparser import failed: {e}")
        print_info("Install with: pip install feedparser==6.0.11")
        return False


def test_database_connection():
    """Test database connectivity"""
    print_section("2. Testing Database Connection")

    try:
        db = SessionLocal()

        # Test query
        count = db.query(RawContent).filter(
            RawContent.source == SourceType.news
        ).count()
        print_success("Database connection successful")
        print_info(f"Current news article records: {count}")

        # Check for scraped sources
        news_sources = db.query(ScrapedSource).filter(
            ScrapedSource.source_type == SourceType.news,
            ScrapedSource.is_active == True
        ).all()

        print_info(f"Active news sources: {len(news_sources)}")
        for source in news_sources:
            print_info(f"  - {source.name}: {source.identifier}")

        db.close()
        return True

    except Exception as e:
        print_error(f"Database connection failed: {e}")
        return False


def test_stock_filtering():
    """Test stock content filtering logic"""
    print_section("3. Testing Stock Content Filtering")

    aggregator = get_news_aggregator()

    # Test cases
    test_cases = [
        # Stock-related (should pass)
        ("Apple stock surges on earnings beat", True),
        ("AAPL hits new highs after iPhone sales", True),
        ("$TSLA rallies on production news", True),
        ("Nasdaq rises as tech stocks gain", True),
        ("Analyst upgrades Microsoft to buy", True),
        ("S&P 500 closes higher on strong earnings", True),
        ("Company announces stock buyback program", True),
        ("Tesla announces stock split", True),
        ("IPO expected to raise $2 billion", True),
        ("Dividend increased to $0.50 per share", True),

        # Not stock-related (should fail)
        ("Local weather forecast for tomorrow", False),
        ("New restaurant opens downtown", False),
        ("Sports team wins championship", False),
        ("Movie review: Latest blockbuster", False),
        ("Recipe for chocolate cake", False),
    ]

    passed = 0
    failed = 0

    for text, expected in test_cases:
        result = aggregator._is_stock_related(text)
        if result == expected:
            passed += 1
        else:
            failed += 1
            print_warning(f"Filter mismatch: '{text}' -> {result} (expected {expected})")

    print_info(f"Stock filtering tests: {passed} passed, {failed} failed")

    if failed == 0:
        print_success("All stock filtering tests passed")
        return True
    else:
        print_error(f"{failed} stock filtering tests failed")
        return False


def test_parse_single_feed(aggregator, limit: int = 5, filter_stocks: bool = True):
    """Test parsing a single RSS feed"""
    print_section("4. Testing Single Feed Parsing")

    db = SessionLocal()

    # Use Yahoo Finance feed as it's reliable
    test_feed = {
        'url': 'https://finance.yahoo.com/news/rssindex',
        'name': 'Yahoo Finance Test'
    }

    try:
        print_info(f"Parsing: {test_feed['name']}")
        print_info(f"URL: {test_feed['url']}")
        print_info(f"Stock filtering: {filter_stocks}")
        print_info("This may take 10-20 seconds...")

        # Get count before parsing
        before_count = db.query(RawContent).filter(
            RawContent.source == SourceType.news,
            RawContent.source_identifier == test_feed['name']
        ).count()

        # Parse
        stats = aggregator.parse_feed(
            db=db,
            feed_url=test_feed['url'],
            source_name=test_feed['name'],
            filter_stocks=filter_stocks
        )

        # Get count after parsing
        after_count = db.query(RawContent).filter(
            RawContent.source == SourceType.news,
            RawContent.source_identifier == test_feed['name']
        ).count()

        new_records = after_count - before_count

        print_success(f"Feed parsing completed")
        print_info(f"Articles scraped: {stats.get('articles_scraped', 0)}")
        print_info(f"Articles skipped (already existed): {stats.get('articles_skipped', 0)}")
        print_info(f"Articles filtered (not stock-related): {stats.get('articles_filtered', 0)}")
        print_info(f"New records in database: {new_records}")

        # Show sample articles
        sample_articles = db.query(RawContent).filter(
            RawContent.source == SourceType.news,
            RawContent.source_identifier == test_feed['name']
        ).order_by(RawContent.collected_at.desc()).limit(3).all()

        if sample_articles:
            print_info("\nSample articles:")
            for i, article in enumerate(sample_articles, 1):
                title = article.title or "No title"
                title_display = title[:60] + "..." if len(title) > 60 else title
                print_info(f"  {i}. {title_display}")
                if article.author:
                    print_info(f"     Author: {article.author}")
                if article.url:
                    print_info(f"     URL: {article.url[:60]}...")

        db.close()
        return True

    except Exception as e:
        print_error(f"Feed parsing failed: {e}")
        db.close()
        return False


def test_parse_multiple_feeds(aggregator, filter_stocks: bool = True):
    """Test parsing multiple RSS feeds"""
    print_section("5. Testing Multiple Feed Aggregation")

    db = SessionLocal()

    try:
        print_info("Aggregating feeds from database...")
        print_info("This may take 30-60 seconds...")

        # Get count before
        before_count = db.query(RawContent).filter(
            RawContent.source == SourceType.news
        ).count()

        # Parse all feeds
        results = aggregator.parse_multiple_feeds(
            db=db,
            feeds=None,  # Use database sources
            filter_stocks=filter_stocks
        )

        # Get count after
        after_count = db.query(RawContent).filter(
            RawContent.source == SourceType.news
        ).count()

        new_records = after_count - before_count

        print_success(f"Multi-feed aggregation completed")
        print_info(f"Feeds processed: {len(results)}")

        total_articles = sum(s.get('articles_scraped', 0) for s in results.values())
        total_skipped = sum(s.get('articles_skipped', 0) for s in results.values())
        total_filtered = sum(s.get('articles_filtered', 0) for s in results.values())

        print_info(f"Total articles scraped: {total_articles}")
        print_info(f"Total skipped: {total_skipped}")
        print_info(f"Total filtered: {total_filtered}")
        print_info(f"New records in database: {new_records}")

        # Show breakdown by feed
        if results:
            print_info("\nBreakdown by feed:")
            for feed_name, stats in results.items():
                scraped = stats.get('articles_scraped', 0)
                skipped = stats.get('articles_skipped', 0)
                filtered = stats.get('articles_filtered', 0)
                print_info(f"  {feed_name}: {scraped} scraped, {skipped} skipped, {filtered} filtered")

        db.close()
        return True

    except Exception as e:
        print_error(f"Multi-feed aggregation failed: {e}")
        db.close()
        return False


def show_existing_news_content():
    """Show existing news content in database"""
    print_section("6. Existing News Content in Database")

    db = SessionLocal()

    try:
        articles = db.query(RawContent).filter(
            RawContent.source == SourceType.news
        ).order_by(RawContent.collected_at.desc()).limit(10).all()

        if articles:
            print_info(f"Found {len(articles)} recent articles (showing up to 10):\n")
            for article in articles:
                title = article.title or "No title"
                title_display = title[:60] + "..." if len(title) > 60 else title
                print_info(f"  {title_display}")
                print_info(f"    Source: {article.source_identifier}")
                if article.author:
                    print_info(f"    Author: {article.author}")
                if article.url:
                    print_info(f"    URL: {article.url[:50]}...")
                print_info("")
        else:
            print_info("No news content in database yet")

        total = db.query(RawContent).filter(
            RawContent.source == SourceType.news
        ).count()
        print_info(f"Total news articles: {total}")

        db.close()
        return True

    except Exception as e:
        print_error(f"Failed to query news content: {e}")
        db.close()
        return False


def main():
    """Run all tests"""
    parser = argparse.ArgumentParser(description="Test RSS news aggregator")
    parser.add_argument('--no-filter', action='store_true', help='Disable stock filtering')
    parser.add_argument('--limit', type=int, default=5, help='Number of articles to scrape per feed (default: 5)')
    args = parser.parse_args()

    filter_stocks = not args.no_filter

    print(f"\n{BLUE}{'*' * 70}")
    print(f"  RSS News Aggregator Test Suite")
    print(f"  Timestamp: {datetime.now().isoformat()}")
    print(f"  Stock filtering: {filter_stocks}")
    print(f"{'*' * 70}{RESET}\n")

    print_warning("NOTE: RSS feed availability varies. Some feeds may be slow or temporarily down.")
    print_warning("Tests may take 30-90 seconds to complete.\n")

    results = []

    # Test 1: feedparser import
    success = test_feedparser_import()
    results.append(("feedparser Import", success))

    if not success:
        print(f"\n{RED}Cannot proceed without feedparser library{RESET}")
        print(f"{YELLOW}Install with: pip install feedparser==6.0.11{RESET}")
        return 1

    # Test 2: Database
    success = test_database_connection()
    results.append(("Database Connection", success))

    if not success:
        print(f"\n{RED}Cannot proceed without database connection{RESET}")
        return 1

    # Test 3: Stock filtering
    success = test_stock_filtering()
    results.append(("Stock Content Filtering", success))

    # Get aggregator instance
    aggregator = get_news_aggregator()

    # Test 4: Single feed parsing
    success = test_parse_single_feed(aggregator, limit=args.limit, filter_stocks=filter_stocks)
    results.append(("Single Feed Parsing", success))

    # Test 5: Multiple feed aggregation
    success = test_parse_multiple_feeds(aggregator, filter_stocks=filter_stocks)
    results.append(("Multiple Feed Aggregation", success))

    # Test 6: Show existing content
    success = show_existing_news_content()
    results.append(("Show Existing Content", success))

    # Print summary
    print_section("Test Summary")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        if success:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")

    print(f"\n{BLUE}{'=' * 70}{RESET}")
    if passed == total:
        print(f"{GREEN}All tests passed! ({passed}/{total}){RESET}")
        print(f"\n{GREEN}✓ RSS news aggregator is working correctly{RESET}\n")
        return 0
    else:
        print(f"{YELLOW}Some tests failed ({passed}/{total}){RESET}")
        print(f"\n{YELLOW}⚠ RSS feeds can be unreliable. Check feed URLs and try again.{RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
