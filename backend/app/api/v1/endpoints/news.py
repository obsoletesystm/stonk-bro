"""News and sentiment endpoints"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.core.db import get_db
from app.services.news_service import NewsService
from app.services.news_fetcher import NewsFetcher
from app.services.sentiment_service import get_sentiment_analyzer
from app.schemas import news as news_schemas
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/articles", response_model=news_schemas.NewsListResponse)
def get_news_articles(
    symbols: Optional[str] = Query(None, description="Comma-separated stock symbols"),
    sentiment: Optional[str] = Query(None, pattern="^(positive|neutral|negative)$"),
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    source: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get news articles with filtering and pagination

    Args:
        symbols: Filter by stock symbols (comma-separated)
        sentiment: Filter by sentiment (positive, neutral, negative)
        from_date: Start date
        to_date: End date
        source: Filter by news source
        page: Page number
        page_size: Items per page
        db: Database session

    Returns:
        Paginated list of news articles
    """
    try:
        # Parse symbols
        symbol_list = None
        if symbols:
            symbol_list = [s.strip().upper() for s in symbols.split(",")]

        # Get articles
        articles, total = NewsService.get_news(
            db,
            symbols=symbol_list,
            sentiment=sentiment,
            from_date=from_date,
            to_date=to_date,
            source=source,
            page=page,
            page_size=page_size
        )

        has_next = (page * page_size) < total

        return {
            'articles': articles,
            'total': total,
            'page': page,
            'page_size': page_size,
            'has_next': has_next
        }

    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/recent", response_model=List[news_schemas.NewsArticleResponse])
def get_recent_news(
    symbol: str,
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get recent news for a symbol

    Args:
        symbol: Stock symbol
        hours: Hours to look back
        limit: Maximum articles to return
        db: Database session

    Returns:
        List of recent articles
    """
    try:
        articles = NewsService.get_recent_news(
            db,
            symbols=[symbol.upper()],
            hours=hours,
            limit=limit
        )

        return articles

    except Exception as e:
        logger.error(f"Error fetching recent news for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/sentiment", response_model=news_schemas.SentimentSummaryResponse)
def get_sentiment_summary(
    symbol: str,
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """
    Get sentiment summary for a symbol

    Args:
        symbol: Stock symbol
        days: Number of days to analyze
        db: Database session

    Returns:
        Sentiment summary with statistics
    """
    try:
        summary = NewsService.get_sentiment_summary(db, symbol, days)

        # Get historical data
        from_date = summary['period_start']
        to_date = summary['period_end']

        history = NewsService.get_sentiment_history(
            db, symbol, from_date, to_date
        )

        summary['history'] = history

        return summary

    except Exception as e:
        logger.error(f"Error getting sentiment summary for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/top-news")
def get_top_news(
    symbol: str,
    sentiment_type: str = Query("positive", pattern="^(positive|negative)$"),
    limit: int = Query(10, ge=1, le=50),
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """
    Get top news articles by sentiment

    Args:
        symbol: Stock symbol
        sentiment_type: Type of sentiment to filter
        limit: Number of articles
        days: Days to look back
        db: Database session

    Returns:
        List of top articles
    """
    try:
        articles = NewsService.get_top_news_by_sentiment(
            db, symbol, sentiment_type, limit, days
        )

        return articles

    except Exception as e:
        logger.error(f"Error getting top news for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fetch", response_model=news_schemas.NewsFetchResponse)
def fetch_news(
    request: news_schemas.NewsFetchRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Fetch news from external sources

    Args:
        request: News fetch request
        background_tasks: Background task handler
        db: Database session

    Returns:
        Fetch result
    """
    try:
        fetcher = NewsFetcher(db)

        # For now, use mock news for testing
        # In production, would use NewsAPI or other sources
        if request.symbols:
            articles = fetcher.fetch_mock_news(request.symbols, count=20)
        else:
            articles = fetcher.fetch_mock_news(['AAPL', 'MSFT', 'GOOGL'], count=20)

        # Save articles with sentiment analysis
        saved = fetcher.save_articles_with_sentiment(
            articles,
            analyze_sentiment=request.analyze_sentiment
        )

        # Update sentiment history in background
        if request.symbols:
            for symbol in request.symbols:
                background_tasks.add_task(
                    fetcher.update_sentiment_history,
                    symbol.upper()
                )

        return {
            'articles_fetched': len(articles),
            'articles_saved': saved,
            'sources_used': ['mock'],  # Would include actual sources
            'message': f'Successfully fetched and saved {saved} articles'
        }

    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", response_model=news_schemas.SentimentAnalysisResponse)
def analyze_sentiment(request: news_schemas.SentimentAnalysisRequest):
    """
    Analyze sentiment of arbitrary text

    Args:
        request: Text to analyze

    Returns:
        Sentiment analysis result
    """
    try:
        analyzer = get_sentiment_analyzer()
        result = analyzer.analyze_text(request.text)

        return {
            **result,
            'timestamp': datetime.now()
        }

    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
def get_news_stats(
    symbol: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get news statistics

    Args:
        symbol: Optional symbol filter
        db: Database session

    Returns:
        News statistics
    """
    try:
        stats = NewsService.get_news_stats(db, symbol)
        return stats

    except Exception as e:
        logger.error(f"Error getting news stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
