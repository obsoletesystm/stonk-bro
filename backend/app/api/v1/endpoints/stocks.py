"""Stock data endpoints"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
import yfinance as yf
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/quote/{symbol}")
async def get_stock_quote(symbol: str):
    """
    Get current quote for a stock symbol

    Example: /api/v1/stocks/quote/AAPL
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        info = ticker.info

        # Get latest price data
        hist = ticker.history(period="1d")
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")

        latest = hist.iloc[-1]

        return {
            "symbol": symbol.upper(),
            "name": info.get("longName", symbol),
            "price": float(latest["Close"]),
            "open": float(latest["Open"]),
            "high": float(latest["High"]),
            "low": float(latest["Low"]),
            "volume": int(latest["Volume"]),
            "timestamp": latest.name.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching quote: {str(e)}")


@router.get("/history/{symbol}")
async def get_stock_history(
    symbol: str,
    period: str = "1mo",
    interval: str = "1d"
):
    """
    Get historical data for a stock

    Parameters:
    - period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    - interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo

    Example: /api/v1/stocks/history/AAPL?period=1y&interval=1d
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        hist = ticker.history(period=period, interval=interval)

        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No historical data found for {symbol}")

        # Convert to list of dicts
        data = []
        for idx, row in hist.iterrows():
            data.append({
                "timestamp": idx.isoformat(),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(row["Volume"])
            })

        return {
            "symbol": symbol.upper(),
            "period": period,
            "interval": interval,
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")


@router.get("/search/{query}")
async def search_stocks(query: str):
    """
    Search for stocks by name or symbol

    Note: This is a basic implementation using yfinance.
    For production, consider using a dedicated search API.

    Example: /api/v1/stocks/search/apple
    """
    try:
        # Simple implementation: try as ticker symbol first
        ticker = yf.Ticker(query.upper())
        info = ticker.info

        if "symbol" in info:
            return {
                "results": [{
                    "symbol": info.get("symbol", query.upper()),
                    "name": info.get("longName", "Unknown"),
                    "exchange": info.get("exchange", "Unknown"),
                    "type": info.get("quoteType", "Unknown")
                }]
            }

        return {"results": []}
    except Exception as e:
        return {"results": [], "error": str(e)}
