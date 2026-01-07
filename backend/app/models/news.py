"""News and sentiment data models"""
from sqlalchemy import Column, String, Text, Float, DateTime, Integer, Index, JSON
from sqlalchemy.sql import func
from datetime import datetime

from app.core.db import Base


class NewsArticle(Base):
    """News article with sentiment analysis"""
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)

    # Article identification
    article_id = Column(String(255), unique=True, nullable=False, index=True)
    source = Column(String(100), nullable=False, index=True)  # newsapi, finnhub, etc.

    # Article content
    title = Column(String(500), nullable=False)
    description = Column(Text)
    content = Column(Text)
    url = Column(String(1000), nullable=False)
    image_url = Column(String(1000))

    # Metadata
    author = Column(String(255))
    published_at = Column(DateTime, nullable=False, index=True)

    # Stock association
    symbols = Column(JSON, default=list)  # List of related stock symbols

    # Sentiment analysis
    sentiment_score = Column(Float)  # -1 to 1 (negative to positive)
    sentiment_label = Column(String(20))  # negative, neutral, positive
    sentiment_confidence = Column(Float)  # 0 to 1

    # Additional sentiment details
    sentiment_details = Column(JSON)  # Detailed sentiment breakdown

    # Categories and keywords
    category = Column(String(100))
    keywords = Column(JSON, default=list)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    analyzed_at = Column(DateTime)  # When sentiment analysis was performed

    # Indexes for common queries
    __table_args__ = (
        Index('idx_news_symbol_published', 'published_at'),
        Index('idx_news_sentiment', 'sentiment_label', 'sentiment_score'),
    )

    def __repr__(self):
        return f"<NewsArticle(id={self.id}, title='{self.title[:50]}...', sentiment={self.sentiment_label})>"


class SentimentHistory(Base):
    """Aggregated sentiment history for symbols"""
    __tablename__ = "sentiment_history"

    id = Column(Integer, primary_key=True, index=True)

    # Symbol and time
    symbol = Column(String(10), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)

    # Aggregated sentiment metrics
    avg_sentiment = Column(Float)  # Average sentiment score
    sentiment_std = Column(Float)  # Standard deviation
    positive_count = Column(Integer, default=0)
    neutral_count = Column(Integer, default=0)
    negative_count = Column(Integer, default=0)
    total_articles = Column(Integer, default=0)

    # Weighted sentiment (by source credibility)
    weighted_sentiment = Column(Float)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())

    __table_args__ = (
        Index('idx_sentiment_symbol_date', 'symbol', 'date'),
    )

    def __repr__(self):
        return f"<SentimentHistory(symbol='{self.symbol}', date={self.date}, avg={self.avg_sentiment})>"
