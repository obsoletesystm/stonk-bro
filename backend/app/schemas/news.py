"""Pydantic schemas for news and sentiment"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class SentimentDetails(BaseModel):
    """Detailed sentiment breakdown"""
    label: str
    score: float
    confidence: float
    normalized_score: float


class NewsArticleResponse(BaseModel):
    """News article response"""
    id: int
    article_id: str
    source: str
    title: str
    description: Optional[str] = None
    url: str
    image_url: Optional[str] = None
    author: Optional[str] = None
    published_at: datetime
    symbols: List[str] = Field(default_factory=list)
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    sentiment_confidence: Optional[float] = None
    category: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NewsListResponse(BaseModel):
    """List of news articles with pagination"""
    articles: List[NewsArticleResponse]
    total: int
    page: int
    page_size: int
    has_next: bool


class SentimentHistoryResponse(BaseModel):
    """Sentiment history response"""
    symbol: str
    date: datetime
    avg_sentiment: Optional[float] = None
    sentiment_std: Optional[float] = None
    positive_count: int = 0
    neutral_count: int = 0
    negative_count: int = 0
    total_articles: int = 0
    weighted_sentiment: Optional[float] = None

    class Config:
        from_attributes = True


class SentimentSummaryResponse(BaseModel):
    """Aggregated sentiment summary"""
    symbol: str
    period_start: datetime
    period_end: datetime
    avg_sentiment: float
    median_sentiment: float
    std_sentiment: float
    positive_count: int
    neutral_count: int
    negative_count: int
    total_articles: int
    positive_ratio: float
    negative_ratio: float
    sentiment_trend: Optional[str] = None  # improving, declining, stable
    history: List[SentimentHistoryResponse] = Field(default_factory=list)


class SentimentAnalysisRequest(BaseModel):
    """Request to analyze sentiment"""
    text: str


class SentimentAnalysisResponse(BaseModel):
    """Sentiment analysis response"""
    label: str
    score: float
    confidence: float
    normalized_score: float
    timestamp: datetime = Field(default_factory=datetime.now)


class NewsFetchRequest(BaseModel):
    """Request to fetch news"""
    symbols: Optional[List[str]] = None
    query: Optional[str] = None
    days: int = Field(default=7, ge=1, le=30)
    analyze_sentiment: bool = True


class NewsFetchResponse(BaseModel):
    """News fetch response"""
    articles_fetched: int
    articles_saved: int
    sources_used: List[str]
    message: str


class NewsSearchRequest(BaseModel):
    """News search request"""
    symbols: Optional[List[str]] = None
    sentiment: Optional[str] = Field(None, pattern="^(positive|neutral|negative)$")
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    source: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
