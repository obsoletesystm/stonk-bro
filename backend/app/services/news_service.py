"""News retrieval and query service"""
import logging
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, cast, Text

from app.models.news import NewsArticle, SentimentHistory

logger = logging.getLogger(__name__)


class NewsService:
    """Service for retrieving and querying news articles"""

    @staticmethod
    def get_news(
        db: Session,
        symbols: Optional[List[str]] = None,
        sentiment: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        source: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[NewsArticle], int]:
        """
        Get news articles with filtering and pagination

        Args:
            db: Database session
            symbols: Filter by stock symbols
            sentiment: Filter by sentiment label
            from_date: Start date
            to_date: End date
            source: Filter by news source
            page: Page number
            page_size: Items per page

        Returns:
            Tuple of (articles list, total count)
        """
        query = db.query(NewsArticle)

        # Apply filters
        if symbols:
            # Filter articles that contain any of the specified symbols
            # Use text cast to avoid JSON LIKE operator issues
            symbol_filters = [cast(NewsArticle.symbols, Text).like(f'%"{s}"%') for s in symbols]
            query = query.filter(or_(*symbol_filters))

        if sentiment:
            query = query.filter(NewsArticle.sentiment_label == sentiment)

        if from_date:
            query = query.filter(NewsArticle.published_at >= from_date)

        if to_date:
            query = query.filter(NewsArticle.published_at <= to_date)

        if source:
            query = query.filter(NewsArticle.source == source)

        # Get total count
        total = query.count()

        # Apply pagination and sorting
        articles = query.order_by(desc(NewsArticle.published_at))\
            .offset((page - 1) * page_size)\
            .limit(page_size)\
            .all()

        return articles, total

    @staticmethod
    def get_article_by_id(db: Session, article_id: str) -> Optional[NewsArticle]:
        """Get article by article_id"""
        return db.query(NewsArticle).filter(
            NewsArticle.article_id == article_id
        ).first()

    @staticmethod
    def get_recent_news(
        db: Session,
        symbols: Optional[List[str]] = None,
        hours: int = 24,
        limit: int = 50
    ) -> List[NewsArticle]:
        """
        Get recent news articles

        Args:
            db: Database session
            symbols: Filter by symbols
            hours: Hours to look back
            limit: Maximum articles to return

        Returns:
            List of recent articles
        """
        cutoff = datetime.now() - timedelta(hours=hours)

        query = db.query(NewsArticle).filter(
            NewsArticle.published_at >= cutoff
        )

        if symbols:
            # Use text cast to avoid JSON LIKE operator issues
            symbol_filters = [cast(NewsArticle.symbols, Text).like(f'%"{s}"%') for s in symbols]
            query = query.filter(or_(*symbol_filters))

        articles = query.order_by(desc(NewsArticle.published_at))\
            .limit(limit)\
            .all()

        return articles

    @staticmethod
    def get_sentiment_history(
        db: Session,
        symbol: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> List[SentimentHistory]:
        """
        Get sentiment history for a symbol

        Args:
            db: Database session
            symbol: Stock symbol
            from_date: Start date
            to_date: End date

        Returns:
            List of sentiment history records
        """
        query = db.query(SentimentHistory).filter(
            SentimentHistory.symbol == symbol.upper()
        )

        if from_date:
            query = query.filter(SentimentHistory.date >= from_date)

        if to_date:
            query = query.filter(SentimentHistory.date <= to_date)

        history = query.order_by(SentimentHistory.date).all()

        return history

    @staticmethod
    def get_sentiment_summary(
        db: Session,
        symbol: str,
        days: int = 7
    ) -> dict:
        """
        Get aggregated sentiment summary for a symbol

        Args:
            db: Database session
            symbol: Stock symbol
            days: Number of days to analyze

        Returns:
            Dictionary with sentiment summary
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Get articles
        # Use text cast to avoid JSON LIKE operator issues
        articles = db.query(NewsArticle).filter(
            cast(NewsArticle.symbols, Text).like(f'%"{symbol.upper()}"%'),
            NewsArticle.published_at >= start_date,
            NewsArticle.published_at <= end_date,
            NewsArticle.sentiment_score.isnot(None)
        ).all()

        if not articles:
            return {
                'symbol': symbol,
                'period_start': start_date,
                'period_end': end_date,
                'avg_sentiment': 0.0,
                'median_sentiment': 0.0,
                'std_sentiment': 0.0,
                'positive_count': 0,
                'neutral_count': 0,
                'negative_count': 0,
                'total_articles': 0,
                'positive_ratio': 0.0,
                'negative_ratio': 0.0,
                'sentiment_trend': 'stable'
            }

        # Calculate metrics
        scores = [a.sentiment_score for a in articles]
        labels = [a.sentiment_label for a in articles]

        avg_sentiment = sum(scores) / len(scores)
        median_sentiment = sorted(scores)[len(scores) // 2]
        variance = sum((s - avg_sentiment) ** 2 for s in scores) / len(scores)
        std_sentiment = variance ** 0.5

        positive_count = labels.count('positive')
        neutral_count = labels.count('neutral')
        negative_count = labels.count('negative')

        # Determine trend
        mid_point = len(articles) // 2
        first_half_avg = sum(scores[:mid_point]) / mid_point if mid_point > 0 else 0
        second_half_avg = sum(scores[mid_point:]) / (len(scores) - mid_point) if len(scores) > mid_point else 0

        if second_half_avg > first_half_avg + 0.1:
            sentiment_trend = 'improving'
        elif second_half_avg < first_half_avg - 0.1:
            sentiment_trend = 'declining'
        else:
            sentiment_trend = 'stable'

        return {
            'symbol': symbol,
            'period_start': start_date,
            'period_end': end_date,
            'avg_sentiment': avg_sentiment,
            'median_sentiment': median_sentiment,
            'std_sentiment': std_sentiment,
            'positive_count': positive_count,
            'neutral_count': neutral_count,
            'negative_count': negative_count,
            'total_articles': len(articles),
            'positive_ratio': positive_count / len(articles),
            'negative_ratio': negative_count / len(articles),
            'sentiment_trend': sentiment_trend
        }

    @staticmethod
    def get_top_news_by_sentiment(
        db: Session,
        symbol: str,
        sentiment_type: str = 'positive',
        limit: int = 10,
        days: int = 7
    ) -> List[NewsArticle]:
        """
        Get top news articles by sentiment

        Args:
            db: Database session
            symbol: Stock symbol
            sentiment_type: 'positive' or 'negative'
            limit: Number of articles
            days: Days to look back

        Returns:
            List of top articles
        """
        cutoff = datetime.now() - timedelta(days=days)

        # Use text cast to avoid JSON LIKE operator issues
        query = db.query(NewsArticle).filter(
            cast(NewsArticle.symbols, Text).like(f'%"{symbol.upper()}"%'),
            NewsArticle.published_at >= cutoff,
            NewsArticle.sentiment_label == sentiment_type
        )

        if sentiment_type == 'positive':
            articles = query.order_by(desc(NewsArticle.sentiment_score))\
                .limit(limit)\
                .all()
        else:  # negative
            articles = query.order_by(NewsArticle.sentiment_score)\
                .limit(limit)\
                .all()

        return articles

    @staticmethod
    def get_news_stats(db: Session, symbol: Optional[str] = None) -> dict:
        """
        Get news statistics

        Args:
            db: Database session
            symbol: Optional symbol filter

        Returns:
            Dictionary with statistics
        """
        query = db.query(NewsArticle)

        if symbol:
            # Use text cast to avoid JSON LIKE operator issues
            query = query.filter(cast(NewsArticle.symbols, Text).like(f'%"{symbol.upper()}"%'))

        total_articles = query.count()

        with_sentiment = query.filter(
            NewsArticle.sentiment_score.isnot(None)
        ).count()

        # Count by source
        sources = db.query(
            NewsArticle.source,
            func.count(NewsArticle.id).label('count')
        )

        if symbol:
            # Use text cast to avoid JSON LIKE operator issues
            sources = sources.filter(cast(NewsArticle.symbols, Text).like(f'%"{symbol.upper()}"%'))

        sources = sources.group_by(NewsArticle.source).all()

        # Count by sentiment
        sentiments = db.query(
            NewsArticle.sentiment_label,
            func.count(NewsArticle.id).label('count')
        )

        if symbol:
            # Use text cast to avoid JSON LIKE operator issues
            sentiments = sentiments.filter(cast(NewsArticle.symbols, Text).like(f'%"{symbol.upper()}"%'))

        sentiments = sentiments.filter(
            NewsArticle.sentiment_label.isnot(None)
        ).group_by(NewsArticle.sentiment_label).all()

        return {
            'total_articles': total_articles,
            'with_sentiment': with_sentiment,
            'by_source': {s.source: s.count for s in sources},
            'by_sentiment': {s.sentiment_label: s.count for s in sentiments}
        }
