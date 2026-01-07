"""API v1 router aggregation"""
from fastapi import APIRouter
from app.api.v1.endpoints import stocks, portfolio, health, alerts, indicators, ml, news

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(stocks.router, prefix="/stocks", tags=["stocks"])
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(indicators.router, prefix="/indicators", tags=["indicators"])
api_router.include_router(ml.router, prefix="/ml", tags=["ml"])
api_router.include_router(news.router, prefix="/news", tags=["news"])
