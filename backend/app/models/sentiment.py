"""Sentiment data models for social media scraping and analysis"""
from sqlalchemy import (
    Column, String, Text, Integer, BigInteger, Float, Boolean,
    DateTime, ForeignKey, Index, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.db import Base
import enum


class SourceType(str, enum.Enum):
    """Supported data source types"""
    REDDIT = "reddit"
    NEWS = "news"


class RawContent(Base):
    """
    Raw scraped content from social media and news sources.
    Stores original content with metadata for later processing.
    """
    __tablename__ = "raw_content"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # Source information
    source = Column(String(20), nullable=False, index=True)
    source_id = Column(String(255), nullable=True)  # Original ID from source (Reddit post ID, tweet ID, etc.)

    # Content
    content = Column(Text, nullable=False)
    title = Column(Text, nullable=True)  # For Reddit posts and news articles

    # Author metadata (for quality filtering)
    author = Column(String(255), nullable=True)
    author_karma = Column(Integer, nullable=True)  # Reddit karma
    author_followers = Column(Integer, nullable=True)  # Twitter followers
    author_account_age_days = Column(Integer, nullable=True)

    # Engagement metrics
    upvotes = Column(Integer, nullable=True)
    downvotes = Column(Integer, nullable=True)
    comments_count = Column(Integer, nullable=True)
    retweets = Column(Integer, nullable=True)
    likes = Column(Integer, nullable=True)

    # Source-specific metadata
    subreddit = Column(String(100), nullable=True)  # For Reddit
    is_comment = Column(Boolean, default=False)  # True if Reddit comment vs post
    parent_id = Column(String(255), nullable=True)  # Parent post/comment ID

    # URLs and references
    url = Column(Text, nullable=True)

    # Timestamps
    collected_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at = Column(DateTime(timezone=True), nullable=True)  # Original post time

    # Processing status
    processed = Column(Boolean, default=False, index=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index('idx_raw_content_collected', 'collected_at'),
        Index('idx_raw_content_source_collected', 'source', 'collected_at'),
        Index('idx_raw_content_unprocessed', 'processed', postgresql_where='processed = false'),
        Index('idx_raw_content_source_id', 'source', 'source_id', unique=True),
    )

    def __repr__(self):
        return f"<RawContent {self.id} source={self.source} collected={self.collected_at}>"


class ScrapedSource(Base):
    """
    Configuration for data sources to scrape.
    Tracks which subreddits, Twitter accounts, and RSS feeds to monitor.
    """
    __tablename__ = "scraped_sources"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Source type and identifier
    source_type = Column(String(20), nullable=False)  # reddit, twitter, news
    identifier = Column(String(255), nullable=False)  # subreddit name, twitter handle, RSS URL

    # Display name
    name = Column(String(255), nullable=True)

    # Configuration
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=5)  # 1-10, higher = more frequent scraping

    # Rate limiting
    min_interval_minutes = Column(Integer, default=60)  # Minimum time between scrapes
    last_scraped_at = Column(DateTime(timezone=True), nullable=True)

    # Quality settings
    min_karma = Column(Integer, nullable=True)  # For Reddit: minimum author karma
    min_followers = Column(Integer, nullable=True)  # For Twitter: minimum followers

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Stats
    total_items_scraped = Column(BigInteger, default=0)
    last_error = Column(Text, nullable=True)
    error_count = Column(Integer, default=0)

    __table_args__ = (
        Index('idx_scraped_sources_active', 'is_active', 'source_type'),
        Index('idx_scraped_sources_type_id', 'source_type', 'identifier', unique=True),
    )

    def __repr__(self):
        return f"<ScrapedSource {self.source_type}:{self.identifier}>"


class Stock(Base):
    """
    Reference table for identified stocks.
    Normalized stock information for FK relationships.
    """
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(10), unique=True, nullable=False, index=True)
    company_name = Column(String(255), nullable=True)
    sector = Column(String(100), nullable=True)
    exchange = Column(String(50), nullable=True)

    # Metadata
    is_active = Column(Boolean, default=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_stocks_symbol', 'symbol'),
    )

    def __repr__(self):
        return f"<Stock {self.symbol}>"


class ContentStockMention(Base):
    """
    Junction table linking raw content to mentioned stocks.
    Enables many-to-many relationship between content and stocks.
    """
    __tablename__ = "content_stock_mentions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    content_id = Column(BigInteger, ForeignKey('raw_content.id', ondelete='CASCADE'), nullable=False)
    stock_id = Column(Integer, ForeignKey('stocks.id', ondelete='CASCADE'), nullable=False)

    # How the stock was mentioned
    mention_type = Column(String(20), default='cashtag')  # cashtag, company_name, inferred
    confidence = Column(Float, default=1.0)  # Confidence score for fuzzy matches

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_content_stock_mentions_content', 'content_id'),
        Index('idx_content_stock_mentions_stock', 'stock_id'),
        Index('idx_content_stock_mentions_unique', 'content_id', 'stock_id', unique=True),
    )

    def __repr__(self):
        return f"<ContentStockMention content={self.content_id} stock={self.stock_id}>"
