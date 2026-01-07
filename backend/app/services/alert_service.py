"""Alert service"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime
import yfinance as yf
import json

from app.models.alert import Alert, AlertHistory, AlertCondition, AlertStatus
from app.schemas.alert import AlertCreate, AlertUpdate
from app.services.news_alert_service import NewsAlertService


class AlertService:
    """Service for managing alerts"""

    @staticmethod
    def create_alert(db: Session, alert: AlertCreate) -> Alert:
        """Create a new alert"""
        db_alert = Alert(
            symbol=alert.symbol.upper(),
            condition=alert.condition,
            threshold_value=alert.threshold_value,
            message=alert.message,
            status=AlertStatus.ACTIVE
        )
        db.add(db_alert)
        db.commit()
        db.refresh(db_alert)
        return db_alert

    @staticmethod
    def get_alert(db: Session, alert_id: int) -> Optional[Alert]:
        """Get alert by ID"""
        return db.query(Alert).filter(Alert.id == alert_id).first()

    @staticmethod
    def get_alerts(
        db: Session,
        symbol: Optional[str] = None,
        status: Optional[AlertStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Alert]:
        """Get alerts with optional filtering"""
        query = db.query(Alert)

        if symbol:
            query = query.filter(Alert.symbol == symbol.upper())

        if status:
            query = query.filter(Alert.status == status)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_active_alerts(db: Session) -> List[Alert]:
        """Get all active alerts"""
        return db.query(Alert).filter(Alert.status == AlertStatus.ACTIVE).all()

    @staticmethod
    def update_alert(db: Session, alert_id: int, alert_update: AlertUpdate) -> Optional[Alert]:
        """Update an alert"""
        db_alert = AlertService.get_alert(db, alert_id)
        if not db_alert:
            return None

        update_data = alert_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_alert, field, value)

        db.commit()
        db.refresh(db_alert)
        return db_alert

    @staticmethod
    def delete_alert(db: Session, alert_id: int) -> bool:
        """Delete an alert"""
        db_alert = AlertService.get_alert(db, alert_id)
        if not db_alert:
            return False

        db.delete(db_alert)
        db.commit()
        return True

    @staticmethod
    def check_alert_condition(alert: Alert, current_price: float) -> bool:
        """
        Check if an alert condition is met

        Args:
            alert: The alert to check
            current_price: Current stock price

        Returns:
            True if alert should trigger, False otherwise
        """
        if alert.condition == AlertCondition.PRICE_ABOVE:
            return current_price > alert.threshold_value

        elif alert.condition == AlertCondition.PRICE_BELOW:
            return current_price < alert.threshold_value

        elif alert.condition == AlertCondition.PRICE_CHANGE_PERCENT:
            # For percent change, we need historical data
            # threshold_value represents the percentage change (e.g., 5 for 5%)
            # This is a simplified version - in production you'd compare to previous close
            ticker = yf.Ticker(alert.symbol)
            hist = ticker.history(period="2d")
            if len(hist) < 2:
                return False

            prev_close = hist['Close'].iloc[-2]
            pct_change = ((current_price - prev_close) / prev_close) * 100
            return abs(pct_change) >= alert.threshold_value

        elif alert.condition == AlertCondition.VOLUME_ABOVE:
            # Get current volume
            ticker = yf.Ticker(alert.symbol)
            hist = ticker.history(period="1d")
            if hist.empty:
                return False

            current_volume = hist['Volume'].iloc[-1]
            return current_volume > alert.threshold_value

        return False

    @staticmethod
    def trigger_alert(
        db: Session,
        alert: Alert,
        current_price: Optional[float] = None,
        sentiment: Optional[float] = None,
        article_count: Optional[int] = None,
        details: Optional[dict] = None
    ) -> AlertHistory:
        """
        Trigger an alert and create history record

        Args:
            db: Database session
            alert: Alert to trigger
            current_price: Price that triggered the alert (for price alerts)
            sentiment: Sentiment that triggered the alert (for news alerts)
            article_count: Article count (for news alerts)
            details: Additional trigger details

        Returns:
            AlertHistory record
        """
        # Update alert status
        alert.status = AlertStatus.TRIGGERED
        alert.triggered_at = datetime.now()

        # Create history record
        history = AlertHistory(
            alert_id=alert.id,
            price_at_trigger=current_price,
            sentiment_at_trigger=sentiment,
            articles_count=article_count,
            trigger_details=json.dumps(details) if details else None,
            notification_sent=False
        )

        db.add(history)
        db.commit()
        db.refresh(history)

        return history

    @staticmethod
    def mark_notification_sent(db: Session, history_id: int):
        """Mark notification as sent in history"""
        history = db.query(AlertHistory).filter(AlertHistory.id == history_id).first()
        if history:
            history.notification_sent = True
            db.commit()

    @staticmethod
    def get_alert_history(db: Session, alert_id: int) -> List[AlertHistory]:
        """Get history for a specific alert"""
        return db.query(AlertHistory).filter(
            AlertHistory.alert_id == alert_id
        ).order_by(AlertHistory.triggered_at.desc()).all()

    @staticmethod
    def check_all_active_alerts(db: Session, include_news: bool = True) -> List[dict]:
        """
        Check all active alerts and trigger any that meet conditions

        Args:
            db: Database session
            include_news: Whether to check news-based alerts

        Returns:
            List of triggered alerts with details
        """
        triggered = []

        # Check price-based alerts
        price_conditions = [
            AlertCondition.PRICE_ABOVE,
            AlertCondition.PRICE_BELOW,
            AlertCondition.PRICE_CHANGE_PERCENT,
            AlertCondition.VOLUME_ABOVE
        ]

        price_alerts = db.query(Alert).filter(
            Alert.status == AlertStatus.ACTIVE,
            Alert.condition.in_(price_conditions)
        ).all()

        for alert in price_alerts:
            try:
                # Get current price
                ticker = yf.Ticker(alert.symbol)
                hist = ticker.history(period="1d")

                if hist.empty:
                    continue

                current_price = hist['Close'].iloc[-1]

                # Check if condition is met
                if AlertService.check_alert_condition(alert, current_price):
                    history = AlertService.trigger_alert(db, alert, current_price=current_price)

                    triggered.append({
                        "alert_id": alert.id,
                        "symbol": alert.symbol,
                        "condition": alert.condition.value,
                        "threshold": alert.threshold_value,
                        "current_price": current_price,
                        "message": alert.message,
                        "history_id": history.id,
                        "type": "price"
                    })

            except Exception as e:
                print(f"Error checking price alert {alert.id}: {e}")
                continue

        # Check news-based alerts
        if include_news:
            try:
                news_triggered = NewsAlertService.check_all_news_alerts(db)
                for alert_data in news_triggered:
                    alert_data['type'] = 'news'
                    triggered.append(alert_data)
            except Exception as e:
                print(f"Error checking news alerts: {e}")

        return triggered
