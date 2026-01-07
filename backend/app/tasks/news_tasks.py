"""News and sentiment tasks for Celery"""
import logging
from typing import List, Optional
from app.celery_app import celery_app
from app.core.db import SessionLocal
from app.services.news_fetcher import NewsFetcher
from app.services.data_fetcher import DataFetcher

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def fetch_news_task(self, symbols: Optional[List[str]] = None, days: int = 1):
    """
    Fetch news articles and analyze sentiment

    Args:
        symbols: List of symbols to fetch news for (defaults to portfolio holdings)
        days: Number of days of news to fetch

    Returns:
        Dict with fetch results
    """
    db = SessionLocal()
    try:
        logger.info(f"Starting news fetch task for {days} days")

        fetcher = NewsFetcher(db)

        # Get symbols from portfolios if not provided
        if not symbols:
            data_fetcher = DataFetcher(db)
            symbols = data_fetcher.get_symbols_from_portfolios()

        if not symbols:
            logger.warning("No symbols found")
            return {
                'status': 'skipped',
                'reason': 'No symbols to fetch',
                'articles_fetched': 0
            }

        logger.info(f"Fetching news for {len(symbols)} symbols: {symbols}")

        # Use mock news for now (replace with NewsAPI when configured)
        articles = fetcher.fetch_mock_news(symbols, count=min(len(symbols) * 10, 100))

        # Save articles with sentiment analysis
        saved = fetcher.save_articles_with_sentiment(
            articles,
            analyze_sentiment=True
        )

        # Update sentiment history for each symbol
        for symbol in symbols:
            try:
                fetcher.update_sentiment_history(symbol)
            except Exception as e:
                logger.error(f"Error updating sentiment history for {symbol}: {e}")

        logger.info(f"News fetch complete. Fetched: {len(articles)}, Saved: {saved}")

        return {
            'status': 'success',
            'articles_fetched': len(articles),
            'articles_saved': saved,
            'symbols_processed': len(symbols)
        }

    except Exception as e:
        logger.error(f"Error in news fetch task: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }
    finally:
        db.close()


@celery_app.task(bind=True)
def fetch_news_for_symbol_task(self, symbol: str, days: int = 7):
    """
    Fetch news for a specific symbol

    Args:
        symbol: Stock symbol
        days: Number of days of news to fetch

    Returns:
        Dict with fetch results
    """
    db = SessionLocal()
    try:
        logger.info(f"Fetching {days} days of news for {symbol}")

        fetcher = NewsFetcher(db)

        # Use mock news for now
        articles = fetcher.fetch_mock_news([symbol], count=20)

        # Save articles with sentiment analysis
        saved = fetcher.save_articles_with_sentiment(
            articles,
            analyze_sentiment=True
        )

        # Update sentiment history
        fetcher.update_sentiment_history(symbol)

        logger.info(f"Fetched {len(articles)} articles for {symbol}, saved {saved}")

        return {
            'status': 'success',
            'symbol': symbol,
            'articles_fetched': len(articles),
            'articles_saved': saved
        }

    except Exception as e:
        logger.error(f"Error fetching news for {symbol}: {e}")
        return {
            'status': 'error',
            'symbol': symbol,
            'error': str(e)
        }
    finally:
        db.close()


@celery_app.task(bind=True)
def update_sentiment_history_task(self):
    """
    Update sentiment history for all portfolio holdings

    This task aggregates sentiment data daily for historical tracking.
    """
    db = SessionLocal()
    try:
        logger.info("Starting sentiment history update task")

        fetcher = NewsFetcher(db)
        data_fetcher = DataFetcher(db)

        # Get all symbols from portfolios
        symbols = data_fetcher.get_symbols_from_portfolios()

        if not symbols:
            logger.warning("No symbols found in portfolios")
            return {
                'status': 'skipped',
                'reason': 'No symbols in portfolios',
                'symbols_processed': 0
            }

        logger.info(f"Updating sentiment history for {len(symbols)} symbols")

        results = {
            'symbols_processed': 0,
            'symbols_failed': 0,
            'failed_symbols': []
        }

        for symbol in symbols:
            try:
                fetcher.update_sentiment_history(symbol)
                results['symbols_processed'] += 1
                logger.info(f"Updated sentiment history for {symbol}")

            except Exception as e:
                results['symbols_failed'] += 1
                results['failed_symbols'].append(symbol)
                logger.error(f"Error updating sentiment history for {symbol}: {e}")

        logger.info(f"Sentiment history update complete. Processed: {results['symbols_processed']}, "
                   f"Failed: {results['symbols_failed']}")

        return results

    except Exception as e:
        logger.error(f"Error in sentiment history update task: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }
    finally:
        db.close()


@celery_app.task(bind=True)
def analyze_sentiment_batch_task(self, article_ids: List[int]):
    """
    Analyze sentiment for a batch of articles

    Args:
        article_ids: List of article IDs to analyze

    Returns:
        Dict with analysis results
    """
    db = SessionLocal()
    try:
        logger.info(f"Analyzing sentiment for {len(article_ids)} articles")

        from app.services.sentiment_service import get_sentiment_analyzer
        from app.models.news import NewsArticle

        analyzer = get_sentiment_analyzer()
        analyzed_count = 0

        for article_id in article_ids:
            try:
                article = db.query(NewsArticle).filter(NewsArticle.id == article_id).first()

                if not article:
                    continue

                # Analyze sentiment
                sentiment = analyzer.analyze_article(
                    title=article.title,
                    description=article.description,
                    content=article.content
                )

                # Update article
                article.sentiment_score = sentiment['normalized_score']
                article.sentiment_label = sentiment['label']
                article.sentiment_confidence = sentiment['confidence']

                analyzed_count += 1

            except Exception as e:
                logger.error(f"Error analyzing article {article_id}: {e}")

        db.commit()

        logger.info(f"Analyzed sentiment for {analyzed_count} articles")

        return {
            'status': 'success',
            'articles_analyzed': analyzed_count
        }

    except Exception as e:
        logger.error(f"Error in batch sentiment analysis: {e}")
        db.rollback()
        return {
            'status': 'error',
            'error': str(e)
        }
    finally:
        db.close()
