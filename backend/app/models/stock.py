"""Stock data models"""
from sqlalchemy import Column, String, Float, BigInteger, DateTime, Index
from sqlalchemy.sql import func
from app.core.db import Base


class StockQuote(Base):
    """
    Time-series stock quote data
    Converted to TimescaleDB hypertable via migration
    """
    __tablename__ = "stock_quotes"

    symbol = Column(String(10), primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), primary_key=True, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(BigInteger, nullable=False)
    adjusted_close = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_stock_quotes_symbol_time', 'symbol', 'timestamp'),
    )

    def __repr__(self):
        return f"<StockQuote {self.symbol} {self.timestamp}>"
