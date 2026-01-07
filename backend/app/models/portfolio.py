"""Portfolio models"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.db import Base
import enum


class TransactionType(str, enum.Enum):
    """Transaction types"""
    BUY = "buy"
    SELL = "sell"
    DIVIDEND = "dividend"
    SPLIT = "split"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"


class Portfolio(Base):
    """User portfolio"""
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, default="My Portfolio")
    description = Column(String(500), nullable=True)
    is_tfsa = Column(Boolean, default=True)  # True for TFSA, False for non-registered
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    holdings = relationship("PortfolioHolding", back_populates="portfolio", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="portfolio", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Portfolio {self.id}: {self.name}>"


class PortfolioHolding(Base):
    """Current portfolio holdings"""
    __tablename__ = "portfolio_holdings"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    symbol = Column(String(10), nullable=False, index=True)
    shares = Column(Float, nullable=False)
    average_cost = Column(Float, nullable=False)  # Average cost per share
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    portfolio = relationship("Portfolio", back_populates="holdings")

    def __repr__(self):
        return f"<Holding {self.symbol}: {self.shares} shares>"


class Transaction(Base):
    """Transaction history"""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    symbol = Column(String(10), nullable=False, index=True)
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    shares = Column(Float, nullable=False)
    price_per_share = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    fees = Column(Float, default=0.0)
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    portfolio = relationship("Portfolio", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction {self.transaction_type}: {self.symbol} x {self.shares}>"
