"""
RSS news aggregator service.

This module handles:
- Parsing RSS/Atom feeds
- Filtering stock-related content
- Extracting article metadata
- Rate limit handling
- Error recovery
"""
import logging
import time
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib.parse import urlparse

import feedparser
import requests
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.sentiment import RawContent, ScrapedSource, SourceType
from app.services.raw_content_store import save_raw_content

logger = logging.getLogger(__name__)


class NewsAggregatorService:
    """
    RSS/Atom feed aggregator for financial news.

    Handles parsing of RSS feeds from various financial news sources,
    filters for stock-related content, and stores articles for analysis.
    """

    # Stock-related keywords for filtering
    STOCK_KEYWORDS = [
        # General
        'stock', 'stocks', 'market', 'markets', 'trading', 'trader',
        'investor', 'investment', 'equity', 'equities', 'share', 'shares',

        # Exchanges
        'nyse', 'nasdaq', 'tsx', 'dow', 's&p', 'tsx-v',

        # Metrics
        'earnings', 'revenue', 'profit', 'loss', 'eps', 'pe ratio',
        'dividend', 'ipo', 'merger', 'acquisition',

        # Symbols (pattern)
        r'\$[A-Z]{1,5}',  # Cashtag like $AAPL
        r'\b[A-Z]{2,5}\b',  # Ticker symbols

        # Market terms
        'bull', 'bear', 'rally', 'selloff', 'crash', 'surge',
        'price target', 'analyst', 'upgrade', 'downgrade',
        'buyback', 'stock split', 'reverse split'
    ]

    # Minimum article age to avoid scraping too frequently
    MIN_ARTICLE_AGE = timedelta(hours=1)

    def __init__(self):
        """Initialize news aggregator"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; StockResearchBot/1.0)'
        })

    def _is_stock_related(self, text: str) -> bool:
        """
        Check if text contains stock-related keywords.

        Args:
            text: Text to analyze (title + description)

        Returns:
            True if text appears to be stock-related
        """
        if not text:
            return False

        text_lower = text.lower()

        # Check each keyword
        for keyword in self.STOCK_KEYWORDS:
            if keyword.startswith(r'\$') or keyword.startswith(r'\b'):
                # Regex pattern
                if re.search(keyword, text, re.IGNORECASE):
                    return True
            else:
                # Simple substring match
                if keyword in text_lower:
                    return True

        return False

    def _parse_entry_date(self, entry) -> Optional[datetime]:
        """
        Parse publication date from feed entry.

        Args:
            entry: feedparser entry object

        Returns:
            datetime object or None if parsing fails
        """
        # Try various date fields
        date_fields = [
            'published_parsed',
            'updated_parsed',
            'created_parsed'
        ]

        for field in date_fields:
            if hasattr(entry, field):
                time_struct = getattr(entry, field)
                if time_struct:
                    try:
                        return datetime(*time_struct[:6])
                    except (TypeError, ValueError):
                        continue

        # Fallback to current time
        return datetime.utcnow()

    def _extract_article_id(self, entry) -> str:
        """
        Extract unique article identifier.

        Args:
            entry: feedparser entry object

        Returns:
            Unique identifier string
        """
        # Try various ID fields
        if hasattr(entry, 'id') and entry.id:
            return entry.id

        if hasattr(entry, 'link') and entry.link:
            return entry.link

        # Fallback: hash of title + date
        if hasattr(entry, 'title') and entry.title:
            date_str = str(self._parse_entry_date(entry))
            return f"{entry.title[:50]}_{date_str}"

        # Last resort: timestamp
        return f"article_{datetime.utcnow().isoformat()}"

    def _extract_author(self, entry) -> Optional[str]:
        """
        Extract author from feed entry.

        Args:
            entry: feedparser entry object

        Returns:
            Author name or None
        """
        if hasattr(entry, 'author') and entry.author:
            return entry.author[:100]

        if hasattr(entry, 'authors') and entry.authors:
            return entry.authors[0].get('name', '')[:100]

        if hasattr(entry, 'creator') and entry.creator:
            return entry.creator[:100]

        return None

    def _extract_description(self, entry) -> str:
        """
        Extract article description/summary.

        Args:
            entry: feedparser entry object

        Returns:
            Description text
        """
        # Try various description fields
        if hasattr(entry, 'summary') and entry.summary:
            return entry.summary

        if hasattr(entry, 'description') and entry.description:
            return entry.description

        if hasattr(entry, 'content') and entry.content:
            return entry.content[0].get('value', '')

        return ""

    def parse_feed(
        self,
        db: Session,
        feed_url: str,
        source_name: str,
        filter_stocks: bool = True
    ) -> Dict[str, int]:
        """
        Parse a single RSS/Atom feed.

        Args:
            db: Database session
            feed_url: URL of the RSS/Atom feed
            source_name: Human-readable source name
            filter_stocks: Whether to filter for stock-related content

        Returns:
            Dict with statistics (articles_scraped, articles_skipped)
        """
        stats = {'articles_scraped': 0, 'articles_skipped': 0, 'articles_filtered': 0}

        try:
            logger.info(f"Parsing feed: {source_name} ({feed_url})")

            # feedparser has no timeout of its own, so download first
            resp = self.session.get(feed_url, timeout=15)
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)

            # Check for errors
            if hasattr(feed, 'bozo') and feed.bozo:
                if hasattr(feed, 'bozo_exception'):
                    logger.warning(f"Feed parse error for {source_name}: {feed.bozo_exception}")
                # Continue anyway - feedparser is forgiving

            if not hasattr(feed, 'entries') or not feed.entries:
                logger.warning(f"No entries found in feed: {source_name}")
                return stats

            logger.info(f"Found {len(feed.entries)} entries in {source_name}")

            for entry in feed.entries:
                try:
                    # Extract article ID
                    article_id = self._extract_article_id(entry)

                    # Extract fields
                    title = entry.title if hasattr(entry, 'title') else ""
                    description = self._extract_description(entry)
                    link = entry.link if hasattr(entry, 'link') else ""
                    author = self._extract_author(entry)
                    published_date = self._parse_entry_date(entry)

                    # Filter for stock content if enabled
                    if filter_stocks:
                        combined_text = f"{title} {description}"
                        if not self._is_stock_related(combined_text):
                            stats['articles_filtered'] += 1
                            continue

                    saved = save_raw_content(
                        db,
                        source=SourceType.NEWS.value,
                        source_id=article_id[:255],
                        content=description[:50000] if description else "",
                        title=title[:500] if title else None,
                        author=author,
                        url=link[:2000] if link else None,
                        collected_at=datetime.utcnow(),
                        created_at=published_date,
                        processed=False,
                    )
                    if not saved:
                        stats['articles_skipped'] += 1
                        continue
                    stats['articles_scraped'] += 1

                except Exception as e:
                    logger.error(f"Error parsing entry from {source_name}: {e}")
                    continue

            # Commit all articles
            db.commit()

            logger.info(
                f"Parsed {source_name}: {stats['articles_scraped']} new articles, "
                f"{stats['articles_skipped']} skipped, {stats['articles_filtered']} filtered"
            )

            # Rate limiting between feeds
            time.sleep(1)

        except Exception as e:
            logger.error(f"Error parsing feed {source_name}: {e}")
            db.rollback()

        return stats

    def parse_multiple_feeds(
        self,
        db: Session,
        feeds: Optional[List[Dict[str, str]]] = None,
        filter_stocks: bool = True
    ) -> Dict[str, Dict[str, int]]:
        """
        Parse multiple RSS/Atom feeds.

        Args:
            db: Database session
            feeds: List of dicts with 'url' and 'name'. If None, uses active sources from DB.
            filter_stocks: Whether to filter for stock-related content

        Returns:
            Dict mapping feed name to stats
        """
        # Get feeds from database if not provided
        if feeds is None:
            sources = db.query(ScrapedSource).filter(
                ScrapedSource.source_type == SourceType.NEWS.value,
                ScrapedSource.is_active == True
            ).all()
            feeds = [
                {'url': s.identifier, 'name': s.name or s.identifier}
                for s in sources
            ]

        if not feeds:
            logger.warning("No RSS feeds configured for aggregation")
            return {}

        logger.info(f"Aggregating {len(feeds)} RSS feeds")

        results = {}

        for feed in feeds:
            feed_url = feed.get('url')
            feed_name = feed.get('name', feed_url)

            stats = self.parse_feed(
                db=db,
                feed_url=feed_url,
                source_name=feed_name,
                filter_stocks=filter_stocks
            )
            results[feed_name] = stats

        # Calculate totals
        total_scraped = sum(s.get('articles_scraped', 0) for s in results.values())
        total_skipped = sum(s.get('articles_skipped', 0) for s in results.values())
        total_filtered = sum(s.get('articles_filtered', 0) for s in results.values())

        logger.info(
            f"News aggregation complete: {total_scraped} articles from {len(feeds)} feeds, "
            f"{total_skipped} skipped, {total_filtered} filtered"
        )

        return results


# Singleton instance
_news_aggregator = None


def get_news_aggregator() -> NewsAggregatorService:
    """Get singleton news aggregator instance"""
    global _news_aggregator
    if _news_aggregator is None:
        _news_aggregator = NewsAggregatorService()
    return _news_aggregator
