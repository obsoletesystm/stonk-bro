"""Alert endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.db import get_db
from app.services.alert_service import AlertService
from app.services.news_alert_service import NewsAlertService
from app.schemas.alert import (
    AlertCreate,
    AlertUpdate,
    AlertResponse,
    AlertHistoryResponse,
    AlertWithHistory
)
from app.models.alert import AlertStatus

router = APIRouter()


@router.post("/", response_model=AlertResponse, status_code=201)
def create_alert(
    alert: AlertCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new price alert

    - **symbol**: Stock symbol to monitor
    - **condition**: Type of condition (price_above, price_below, price_change_percent, volume_above)
    - **threshold_value**: Threshold value for the condition
    - **message**: Optional custom message for the alert
    """
    return AlertService.create_alert(db, alert)


@router.get("/", response_model=List[AlertResponse])
def list_alerts(
    symbol: Optional[str] = Query(None, description="Filter by stock symbol"),
    status: Optional[AlertStatus] = Query(None, description="Filter by alert status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    List alerts with optional filtering

    - **symbol**: Filter by stock symbol (optional)
    - **status**: Filter by alert status (optional)
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    return AlertService.get_alerts(db, symbol=symbol, status=status, skip=skip, limit=limit)


@router.get("/active", response_model=List[AlertResponse])
def list_active_alerts(db: Session = Depends(get_db)):
    """Get all active alerts"""
    return AlertService.get_active_alerts(db)


@router.get("/{alert_id}", response_model=AlertWithHistory)
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific alert with its trigger history

    - **alert_id**: ID of the alert to retrieve
    """
    alert = AlertService.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.put("/{alert_id}", response_model=AlertResponse)
def update_alert(
    alert_id: int,
    alert_update: AlertUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an alert

    - **alert_id**: ID of the alert to update
    - **condition**: New condition type (optional)
    - **threshold_value**: New threshold value (optional)
    - **status**: New status (optional)
    - **message**: New custom message (optional)
    """
    alert = AlertService.update_alert(db, alert_id, alert_update)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.delete("/{alert_id}", status_code=204)
def delete_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete an alert

    - **alert_id**: ID of the alert to delete
    """
    success = AlertService.delete_alert(db, alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")


@router.get("/{alert_id}/history", response_model=List[AlertHistoryResponse])
def get_alert_history(
    alert_id: int,
    db: Session = Depends(get_db)
):
    """
    Get trigger history for a specific alert

    - **alert_id**: ID of the alert
    """
    alert = AlertService.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return AlertService.get_alert_history(db, alert_id)


@router.post("/check", response_model=dict)
def check_alerts_now(
    include_news: bool = Query(True, description="Include news-based alerts"),
    db: Session = Depends(get_db)
):
    """
    Manually trigger alert checking (for testing)

    Checks all active alerts and triggers any that meet their conditions.
    Returns list of triggered alerts.

    - **include_news**: Whether to check news-based alerts (default: True)
    """
    triggered = AlertService.check_all_active_alerts(db, include_news=include_news)

    return {
        "checked_at": "now",
        "triggered_count": len(triggered),
        "triggered_alerts": triggered
    }


@router.post("/news/check/{symbol}", response_model=dict)
def check_news_alerts_for_symbol(
    symbol: str,
    db: Session = Depends(get_db)
):
    """
    Check news-based alerts for a specific symbol

    Checks all active news alerts for the given symbol and triggers
    any that meet their conditions based on recent sentiment data.

    - **symbol**: Stock symbol to check alerts for
    """
    triggered = NewsAlertService.check_news_alerts_for_symbol(db, symbol)

    return {
        "symbol": symbol.upper(),
        "checked_at": "now",
        "triggered_count": len(triggered),
        "triggered_alerts": triggered
    }


@router.get("/news/stats", response_model=dict)
def get_news_alert_stats(
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    db: Session = Depends(get_db)
):
    """
    Get statistics about news-based alerts

    Returns counts and breakdowns of news alerts by type, status, etc.

    - **symbol**: Optional symbol filter
    """
    stats = NewsAlertService.get_news_alert_stats(db, symbol)
    return stats
