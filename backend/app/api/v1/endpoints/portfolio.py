"""Portfolio management endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.db import get_db
from app.services.portfolio_service import PortfolioService
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioUpdate,
    PortfolioResponse,
    HoldingCreate,
    HoldingUpdate,
    HoldingResponse,
    TransactionCreate,
    TransactionResponse,
    PortfolioPerformance
)

router = APIRouter()


# Portfolio endpoints
@router.post("/", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    portfolio: PortfolioCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new portfolio

    **Parameters:**
    - **name**: Portfolio name
    - **description**: Optional description
    - **is_tfsa**: Whether this is a TFSA account (default: true)

    **Example:**
    ```json
    {
        "name": "My TFSA Portfolio",
        "description": "Long-term growth stocks",
        "is_tfsa": true
    }
    ```
    """
    return PortfolioService.create_portfolio(db, portfolio)


@router.get("/", response_model=List[PortfolioResponse])
async def get_portfolios(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all portfolios

    **Parameters:**
    - **skip**: Number of portfolios to skip (pagination)
    - **limit**: Maximum number of portfolios to return
    """
    return PortfolioService.get_portfolios(db, skip=skip, limit=limit)


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific portfolio by ID
    """
    portfolio = PortfolioService.get_portfolio(db, portfolio_id)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio {portfolio_id} not found"
        )
    return portfolio


@router.put("/{portfolio_id}", response_model=PortfolioResponse)
async def update_portfolio(
    portfolio_id: int,
    portfolio: PortfolioUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a portfolio

    **Example:**
    ```json
    {
        "name": "Updated Portfolio Name",
        "description": "New description"
    }
    ```
    """
    updated = PortfolioService.update_portfolio(db, portfolio_id, portfolio)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio {portfolio_id} not found"
        )
    return updated


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a portfolio

    **Warning:** This will delete all holdings and transactions associated with this portfolio.
    """
    deleted = PortfolioService.delete_portfolio(db, portfolio_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio {portfolio_id} not found"
        )


@router.get("/{portfolio_id}/performance", response_model=PortfolioPerformance)
async def get_portfolio_performance(
    portfolio_id: int,
    db: Session = Depends(get_db)
):
    """
    Get portfolio performance with current values

    Returns:
    - Total portfolio value at current prices
    - Total cost basis
    - Gain/loss (absolute and percentage)
    - Individual holdings with current prices
    """
    return PortfolioService.get_portfolio_performance(db, portfolio_id)


# Holdings endpoints
@router.get("/{portfolio_id}/holdings", response_model=List[HoldingResponse])
async def get_holdings(
    portfolio_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all holdings in a portfolio
    """
    # Verify portfolio exists
    portfolio = PortfolioService.get_portfolio(db, portfolio_id)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio {portfolio_id} not found"
        )

    holdings = PortfolioService.get_holdings(db, portfolio_id)

    # Enrich with current prices
    enriched_holdings = []
    for holding in holdings:
        import yfinance as yf
        try:
            ticker = yf.Ticker(holding.symbol)
            hist = ticker.history(period="1d")
            if not hist.empty:
                current_price = float(hist['Close'].iloc[-1])
                current_value = holding.shares * current_price
                total_cost = holding.shares * holding.average_cost
                gain_loss = current_value - total_cost
                gain_loss_percent = (gain_loss / total_cost * 100) if total_cost > 0 else 0.0
            else:
                current_price = None
                current_value = None
                total_cost = None
                gain_loss = None
                gain_loss_percent = None
        except:
            current_price = None
            current_value = None
            total_cost = None
            gain_loss = None
            gain_loss_percent = None

        enriched_holdings.append(HoldingResponse(
            id=holding.id,
            portfolio_id=holding.portfolio_id,
            symbol=holding.symbol,
            shares=holding.shares,
            average_cost=holding.average_cost,
            current_price=current_price,
            current_value=current_value,
            total_cost=total_cost,
            gain_loss=gain_loss,
            gain_loss_percent=gain_loss_percent,
            created_at=holding.created_at,
            updated_at=holding.updated_at
        ))

    return enriched_holdings


@router.post("/{portfolio_id}/holdings", response_model=HoldingResponse, status_code=status.HTTP_201_CREATED)
async def create_holding(
    portfolio_id: int,
    holding: HoldingCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new holding in a portfolio

    **Note:** It's recommended to use the transaction endpoint instead,
    which will automatically create/update holdings.

    **Example:**
    ```json
    {
        "portfolio_id": 1,
        "symbol": "AAPL",
        "shares": 10,
        "average_cost": 150.50
    }
    ```
    """
    # Override portfolio_id from path
    holding.portfolio_id = portfolio_id
    return PortfolioService.create_holding(db, holding)


@router.put("/holdings/{holding_id}", response_model=HoldingResponse)
async def update_holding(
    holding_id: int,
    holding: HoldingUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a holding

    **Example:**
    ```json
    {
        "shares": 15,
        "average_cost": 145.00
    }
    ```
    """
    updated = PortfolioService.update_holding(db, holding_id, holding)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Holding {holding_id} not found"
        )
    return updated


@router.delete("/holdings/{holding_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_holding(
    holding_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a holding
    """
    deleted = PortfolioService.delete_holding(db, holding_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Holding {holding_id} not found"
        )


# Transaction endpoints
@router.post("/{portfolio_id}/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    portfolio_id: int,
    transaction: TransactionCreate,
    db: Session = Depends(get_db)
):
    """
    Create a transaction (buy/sell)

    This will automatically update the portfolio holdings.
    - **BUY**: Creates or updates holding, adjusts average cost
    - **SELL**: Reduces shares, removes holding if shares = 0

    **Example (Buy):**
    ```json
    {
        "portfolio_id": 1,
        "symbol": "AAPL",
        "transaction_type": "buy",
        "shares": 10,
        "price_per_share": 150.50,
        "fees": 1.99,
        "transaction_date": "2024-01-15T10:30:00Z",
        "notes": "Initial purchase"
    }
    ```

    **Example (Sell):**
    ```json
    {
        "portfolio_id": 1,
        "symbol": "AAPL",
        "transaction_type": "sell",
        "shares": 5,
        "price_per_share": 160.00,
        "fees": 1.99,
        "transaction_date": "2024-02-15T14:30:00Z",
        "notes": "Partial sell"
    }
    ```
    """
    # Override portfolio_id from path
    transaction.portfolio_id = portfolio_id
    return PortfolioService.create_transaction(db, transaction)


@router.get("/{portfolio_id}/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    portfolio_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get transaction history for a portfolio

    Sorted by transaction date (newest first)
    """
    # Verify portfolio exists
    portfolio = PortfolioService.get_portfolio(db, portfolio_id)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio {portfolio_id} not found"
        )

    return PortfolioService.get_transactions(db, portfolio_id, skip=skip, limit=limit)
