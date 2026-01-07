"""Portfolio business logic"""
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status
import yfinance as yf

from app.models.portfolio import Portfolio, PortfolioHolding, Transaction, TransactionType
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioUpdate,
    HoldingCreate,
    HoldingUpdate,
    TransactionCreate,
    PortfolioPerformance,
    HoldingResponse
)


class PortfolioService:
    """Service for portfolio operations"""

    @staticmethod
    def create_portfolio(db: Session, portfolio: PortfolioCreate) -> Portfolio:
        """Create a new portfolio"""
        db_portfolio = Portfolio(
            name=portfolio.name,
            description=portfolio.description,
            is_tfsa=portfolio.is_tfsa
        )
        db.add(db_portfolio)
        db.commit()
        db.refresh(db_portfolio)
        return db_portfolio

    @staticmethod
    def get_portfolio(db: Session, portfolio_id: int) -> Optional[Portfolio]:
        """Get portfolio by ID"""
        return db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()

    @staticmethod
    def get_portfolios(db: Session, skip: int = 0, limit: int = 100) -> List[Portfolio]:
        """Get all portfolios"""
        return db.query(Portfolio).offset(skip).limit(limit).all()

    @staticmethod
    def update_portfolio(db: Session, portfolio_id: int, portfolio: PortfolioUpdate) -> Optional[Portfolio]:
        """Update portfolio"""
        db_portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not db_portfolio:
            return None

        update_data = portfolio.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_portfolio, field, value)

        db.commit()
        db.refresh(db_portfolio)
        return db_portfolio

    @staticmethod
    def delete_portfolio(db: Session, portfolio_id: int) -> bool:
        """Delete portfolio"""
        db_portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not db_portfolio:
            return False

        db.delete(db_portfolio)
        db.commit()
        return True

    # Holdings
    @staticmethod
    def get_holdings(db: Session, portfolio_id: int) -> List[PortfolioHolding]:
        """Get all holdings for a portfolio"""
        return db.query(PortfolioHolding).filter(
            PortfolioHolding.portfolio_id == portfolio_id
        ).all()

    @staticmethod
    def get_holding(db: Session, holding_id: int) -> Optional[PortfolioHolding]:
        """Get specific holding"""
        return db.query(PortfolioHolding).filter(PortfolioHolding.id == holding_id).first()

    @staticmethod
    def create_holding(db: Session, holding: HoldingCreate) -> PortfolioHolding:
        """Create a new holding"""
        # Check if portfolio exists
        portfolio = db.query(Portfolio).filter(Portfolio.id == holding.portfolio_id).first()
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Portfolio {holding.portfolio_id} not found"
            )

        # Check if holding already exists
        existing = db.query(PortfolioHolding).filter(
            PortfolioHolding.portfolio_id == holding.portfolio_id,
            PortfolioHolding.symbol == holding.symbol.upper()
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Holding for {holding.symbol} already exists in this portfolio"
            )

        db_holding = PortfolioHolding(
            portfolio_id=holding.portfolio_id,
            symbol=holding.symbol.upper(),
            shares=holding.shares,
            average_cost=holding.average_cost
        )
        db.add(db_holding)
        db.commit()
        db.refresh(db_holding)
        return db_holding

    @staticmethod
    def update_holding(db: Session, holding_id: int, holding: HoldingUpdate) -> Optional[PortfolioHolding]:
        """Update holding"""
        db_holding = db.query(PortfolioHolding).filter(PortfolioHolding.id == holding_id).first()
        if not db_holding:
            return None

        update_data = holding.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_holding, field, value)

        db.commit()
        db.refresh(db_holding)
        return db_holding

    @staticmethod
    def delete_holding(db: Session, holding_id: int) -> bool:
        """Delete holding"""
        db_holding = db.query(PortfolioHolding).filter(PortfolioHolding.id == holding_id).first()
        if not db_holding:
            return False

        db.delete(db_holding)
        db.commit()
        return True

    # Transactions
    @staticmethod
    def create_transaction(db: Session, transaction: TransactionCreate) -> Transaction:
        """Create a transaction and update holdings"""
        # Check if portfolio exists
        portfolio = db.query(Portfolio).filter(Portfolio.id == transaction.portfolio_id).first()
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Portfolio {transaction.portfolio_id} not found"
            )

        # Calculate total amount
        total_amount = (transaction.shares * transaction.price_per_share) + transaction.fees

        # Create transaction record
        db_transaction = Transaction(
            portfolio_id=transaction.portfolio_id,
            symbol=transaction.symbol.upper(),
            transaction_type=transaction.transaction_type,
            shares=transaction.shares,
            price_per_share=transaction.price_per_share,
            total_amount=total_amount,
            fees=transaction.fees,
            transaction_date=transaction.transaction_date,
            notes=transaction.notes
        )
        db.add(db_transaction)

        # Update or create holding
        holding = db.query(PortfolioHolding).filter(
            PortfolioHolding.portfolio_id == transaction.portfolio_id,
            PortfolioHolding.symbol == transaction.symbol.upper()
        ).first()

        if transaction.transaction_type == TransactionType.BUY:
            if holding:
                # Update average cost and shares
                total_cost = (holding.shares * holding.average_cost) + total_amount
                total_shares = holding.shares + transaction.shares
                holding.average_cost = total_cost / total_shares
                holding.shares = total_shares
            else:
                # Create new holding
                holding = PortfolioHolding(
                    portfolio_id=transaction.portfolio_id,
                    symbol=transaction.symbol.upper(),
                    shares=transaction.shares,
                    average_cost=transaction.price_per_share + (transaction.fees / transaction.shares)
                )
                db.add(holding)

        elif transaction.transaction_type == TransactionType.SELL:
            if not holding:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"No holding found for {transaction.symbol}"
                )
            if holding.shares < transaction.shares:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient shares. Have {holding.shares}, trying to sell {transaction.shares}"
                )

            holding.shares -= transaction.shares

            # If no shares left, delete holding
            if holding.shares == 0:
                db.delete(holding)

        db.commit()
        db.refresh(db_transaction)
        return db_transaction

    @staticmethod
    def get_transactions(db: Session, portfolio_id: int, skip: int = 0, limit: int = 100) -> List[Transaction]:
        """Get transactions for a portfolio"""
        return db.query(Transaction).filter(
            Transaction.portfolio_id == portfolio_id
        ).order_by(Transaction.transaction_date.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_portfolio_performance(db: Session, portfolio_id: int) -> PortfolioPerformance:
        """Calculate portfolio performance"""
        portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Portfolio {portfolio_id} not found"
            )

        holdings = db.query(PortfolioHolding).filter(
            PortfolioHolding.portfolio_id == portfolio_id
        ).all()

        total_value = 0.0
        total_cost = 0.0
        holdings_response = []

        for holding in holdings:
            # Get current price
            try:
                ticker = yf.Ticker(holding.symbol)
                hist = ticker.history(period="1d")
                if not hist.empty:
                    current_price = float(hist['Close'].iloc[-1])
                else:
                    current_price = holding.average_cost  # Fallback
            except:
                current_price = holding.average_cost  # Fallback on error

            current_value = holding.shares * current_price
            cost = holding.shares * holding.average_cost
            gain_loss = current_value - cost
            gain_loss_percent = (gain_loss / cost * 100) if cost > 0 else 0.0

            total_value += current_value
            total_cost += cost

            holdings_response.append(HoldingResponse(
                id=holding.id,
                portfolio_id=holding.portfolio_id,
                symbol=holding.symbol,
                shares=holding.shares,
                average_cost=holding.average_cost,
                current_price=current_price,
                current_value=current_value,
                total_cost=cost,
                gain_loss=gain_loss,
                gain_loss_percent=gain_loss_percent,
                created_at=holding.created_at,
                updated_at=holding.updated_at
            ))

        total_gain_loss = total_value - total_cost
        total_gain_loss_percent = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0.0

        return PortfolioPerformance(
            portfolio_id=portfolio.id,
            portfolio_name=portfolio.name,
            total_value=total_value,
            total_cost=total_cost,
            total_gain_loss=total_gain_loss,
            total_gain_loss_percent=total_gain_loss_percent,
            holdings_count=len(holdings),
            holdings=holdings_response
        )
