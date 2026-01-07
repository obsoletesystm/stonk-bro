"""Data fetching service with rate limiting and caching"""
import yfinance as yf
import requests
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import redis
import json
import time
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.stock import StockQuote


class DataFetcher:
    """Service for fetching stock data from various sources"""

    def __init__(self, db: Session, cache_client: Optional[redis.Redis] = None):
        self.db = db
        self.cache = cache_client or redis.from_url(settings.REDIS_URL)
        self.alpha_vantage_key = settings.ALPHA_VANTAGE_KEY
        self.last_request_time = {}  # Track last request time per source

    def _rate_limit(self, source: str, min_interval: float = 12.0):
        """
        Rate limiting for API calls

        Alpha Vantage: 5 calls/minute = 12 seconds between calls
        yfinance: No official limit, but be respectful (1 second)
        """
        if source in self.last_request_time:
            elapsed = time.time() - self.last_request_time[source]
            if elapsed < min_interval:
                sleep_time = min_interval - elapsed
                print(f"Rate limiting {source}: sleeping {sleep_time:.2f}s")
                time.sleep(sleep_time)

        self.last_request_time[source] = time.time()

    def _get_cache_key(self, symbol: str, data_type: str) -> str:
        """Generate cache key"""
        return f"stock:{symbol}:{data_type}"

    def _get_cached(self, key: str) -> Optional[Dict]:
        """Get data from cache"""
        try:
            data = self.cache.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            print(f"Cache error: {e}")
        return None

    def _set_cached(self, key: str, data: Dict, ttl: int):
        """Set data in cache"""
        try:
            self.cache.setex(key, ttl, json.dumps(data))
        except Exception as e:
            print(f"Cache error: {e}")

    def fetch_historical_yfinance(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d"
    ) -> List[Dict]:
        """
        Fetch historical data from yfinance (primary source)

        Args:
            symbol: Stock symbol
            period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
            interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo

        Returns:
            List of price data dictionaries
        """
        # Check cache first
        cache_key = self._get_cache_key(symbol, f"history_{period}_{interval}")
        cached = self._get_cached(cache_key)
        if cached:
            print(f"Cache hit for {symbol} {period}")
            return cached

        print(f"Fetching {symbol} from yfinance (period={period}, interval={interval})")

        # Rate limit (be nice to yfinance)
        self._rate_limit("yfinance", min_interval=1.0)

        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)

            if hist.empty:
                print(f"No data returned for {symbol}")
                return []

            data = []
            for timestamp, row in hist.iterrows():
                data.append({
                    "symbol": symbol.upper(),
                    "timestamp": timestamp.isoformat(),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"]),
                    "adjusted_close": float(row.get("Close", row["Close"]))  # yfinance auto-adjusts
                })

            # Cache the data
            self._set_cached(cache_key, data, settings.CACHE_TTL_HISTORICAL)

            print(f"Fetched {len(data)} records for {symbol}")
            return data

        except Exception as e:
            print(f"Error fetching {symbol} from yfinance: {e}")
            return []

    def fetch_quote_yfinance(self, symbol: str) -> Optional[Dict]:
        """
        Fetch current quote from yfinance

        Returns:
            Quote data dictionary or None
        """
        # Check cache first
        cache_key = self._get_cache_key(symbol, "quote")
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        print(f"Fetching quote for {symbol} from yfinance")

        # Rate limit
        self._rate_limit("yfinance", min_interval=1.0)

        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")

            if hist.empty:
                return None

            latest = hist.iloc[-1]
            quote = {
                "symbol": symbol.upper(),
                "timestamp": latest.name.isoformat(),
                "open": float(latest["Open"]),
                "high": float(latest["High"]),
                "low": float(latest["Low"]),
                "close": float(latest["Close"]),
                "volume": int(latest["Volume"]),
                "adjusted_close": float(latest["Close"])
            }

            # Cache for 5 minutes during market hours
            self._set_cached(cache_key, quote, settings.CACHE_TTL_REALTIME)

            return quote

        except Exception as e:
            print(f"Error fetching quote for {symbol}: {e}")
            return None

    def fetch_historical_alpha_vantage(
        self,
        symbol: str,
        outputsize: str = "compact"
    ) -> List[Dict]:
        """
        Fetch historical data from Alpha Vantage (fallback/supplement)

        Args:
            symbol: Stock symbol
            outputsize: "compact" (100 days) or "full" (20+ years)

        Returns:
            List of price data dictionaries
        """
        if not self.alpha_vantage_key:
            print("Alpha Vantage API key not configured")
            return []

        # Check cache first
        cache_key = self._get_cache_key(symbol, f"av_history_{outputsize}")
        cached = self._get_cached(cache_key)
        if cached:
            print(f"Cache hit for {symbol} (Alpha Vantage)")
            return cached

        print(f"Fetching {symbol} from Alpha Vantage (outputsize={outputsize})")

        # Rate limit (5 calls/minute)
        self._rate_limit("alpha_vantage", min_interval=12.0)

        try:
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "TIME_SERIES_DAILY_ADJUSTED",
                "symbol": symbol,
                "outputsize": outputsize,
                "apikey": self.alpha_vantage_key
            }

            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            result = response.json()

            if "Error Message" in result:
                print(f"Alpha Vantage error: {result['Error Message']}")
                return []

            if "Note" in result:
                print(f"Alpha Vantage rate limit: {result['Note']}")
                return []

            time_series = result.get("Time Series (Daily)", {})

            data = []
            for date_str, values in time_series.items():
                data.append({
                    "symbol": symbol.upper(),
                    "timestamp": f"{date_str}T16:00:00",  # Market close
                    "open": float(values["1. open"]),
                    "high": float(values["2. high"]),
                    "low": float(values["3. low"]),
                    "close": float(values["4. close"]),
                    "volume": int(values["6. volume"]),
                    "adjusted_close": float(values["5. adjusted close"])
                })

            # Cache the data
            self._set_cached(cache_key, data, settings.CACHE_TTL_HISTORICAL)

            print(f"Fetched {len(data)} records for {symbol} from Alpha Vantage")
            return data

        except Exception as e:
            print(f"Error fetching {symbol} from Alpha Vantage: {e}")
            return []

    def save_to_database(self, data: List[Dict]) -> int:
        """
        Save price data to database (upsert)

        Returns:
            Number of records saved
        """
        if not data:
            return 0

        saved_count = 0

        for record in data:
            try:
                # Parse timestamp
                timestamp = datetime.fromisoformat(record["timestamp"].replace("Z", "+00:00"))

                # Check if record exists
                existing = self.db.query(StockQuote).filter(
                    StockQuote.symbol == record["symbol"],
                    StockQuote.timestamp == timestamp
                ).first()

                if existing:
                    # Update existing record
                    existing.open = record["open"]
                    existing.high = record["high"]
                    existing.low = record["low"]
                    existing.close = record["close"]
                    existing.volume = record["volume"]
                    existing.adjusted_close = record.get("adjusted_close")
                else:
                    # Create new record
                    quote = StockQuote(
                        symbol=record["symbol"],
                        timestamp=timestamp,
                        open=record["open"],
                        high=record["high"],
                        low=record["low"],
                        close=record["close"],
                        volume=record["volume"],
                        adjusted_close=record.get("adjusted_close")
                    )
                    self.db.add(quote)

                saved_count += 1

            except Exception as e:
                print(f"Error saving record: {e}")
                continue

        try:
            self.db.commit()
            print(f"Saved {saved_count} records to database")
        except Exception as e:
            print(f"Error committing to database: {e}")
            self.db.rollback()
            return 0

        return saved_count

    def fetch_and_save(
        self,
        symbol: str,
        period: str = "1y",
        source: str = "yfinance"
    ) -> int:
        """
        Fetch data and save to database (convenience method)

        Args:
            symbol: Stock symbol
            period: Period to fetch (yfinance format)
            source: "yfinance" or "alpha_vantage"

        Returns:
            Number of records saved
        """
        if source == "yfinance":
            data = self.fetch_historical_yfinance(symbol, period=period)
        elif source == "alpha_vantage":
            outputsize = "full" if period in ["5y", "10y", "max"] else "compact"
            data = self.fetch_historical_alpha_vantage(symbol, outputsize=outputsize)
        else:
            print(f"Unknown source: {source}")
            return 0

        return self.save_to_database(data)

    def get_symbols_from_portfolios(self) -> List[str]:
        """
        Get all unique symbols from portfolio holdings

        Returns:
            List of stock symbols
        """
        from app.models.portfolio import PortfolioHolding

        holdings = self.db.query(PortfolioHolding.symbol).distinct().all()
        return [h.symbol for h in holdings]
