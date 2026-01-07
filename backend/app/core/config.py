"""Application configuration"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # App
    APP_NAME: str = "Stonk Bro"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "info"

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://redis:6379"

    # API Keys
    ALPHA_VANTAGE_KEY: Optional[str] = None
    NEWS_API_KEY: Optional[str] = None

    # TFSA Settings
    TFSA_BIRTH_YEAR: int = 1990
    TFSA_INITIAL_CONTRIBUTION_ROOM: int = 95000

    # Email/SMTP (for alerts)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    ALERT_EMAIL: Optional[str] = None

    # Rate Limiting
    API_RATE_LIMIT: int = 100  # requests per minute

    # Caching
    CACHE_TTL_HISTORICAL: int = 86400  # 24 hours for historical data
    CACHE_TTL_REALTIME: int = 300  # 5 minutes for real-time quotes
    CACHE_TTL_FUNDAMENTAL: int = 604800  # 1 week for fundamental data

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
