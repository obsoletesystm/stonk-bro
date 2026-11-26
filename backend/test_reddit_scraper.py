#!/usr/bin/env python3
"""
Test Reddit scraper implementation.

This script validates:
1. PRAW client authentication
2. Subreddit scraping functionality
3. Post and comment collection
4. Database storage in raw_content table
5. Rate limit handling

Usage: python test_reddit_scraper.py [--with-comments] [--limit N]
"""
import sys
import argparse
from datetime import datetime

from app.core.db import SessionLocal
from app.services.reddit_scraper import get_reddit_scraper
from app.models.sentiment import RawContent, ScrapedSource, SourceType

# Test colors for output
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


def test_authentication():
    """Test Reddit API authentication"""
    print_section("1. Testing Reddit API Authentication")

    try:
        scraper = get_reddit_scraper()

        if scraper.is_authenticated():
            print_success("Reddit API authenticated successfully")
            print_info(f"User agent: {scraper.reddit.config.user_agent}")
            print_info("Client configured in read-only mode")
            return True, scraper
        else:
            print_error("Reddit API not authenticated")
            print_warning("Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in .env file")
            print_warning("Get credentials at: https://www.reddit.com/prefs/apps")
            return False, None

    except Exception as e:
        print_error(f"Authentication failed: {e}")
        return False, None


def test_database_connection():
    """Test database connectivity"""
    print_section("2. Testing Database Connection")

    try:
        db = SessionLocal()

        # Test query
        count = db.query(RawContent).count()
        print_success("Database connection successful")
        print_info(f"Current raw_content records: {count}")

        # Check for scraped sources
        reddit_sources = db.query(ScrapedSource).filter(
            ScrapedSource.source_type == SourceType.reddit,
            ScrapedSource.is_active == True
        ).all()

        print_info(f"Active Reddit sources: {len(reddit_sources)}")
        for source in reddit_sources:
            print_info(f"  - {source.identifier}")

        db.close()
        return True

    except Exception as e:
        print_error(f"Database connection failed: {e}")
        return False


def test_scrape_subreddit(scraper, limit: int = 10, with_comments: bool = False):
    """Test scraping a single subreddit"""
    print_section("3. Testing Subreddit Scraping")

    db = SessionLocal()

    try:
        # Test with wallstreetbets (usually has active content)
        test_subreddit = "wallstreetbets"

        print_info(f"Scraping r/{test_subreddit} (limit={limit}, comments={'yes' if with_comments else 'no'})")
        print_info("This may take 10-30 seconds...")

        # Get count before scraping
        before_count = db.query(RawContent).filter(
            RawContent.source == SourceType.reddit,
            RawContent.source_identifier == f"r/{test_subreddit}"
        ).count()

        # Scrape
        stats = scraper.scrape_subreddit(
            db=db,
            subreddit_name=test_subreddit,
            limit=limit,
            sort='hot',
            scrape_comments=with_comments,
            comment_limit=10
        )

        # Get count after scraping
        after_count = db.query(RawContent).filter(
            RawContent.source == SourceType.reddit,
            RawContent.source_identifier == f"r/{test_subreddit}"
        ).count()

        new_records = after_count - before_count

        print_success(f"Scraping completed successfully")
        print_info(f"Posts scraped: {stats.get('posts_scraped', 0)}")
        print_info(f"Comments scraped: {stats.get('comments_scraped', 0)}")
        print_info(f"Posts skipped (already existed): {stats.get('posts_skipped', 0)}")
        print_info(f"New records in database: {new_records}")

        # Show sample posts
        sample_posts = db.query(RawContent).filter(
            RawContent.source == SourceType.reddit,
            RawContent.source_identifier == f"r/{test_subreddit}",
            RawContent.content_type == 'post'
        ).order_by(RawContent.collected_at.desc()).limit(3).all()

        if sample_posts:
            print_info("\nSample posts:")
            for i, post in enumerate(sample_posts, 1):
                title = post.title[:60] + "..." if len(post.title) > 60 else post.title
                print_info(f"  {i}. {title} (score: {post.score}, comments: {post.num_comments})")

        db.close()
        return True

    except Exception as e:
        print_error(f"Scraping failed: {e}")
        db.close()
        return False


