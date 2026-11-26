"""
Reddit scraper service using PRAW (Python Reddit API Wrapper).

This module handles:
- Authenticating with Reddit API
- Scraping posts and comments from configured subreddits
- Storing raw content in the database
- Rate limit handling with exponential backoff
"""
import logging
import time
from datetime import datetime
from typing import List, Dict, Set, Optional
import praw
from praw.exceptions import APIException, PRAWException
from prawcore.exceptions import ResponseException, RequestException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.sentiment import RawContent, ScrapedSource, SourceType
from app.services.raw_content_store import save_raw_content

logger = logging.getLogger(__name__)


class RedditScraperService:
    """
    Reddit scraper using PRAW for authentic API access.

    Requires environment variables:
    - REDDIT_CLIENT_ID
    - REDDIT_CLIENT_SECRET
    - REDDIT_USER_AGENT
    """

    def __init__(self):
        """Initialize PRAW Reddit client"""
        self.reddit = None
        self._init_client()

    def _init_client(self):
        """Initialize PRAW Reddit client with credentials"""
        try:
            # Check for required credentials
            client_id = getattr(settings, 'REDDIT_CLIENT_ID', None)
            client_secret = getattr(settings, 'REDDIT_CLIENT_SECRET', None)
            user_agent = getattr(settings, 'REDDIT_USER_AGENT', 'stonk-bro:v1.0.0')

            if not client_id or not client_secret:
                logger.warning(
                    "Reddit credentials not configured. "
                    "Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in .env file. "
                    "Get credentials at: https://www.reddit.com/prefs/apps"
                )
                return

            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent,
                check_for_async=False  # We're using synchronous mode
            )

            # Test authentication
            self.reddit.user.me()
            logger.info("Reddit API authentication successful (read-only mode)")

        except Exception as e:
            logger.error(f"Failed to initialize Reddit client: {e}")
            self.reddit = None

    def is_authenticated(self) -> bool:
        """Check if Reddit API is authenticated and ready"""
        return self.reddit is not None

    def _handle_rate_limit(self, retry_count: int = 0):
        """
        Handle rate limiting with exponential backoff.

        Args:
            retry_count: Current retry attempt number
        """
        wait_time = min(60 * (2 ** retry_count), 600)  # Max 10 minutes
        logger.warning(f"Rate limited. Waiting {wait_time} seconds (retry {retry_count})")
        time.sleep(wait_time)

    def scrape_submission(
        self,
        submission: praw.models.Submission,
        db: Session,
        scrape_comments: bool = True,
        comment_limit: int = 50
    ) -> List[RawContent]:
        """
        Scrape a single Reddit submission (post) and optionally its comments.

        Args:
            submission: PRAW Submission object
            db: Database session
            scrape_comments: Whether to scrape comments
            comment_limit: Maximum number of comments to scrape

        Returns:
            List of RawContent objects created
        """
        contents = []

        try:
            subreddit_name = submission.subreddit.display_name
            post = dict(
                source=SourceType.REDDIT.value,
                source_id=submission.fullname,
                content=submission.selftext[:50000] if submission.selftext else "",
                title=submission.title[:500] if submission.title else None,
                author=str(submission.author)[:100] if submission.author else '[deleted]',
                author_karma=submission.author.link_karma if submission.author else None,
                upvotes=submission.score,
                comments_count=submission.num_comments,
                subreddit=subreddit_name,
                is_comment=False,
                url=submission.url[:2000] if submission.url else None,
                collected_at=datetime.utcnow(),
                created_at=datetime.fromtimestamp(submission.created_utc),
                processed=False,
            )
            if not save_raw_content(db, **post):
                logger.debug(f"Post {submission.id} already exists, skipping")
                return contents
            contents.append(post)

            logger.debug(
                f"Scraped post: r/{submission.subreddit.display_name} - "
                f"{submission.title[:50]}... (score: {submission.score}, "
                f"comments: {submission.num_comments})"
            )

            # Scrape comments if requested
            if scrape_comments and submission.num_comments > 0:
                # Expand all comments (may take time for large threads)
                submission.comments.replace_more(limit=0)

                # Get top-level comments up to limit
                comment_count = 0
                for comment in submission.comments.list()[:comment_limit]:
                    if comment_count >= comment_limit:
                        break

                    # Skip deleted/removed comments
                    if not hasattr(comment, 'body') or comment.body in ['[deleted]', '[removed]']:
                        continue

                    comment_row = dict(
                        source=SourceType.REDDIT.value,
                        source_id=comment.fullname,
                        content=comment.body[:10000],
                        author=str(comment.author)[:100] if comment.author else '[deleted]',
                        author_karma=comment.author.link_karma if comment.author else None,
                        upvotes=comment.score,
                        subreddit=subreddit_name,
                        is_comment=True,
                        parent_id=submission.fullname,
                        collected_at=datetime.utcnow(),
                        created_at=datetime.fromtimestamp(comment.created_utc),
                        processed=False,
                    )
                    if not save_raw_content(db, **comment_row):
                        continue
                    contents.append(comment_row)
                    comment_count += 1

                logger.debug(f"Scraped {comment_count} comments from post {submission.id}")

        except Exception as e:
            logger.error(f"Error scraping submission {submission.id}: {e}")

        return contents

    def scrape_subreddit(
        self,
        db: Session,
        subreddit_name: str,
        limit: int = 100,
        time_filter: str = 'day',
        sort: str = 'hot',
        scrape_comments: bool = True,
        comment_limit: int = 50
    ) -> Dict[str, int]:
        """
        Scrape posts from a subreddit.

        Args:
            db: Database session
            subreddit_name: Name of subreddit (without r/ prefix)
            limit: Number of posts to scrape
            time_filter: Time filter for 'top' sort (hour, day, week, month, year, all)
            sort: Sort type (hot, new, top, rising, controversial)
            scrape_comments: Whether to scrape comments from posts
            comment_limit: Maximum comments per post

        Returns:
            Dict with statistics (posts_scraped, comments_scraped, posts_skipped)
        """
        if not self.is_authenticated():
            logger.error("Reddit client not authenticated. Cannot scrape subreddit.")
            return {'posts_scraped': 0, 'comments_scraped': 0, 'posts_skipped': 0, 'error': 'not_authenticated'}

        stats = {
            'posts_scraped': 0,
            'comments_scraped': 0,
            'posts_skipped': 0
        }

        retry_count = 0
        max_retries = 3

        while retry_count < max_retries:
            try:
                logger.info(
                    f"Scraping r/{subreddit_name} (sort={sort}, limit={limit}, "
                    f"comments={'yes' if scrape_comments else 'no'})"
                )

                subreddit = self.reddit.subreddit(subreddit_name)

                # Get submissions based on sort type
                if sort == 'hot':
                    submissions = subreddit.hot(limit=limit)
                elif sort == 'new':
                    submissions = subreddit.new(limit=limit)
                elif sort == 'top':
                    submissions = subreddit.top(time_filter=time_filter, limit=limit)
                elif sort == 'rising':
                    submissions = subreddit.rising(limit=limit)
                elif sort == 'controversial':
                    submissions = subreddit.controversial(time_filter=time_filter, limit=limit)
                else:
                    logger.error(f"Invalid sort type: {sort}")
                    return stats

                # Scrape each submission
                for submission in submissions:
                    contents = self.scrape_submission(
                        submission,
                        db,
                        scrape_comments=scrape_comments,
                        comment_limit=comment_limit
                    )

                    if contents:
                        # Count posts and comments
                        posts = sum(1 for c in contents if not c['is_comment'])
                        comments = sum(1 for c in contents if c['is_comment'])

                        stats['posts_scraped'] += posts
                        stats['comments_scraped'] += comments
                    else:
                        stats['posts_skipped'] += 1

                    # Commit after each post to avoid losing data on errors
                    try:
                        db.commit()
                    except Exception as e:
                        logger.error(f"Database commit error: {e}")
                        db.rollback()

                    # Rate limiting - Reddit allows 60 requests per minute
                    time.sleep(1)  # 1 second between posts

                logger.info(
                    f"Scraped r/{subreddit_name}: {stats['posts_scraped']} posts, "
                    f"{stats['comments_scraped']} comments, {stats['posts_skipped']} skipped"
                )

                break  # Success, exit retry loop

            except APIException as e:
                if 'RATELIMIT' in str(e):
                    self._handle_rate_limit(retry_count)
                    retry_count += 1
                else:
                    logger.error(f"Reddit API exception: {e}")
                    break

            except (ResponseException, RequestException) as e:
                logger.error(f"Reddit network exception: {e}")
                self._handle_rate_limit(retry_count)
                retry_count += 1

            except PRAWException as e:
                logger.error(f"PRAW exception scraping r/{subreddit_name}: {e}")
                break

            except Exception as e:
                logger.error(f"Unexpected error scraping r/{subreddit_name}: {e}")
                break

        return stats

    def scrape_multiple_subreddits(
        self,
        db: Session,
        subreddit_names: Optional[List[str]] = None,
        limit_per_subreddit: int = 100,
        scrape_comments: bool = True,
        comment_limit: int = 50
    ) -> Dict[str, Dict[str, int]]:
        """
        Scrape multiple subreddits.

        Args:
            db: Database session
            subreddit_names: List of subreddit names. If None, uses active sources from DB.
            limit_per_subreddit: Posts to scrape per subreddit
            scrape_comments: Whether to scrape comments
            comment_limit: Max comments per post

        Returns:
            Dict mapping subreddit name to stats
        """
        if not self.is_authenticated():
            logger.error("Reddit client not authenticated")
            return {}

        # Get subreddits from database if not provided
        if subreddit_names is None:
            sources = db.query(ScrapedSource).filter(
                ScrapedSource.source_type == SourceType.REDDIT.value,
                ScrapedSource.is_active == True
            ).all()
            subreddit_names = [s.identifier for s in sources]

        if not subreddit_names:
            logger.warning("No subreddits configured for scraping")
            return {}

        logger.info(f"Scraping {len(subreddit_names)} subreddits: {subreddit_names}")

        results = {}

        for subreddit_name in subreddit_names:
            stats = self.scrape_subreddit(
                db,
                subreddit_name,
                limit=limit_per_subreddit,
                scrape_comments=scrape_comments,
                comment_limit=comment_limit
            )
            results[subreddit_name] = stats

            # Delay between subreddits to be respectful
            time.sleep(2)

        # Calculate totals
        total_posts = sum(s.get('posts_scraped', 0) for s in results.values())
        total_comments = sum(s.get('comments_scraped', 0) for s in results.values())

        logger.info(
            f"Scraping complete: {total_posts} posts, {total_comments} comments "
            f"from {len(subreddit_names)} subreddits"
        )

        return results


# Singleton instance
_reddit_scraper = None


def get_reddit_scraper() -> RedditScraperService:
    """Get singleton Reddit scraper instance"""
    global _reddit_scraper
    if _reddit_scraper is None:
        _reddit_scraper = RedditScraperService()
    return _reddit_scraper
