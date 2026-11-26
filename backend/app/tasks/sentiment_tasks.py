"""
Sentiment collection and analysis tasks.

These tasks handle:
- Scraping Reddit and news sources
- Processing raw content
- Running sentiment analysis
- Stock mention detection
"""
from celery import Task
from celery.utils.log import get_task_logger
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from app.celery_app import celery_app
from app.core.db import SessionLocal
from app.models.sentiment import RawContent, ScrapedSource, Stock, ContentStockMention

logger = get_task_logger(__name__)


class DatabaseTask(Task):
    """
    Base task class that provides database session management.
    Automatically closes session after task completion or failure.
    """
    _db = None

    @property
    def db(self):
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        """Close database session after task completes"""
        if self._db is not None:
            self._db.close()
            self._db = None


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    acks_late=True,  # rerun if worker dies; safe because inserts are idempotent
    name='collect_reddit_content',
    max_retries=3,
    default_retry_delay=60,  # 1 minute
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,  # 10 minutes max
    retry_jitter=True,
)
def collect_reddit_content_task(
    self,
    subreddits: Optional[List[str]] = None,
    limit: int = 100,
    scrape_comments: bool = True,
    comment_limit: int = 50
):
    """
    Collect content from Reddit subreddits using PRAW.

    Args:
        subreddits: List of subreddit names to scrape. If None, uses active sources from DB.
        limit: Maximum number of posts to fetch per subreddit.
        scrape_comments: Whether to scrape comments from posts.
        comment_limit: Maximum number of comments to scrape per post.

    Returns:
        dict: Statistics about collected content
    """
    try:
        logger.info(
            f"Starting Reddit collection. Subreddits: {subreddits}, Limit: {limit}, "
            f"Comments: {'yes' if scrape_comments else 'no'}"
        )

        # Import here to avoid circular dependencies
        from app.services.reddit_scraper import get_reddit_scraper

        scraper = get_reddit_scraper()

        # Check if authenticated
        if not scraper.is_authenticated():
            logger.error("Reddit scraper not authenticated. Check REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET.")
            return {
                "status": "error",
                "reason": "not_authenticated",
                "message": "Reddit API credentials not configured"
            }

        # Scrape subreddits
        results = scraper.scrape_multiple_subreddits(
            db=self.db,
            subreddit_names=subreddits,
            limit_per_subreddit=limit,
            scrape_comments=scrape_comments,
            comment_limit=comment_limit
        )

        if not results:
            logger.warning("No subreddits scraped")
            return {"status": "skipped", "reason": "no_active_sources"}

        # Aggregate statistics
        total_posts = sum(s.get('posts_scraped', 0) for s in results.values())
        total_comments = sum(s.get('comments_scraped', 0) for s in results.values())
        total_skipped = sum(s.get('posts_skipped', 0) for s in results.values())

        logger.info(
            f"Reddit collection complete. Posts: {total_posts}, Comments: {total_comments}, "
            f"Skipped: {total_skipped}"
        )

        return {
            "status": "success",
            "subreddits_scraped": len(results),
            "posts_collected": total_posts,
            "comments_collected": total_comments,
            "posts_skipped": total_skipped,
            "subreddit_breakdown": results,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Reddit collection failed: {e}", exc_info=True)
        # Retry with exponential backoff
        raise


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    acks_late=True,  # rerun if worker dies; safe because inserts are idempotent
    name='collect_news_content',
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
)
def collect_news_content_task(
    self,
    feeds: Optional[List[Dict[str, str]]] = None,
    filter_stocks: bool = True
):
    """
    Collect content from RSS news feeds.

    Args:
        feeds: List of dicts with 'url' and 'name'. If None, uses active sources from DB.
        filter_stocks: Whether to filter for stock-related content

    Returns:
        dict: Statistics about collected content
    """
    try:
        logger.info(f"Starting news RSS collection. Filter stocks: {filter_stocks}")

        # Import here to avoid circular dependencies
        from app.services.news_aggregator import get_news_aggregator

        aggregator = get_news_aggregator()

        # Parse feeds
        results = aggregator.parse_multiple_feeds(
            db=self.db,
            feeds=feeds,
            filter_stocks=filter_stocks
        )

        if not results:
            logger.warning("No feeds parsed")
            return {"status": "skipped", "reason": "no_active_sources"}

        # Aggregate statistics
        total_articles = sum(s.get('articles_scraped', 0) for s in results.values())
        total_skipped = sum(s.get('articles_skipped', 0) for s in results.values())
        total_filtered = sum(s.get('articles_filtered', 0) for s in results.values())

        logger.info(
            f"News collection complete. Articles: {total_articles}, "
            f"Skipped: {total_skipped}, Filtered: {total_filtered}"
        )

        return {
            "status": "success",
            "feeds_scraped": len(results),
            "articles_collected": total_articles,
            "articles_skipped": total_skipped,
            "articles_filtered": total_filtered,
            "feed_breakdown": results,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"News collection failed: {e}", exc_info=True)
        raise


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name='process_unprocessed_content',
    max_retries=3,
    default_retry_delay=300,  # 5 minutes
    autoretry_for=(Exception,),
)
def process_unprocessed_content_task(self, batch_size: int = 100):
    """
    Process raw content that hasn't been analyzed yet.

    This includes:
    - Stock ticker extraction
    - Sentiment analysis
    - Quality filtering

    Args:
        batch_size: Number of content items to process in one batch

    Returns:
        dict: Processing statistics
    """
    try:
        logger.info(f"Processing unprocessed content. Batch size: {batch_size}")

        # Get unprocessed content
        unprocessed = self.db.query(RawContent).filter(
            RawContent.processed == False
        ).limit(batch_size).all()

        if not unprocessed:
            logger.info("No unprocessed content found")
            return {"status": "success", "processed_count": 0}

        logger.info(f"Found {len(unprocessed)} unprocessed items")

        # NOTE: Actual processing logic will be implemented in later stories
        # For now, just mark as processed
        processed_count = 0
        for content in unprocessed:
            content.processed = True
            content.processed_at = datetime.utcnow()
            processed_count += 1

        self.db.commit()

        return {
            "status": "success",
            "processed_count": processed_count,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Content processing failed: {e}", exc_info=True)
        self.db.rollback()
        raise