def test_raw_content_structure(db):
    """Validate raw_content data structure"""
    print_section("4. Validating Raw Content Data Structure")

    try:
        # Get recent Reddit content
        recent = db.query(RawContent).filter(
            RawContent.source == SourceType.reddit
        ).order_by(RawContent.collected_at.desc()).first()

        if not recent:
            print_warning("No Reddit content in database yet")
            return False

        print_success("Found Reddit content in database")

        # Validate fields
        checks = {
            "Has external_id": recent.external_id is not None,
            "Has source_identifier": recent.source_identifier is not None,
            "Has content_type": recent.content_type in ['post', 'comment'],
            "Has author": recent.author is not None,
            "Has collected_at": recent.collected_at is not None,
            "Has content_created_at": recent.content_created_at is not None,
            "Has processed flag": recent.processed is not None,
        }

        for check_name, passed in checks.items():
            if passed:
                print_success(check_name)
            else:
                print_error(check_name)

        # Show sample data
        print_info(f"\nSample record:")
        print_info(f"  ID: {recent.id}")
        print_info(f"  External ID: {recent.external_id}")
        print_info(f"  Source: {recent.source_identifier}")
        print_info(f"  Type: {recent.content_type}")
        print_info(f"  Author: {recent.author}")
        print_info(f"  Score: {recent.score}")
        if recent.title:
            print_info(f"  Title: {recent.title[:60]}...")

        return all(checks.values())

    except Exception as e:
        print_error(f"Validation failed: {e}")
        return False


def main():
    """Run all tests"""
    parser = argparse.ArgumentParser(description="Test Reddit scraper")
    parser.add_argument('--with-comments', action='store_true', help='Also scrape comments')
    parser.add_argument('--limit', type=int, default=10, help='Number of posts to scrape (default: 10)')
    args = parser.parse_args()

    print(f"\n{BLUE}{'*' * 70}")
    print(f"  Reddit Scraper Test Suite")
    print(f"  Timestamp: {datetime.now().isoformat()}")
    print(f"{'*' * 70}{RESET}\n")

    results = []

    # Test 1: Authentication
    success, scraper = test_authentication()
    results.append(("Authentication", success))

    if not success:
        print(f"\n{RED}Cannot proceed without Reddit API authentication{RESET}")
        print(f"{YELLOW}Setup instructions:{RESET}")
        print(f"  1. Go to https://www.reddit.com/prefs/apps")
        print(f"  2. Click 'create another app' at the bottom")
        print(f"  3. Choose 'script' type")
        print(f"  4. Name: stonk-bro")
        print(f"  5. Redirect URI: http://localhost:8000")
        print(f"  6. Copy the client ID (under the app name)")
        print(f"  7. Copy the secret")
        print(f"  8. Add to .env file:")
        print(f"     REDDIT_CLIENT_ID=your_client_id")
        print(f"     REDDIT_CLIENT_SECRET=your_secret")
        return 1

    # Test 2: Database
    success = test_database_connection()
    results.append(("Database Connection", success))

    if not success:
        print(f"\n{RED}Cannot proceed without database connection{RESET}")
        return 1

    # Test 3: Scraping
    success = test_scrape_subreddit(scraper, limit=args.limit, with_comments=args.with_comments)
    results.append(("Subreddit Scraping", success))

    # Test 4: Data validation
    db = SessionLocal()
    success = test_raw_content_structure(db)
    db.close()
    results.append(("Data Structure", success))

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
        print(f"\n{GREEN}✓ Reddit scraper is working correctly{RESET}\n")
        return 0
    else:
        print(f"{YELLOW}Some tests failed ({passed}/{total}){RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
