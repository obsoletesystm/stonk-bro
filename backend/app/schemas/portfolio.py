"""Portfolio Pydantic schemas"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.portfolio import TransactionType


# Portfolio Schemas
class PortfolioBase(BaseModel):
    """Base portfolio schema"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_tfsa: bool = Field(default=True)


class PortfolioCreate(PortfolioBase):
    """Schema for creating a portfolio"""
    pass


class PortfolioUpdate(BaseModel):
    """Schema for updating a portfolio"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_tfsa: Optional[bool] = None


class PortfolioResponse(PortfolioBase):
    """Schema for portfolio response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Holding Schemas
class HoldingBase(BaseModel):
    """Base holding schema"""
    symbol: str = Field(..., min_length=1, max_length=10)
    shares: float = Field(..., gt=0)
    average_cost: float = Field(..., gt=0)


class HoldingCreate(HoldingBase):
    """Schema for creating a holding"""
    portfolio_id: int


class HoldingUpdate(BaseModel):
    """Schema for updating a holding"""
    shares: Optional[float] = Field(None, gt=0)
    average_cost: Optional[float] = Field(None, gt=0)


class HoldingResponse(HoldingBase):
    """Schema for holding response"""
    id: int
    portfolio_id: int
    current_price: Optional[float] = None
    current_value: Optional[float] = None
    total_cost: Optional[float] = None
    gain_loss: Optional[float] = None
    gain_loss_percent: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Transaction Schemas
class TransactionBase(BaseModel):
    """Base transaction schema"""
    symbol: str = Field(..., min_length=1, max_length=10)
    transaction_type: TransactionType
    shares: float = Field(..., gt=0)
    price_per_share: float = Field(..., gt=0)
    fees: float = Field(default=0.0, ge=0)
    transaction_date: datetime
    notes: Optional[str] = Field(None, max_length=500)


class TransactionCreate(TransactionBase):
    """Schema for creating a transaction"""
    portfolio_id: int


class TransactionResponse(TransactionBase):
    """Schema for transaction response"""
    id: int
    portfolio_id: int
    total_amount: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Portfolio Performance Schema
class PortfolioPerformance(BaseModel):
    """Schema for portfolio performance metrics"""
    portfolio_id: int
    portfolio_name: str
    total_value: float
    total_cost: float
    total_gain_loss: float
    total_gain_loss_percent: float
    holdings_count: int
    cash_position: float = 0.0
    holdings: List[HoldingResponse] = []
