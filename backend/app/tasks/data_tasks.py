"""Data fetching tasks for Celery"""
import logging
from app.celery_app import celery_app
from app.core.db import SessionLocal
from app.services.data_fetcher import DataFetcher

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def fetch_daily_data_task(self):
    """
    Fetch daily stock data for all portfolio holdings

    This task runs daily after market close to update
    stock prices, volumes, and technical indicators.
    """
    db = SessionLocal()
    try:
        logger.info("Starting daily data fetch task")

        fetcher = DataFetcher(db)

        # Get all unique symbols from portfolios
        symbols = fetcher.get_symbols_from_portfolios()

        if not symbols:
            logger.warning("No symbols found in portfolios")
            return {
                'status': 'skipped',
                'reason': 'No symbols in portfolios',
                'symbols_processed': 0
            }

        logger.info(f"Fetching data for {len(symbols)} symbols: {symbols}")

        results = {
            'symbols_processed': 0,
            'symbols_failed': 0,
            'failed_symbols': []
        }

        for symbol in symbols:
            try:
                # Fetch and store latest data
                fetcher.fetch_and_store_stock_data(symbol, period='1d')
                results['symbols_processed'] += 1
                logger.info(f"Successfully fetched data for {symbol}")

            except Exception as e:
                results['symbols_failed'] += 1
                results['failed_symbols'].append(symbol)
                logger.error(f"Error fetching data for {symbol}: {e}")

        logger.info(f"Daily data fetch complete. Processed: {results['symbols_processed']}, "
                   f"Failed: {results['symbols_failed']}")

        return results

    except Exception as e:
        logger.error(f"Error in daily data fetch task: {e}")
        raise
    finally:
        db.close()


@celery_app.task(bind=True)
def fetch_stock_data_task(self, symbol: str, period: str = '1mo'):
    """
    Fetch historical data for a specific symbol

    Args:
        symbol: Stock symbol to fetch
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, etc.)

    Returns:
        Dict with fetch status
    """
    db = SessionLocal()
    try:
        logger.info(f"Fetching {period} data for {symbol}")

        fetcher = DataFetcher(db)
        fetcher.fetch_and_store_stock_data(symbol, period=period)

        logger.info(f"Successfully fetched {period} data for {symbol}")

        return {
            'status': 'success',
            'symbol': symbol,
            'period': period
        }

    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {e}")
        return {
            'status': 'failed',
            'symbol': symbol,
            'period': period,
            'error': str(e)
        }
    finally:
        db.close()


@celery_app.task(bind=True)
def backfill_historical_data_task(self, symbol: str, start_date: str, end_date: str = None):
    """
    Backfill historical data for a symbol

    Args:
        symbol: Stock symbol
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD), defaults to today

    Returns:
        Dict with backfill status
    """
    db = SessionLocal()
    try:
        logger.info(f"Backfilling historical data for {symbol} from {start_date}")

        fetcher = DataFetcher(db)
        rows_saved = fetcher.backfill_historical_data(symbol, start_date, end_date)

        logger.info(f"Successfully backfilled {rows_saved} rows for {symbol}")

        return {
            'status': 'success',
            'symbol': symbol,
            'rows_saved': rows_saved,
            'start_date': start_date,
            'end_date': end_date
        }

    except Exception as e:
        logger.error(f"Error backfilling data for {symbol}: {e}")
        return {
            'status': 'failed',
            'symbol': symbol,
            'error': str(e)
        }
    finally:
        db.close()
