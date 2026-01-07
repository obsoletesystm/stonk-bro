"""News fetching service from multiple sources"""
import logging
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import requests
from sqlalchemy.orm import Session
from sqlalchemy import cast, Text

from app.models.news import NewsArticle, SentimentHistory
from app.services.sentiment_service import get_sentiment_analyzer
from app.core.config import settings

logger = logging.getLogger(__name__)


class NewsFetcher:
    """Fetch news from multiple sources"""

    def __init__(self, db: Session):
        """
        Initialize news fetcher

        Args:
            db: Database session
        """
        self.db = db
        self.sentiment_analyzer = None  # Lazy load

    def _get_sentiment_analyzer(self):
        """Lazy load sentiment analyzer"""
        if self.sentiment_analyzer is None:
            self.sentiment_analyzer = get_sentiment_analyzer()
        return self.sentiment_analyzer

    def _generate_article_id(self, url: str, published_at: datetime) -> str:
        """Generate unique article ID from URL and timestamp"""
        content = f"{url}_{published_at.isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()

    def fetch_from_newsapi(
        self,
        symbols: Optional[List[str]] = None,
        query: Optional[str] = None,
        days: int = 7,
        language: str = 'en'
    ) -> List[Dict[str, Any]]:
        """
        Fetch news from NewsAPI

        Args:
            symbols: List of stock symbols
            query: Custom search query
            days: Number of days of news to fetch
            language: Language code

        Returns:
            List of news articles
        """
        api_key = getattr(settings, 'NEWS_API_KEY', None)

        if not api_key:
            logger.warning("NEWS_API_KEY not configured, skipping NewsAPI")
            return []

        articles = []

        try:
            # Build query
            if query:
                search_query = query
            elif symbols:
                # Search for stock symbols and company names
                search_query = ' OR '.join(symbols)
            else:
                search_query = 'stock market'

            # Date range
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

            # API request
            url = 'https://newsapi.org/v2/everything'
            params = {
                'q': search_query,
                'from': from_date,
                'language': language,
                'sortBy': 'publishedAt',
                'apiKey': api_key,
                'pageSize': 100
            }

            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if data['status'] != 'ok':
                logger.error(f"NewsAPI error: {data.get('message')}")
                return []

            # Process articles
            for article in data.get('articles', []):
                try:
                    # Parse published date
                    published_at = datetime.fromisoformat(
                        article['publishedAt'].replace('Z', '+00:00')
                    )

                    # Generate article ID
                    article_id = self._generate_article_id(
                        article['url'],
                        published_at
                    )

                    # Determine related symbols (simple keyword matching)
                    related_symbols = []
                    if symbols:
                        title_and_desc = f"{article.get('title', '')} {article.get('description', '')}".upper()
                        for symbol in symbols:
                            if symbol.upper() in title_and_desc:
                                related_symbols.append(symbol.upper())

                    articles.append({
                        'article_id': article_id,
                        'source': 'newsapi',
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'content': article.get('content', ''),
                        'url': article['url'],
                        'image_url': article.get('urlToImage'),
                        'author': article.get('author'),
                        'published_at': published_at,
                        'symbols': related_symbols,
                        'category': article.get('source', {}).get('name')
                    })

                except Exception as e:
                    logger.warning(f"Error processing NewsAPI article: {e}")
                    continue

            logger.info(f"Fetched {len(articles)} articles from NewsAPI")

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching from NewsAPI: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in NewsAPI fetch: {e}")

        return articles

    def fetch_mock_news(
        self,
        symbols: List[str],
        count: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Generate mock news articles for testing

        Args:
            symbols: List of stock symbols
            count: Number of articles to generate

        Returns:
            List of mock news articles
        """
        articles = []

        news_templates = [
            ("beats earnings expectations", "positive"),
            ("stock surges on strong quarterly results", "positive"),
            ("announces new product launch", "positive"),
            ("reports disappointing quarterly results", "negative"),
            ("faces regulatory challenges", "negative"),
            ("stock drops on weak guidance", "negative"),
            ("maintains steady performance", "neutral"),
            ("announces dividend increase", "positive"),
            ("experiences technical difficulties", "negative"),
            ("expands into new markets", "positive")
        ]

        for i in range(count):
            symbol = symbols[i % len(symbols)]
            template, sentiment_hint = news_templates[i % len(news_templates)]

            title = f"{symbol} {template}"
            description = f"Latest update on {symbol} stock performance and market analysis."

            published_at = datetime.now() - timedelta(hours=i * 2)
            article_id = self._generate_article_id(f"mock_{symbol}_{i}", published_at)

            articles.append({
                'article_id': article_id,
                'source': 'mock',
                'title': title,
                'description': description,
                'content': f"Full article content about {symbol}. {description}",
                'url': f"https://example.com/news/{symbol.lower()}/{i}",
                'image_url': None,
                'author': 'Mock Author',
                'published_at': published_at,
                'symbols': [symbol],
                'category': 'Business'
            })

        logger.info(f"Generated {len(articles)} mock articles")
        return articles

    def save_articles_with_sentiment(
        self,
        articles: List[Dict[str, Any]],
        analyze_sentiment: bool = True
    ) -> int:
        """
        Save articles to database with sentiment analysis

        Args:
            articles: List of article dictionaries
            analyze_sentiment: Whether to run sentiment analysis

        Returns:
            Number of articles saved
        """
        saved_count = 0

        for article_data in articles:
            try:
                # Check if article already exists
                existing = self.db.query(NewsArticle).filter(
                    NewsArticle.article_id == article_data['article_id']
                ).first()

                if existing:
                    logger.debug(f"Article already exists: {article_data['article_id']}")
                    continue

                # Analyze sentiment if requested
                if analyze_sentiment:
                    analyzer = self._get_sentiment_analyzer()
                    sentiment = analyzer.analyze_article(
                        title=article_data.get('title', ''),
                        description=article_data.get('description'),
                        content=article_data.get('content')
                    )

                    article_data['sentiment_score'] = sentiment['normalized_score']
                    article_data['sentiment_label'] = sentiment['label']
                    article_data['sentiment_confidence'] = sentiment['confidence']
                    article_data['sentiment_details'] = sentiment.get('components')
                    article_data['analyzed_at'] = datetime.now()

                # Create article
                article = NewsArticle(**article_data)
                self.db.add(article)
                saved_count += 1

            except Exception as e:
                logger.error(f"Error saving article: {e}")
                continue

        # Commit all articles
        try:
            self.db.commit()
            logger.info(f"Saved {saved_count} new articles")
        except Exception as e:
            logger.error(f"Error committing articles: {e}")
            self.db.rollback()
            saved_count = 0

        return saved_count

    def update_sentiment_history(
        self,
        symbol: str,
        date: Optional[datetime] = None
    ):
        """
        Update aggregated sentiment history for a symbol

        Args:
            symbol: Stock symbol
            date: Date to aggregate (defaults to today)
        """
        if date is None:
            date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        try:
            # Get all articles for this symbol and date
            start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)

            # Use text cast to avoid JSON LIKE operator issues
            articles = self.db.query(NewsArticle).filter(
                cast(NewsArticle.symbols, Text).like(f'%"{symbol}"%'),
                NewsArticle.published_at >= start_of_day,
                NewsArticle.published_at < end_of_day,
                NewsArticle.sentiment_score.isnot(None)
            ).all()

            if not articles:
                logger.debug(f"No articles found for {symbol} on {date.date()}")
                return

            # Calculate aggregated metrics
            scores = [a.sentiment_score for a in articles]
            labels = [a.sentiment_label for a in articles]

            avg_sentiment = sum(scores) / len(scores)
            sentiment_std = (sum((s - avg_sentiment) ** 2 for s in scores) / len(scores)) ** 0.5

            positive_count = labels.count('positive')
            neutral_count = labels.count('neutral')
            negative_count = labels.count('negative')

            # Check if history entry exists
            history = self.db.query(SentimentHistory).filter(
                SentimentHistory.symbol == symbol,
                SentimentHistory.date == date
            ).first()

            if history:
                # Update existing
                history.avg_sentiment = avg_sentiment
                history.sentiment_std = sentiment_std
                history.positive_count = positive_count
                history.neutral_count = neutral_count
                history.negative_count = negative_count
                history.total_articles = len(articles)
                history.weighted_sentiment = avg_sentiment  # Can add weights later
                history.updated_at = datetime.now()
            else:
                # Create new
                history = SentimentHistory(
                    symbol=symbol,
                    date=date,
                    avg_sentiment=avg_sentiment,
                    sentiment_std=sentiment_std,
                    positive_count=positive_count,
                    neutral_count=neutral_count,
                    negative_count=negative_count,
                    total_articles=len(articles),
                    weighted_sentiment=avg_sentiment
                )
                self.db.add(history)

            self.db.commit()
            logger.info(f"Updated sentiment history for {symbol} on {date.date()}")

        except Exception as e:
            logger.error(f"Error updating sentiment history: {e}")
            self.db.rollback()
