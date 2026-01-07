"""Alert-related Celery tasks"""
from celery import Task
from app.celery_app import celery_app
from app.core.db import SessionLocal
from app.services.alert_service import AlertService
from app.services.news_alert_service import NewsAlertService
from app.utils.discord import send_price_alert_discord, send_news_alert_discord


class DatabaseTask(Task):
    """Base task with database session"""
    _db = None

    @property
    def db(self):
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None


@celery_app.task(bind=True, base=DatabaseTask, name="check_alerts")
def check_all_alerts_task(self):
    """
    Check all active alerts (price and news) and trigger notifications

    This task:
    1. Gets all active price and news alerts
    2. Checks each alert's condition
    3. Triggers alerts that meet their conditions
    4. Sends email notifications for triggered alerts
    """
    print("Starting alert check (price + news)...")

    try:
        triggered = AlertService.check_all_active_alerts(self.db, include_news=True)

        print(f"Checked alerts. Triggered: {len(triggered)}")

        # Send notifications for each triggered alert
        for alert_info in triggered:
            send_alert_notification_task.delay(
                alert_id=alert_info["alert_id"],
                symbol=alert_info["symbol"],
                condition=alert_info["condition"],
                threshold=alert_info["threshold"],
                current_price=alert_info.get("current_price"),
                current_sentiment=alert_info.get("current_sentiment"),
                article_count=alert_info.get("article_count"),
                message=alert_info["message"],
                history_id=alert_info["history_id"],
                alert_type=alert_info.get("type", "price")
            )

        return {
            "status": "success",
            "triggered_count": len(triggered),
            "alerts": triggered
        }

    except Exception as e:
        print(f"Error checking alerts: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@celery_app.task(bind=True, base=DatabaseTask, name="check_news_alerts")
def check_news_alerts_task(self):
    """
    Check only news-based alerts

    This task runs more frequently than price alerts
    to catch sentiment changes quickly.
    """
    print("Starting news alert check...")

    try:
        from app.services.news_alert_service import NewsAlertService

        triggered = NewsAlertService.check_all_news_alerts(self.db)

        print(f"Checked news alerts. Triggered: {len(triggered)}")

        # Send notifications for each triggered alert
        for alert_info in triggered:
            send_alert_notification_task.delay(
                alert_id=alert_info["alert_id"],
                symbol=alert_info["symbol"],
                condition=alert_info["condition"],
                threshold=alert_info["threshold"],
                current_price=None,
                current_sentiment=alert_info.get("current_sentiment"),
                article_count=alert_info.get("article_count"),
                message=alert_info["message"],
                history_id=alert_info["history_id"],
                alert_type="news"
            )

        return {
            "status": "success",
            "triggered_count": len(triggered),
            "alerts": triggered
        }

    except Exception as e:
        print(f"Error checking news alerts: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@celery_app.task(bind=True, base=DatabaseTask, name="send_alert_notification")
def send_alert_notification_task(
    self,
    alert_id: int,
    symbol: str,
    condition: str,
    threshold: float,
    current_price: float = None,
    current_sentiment: float = None,
    article_count: int = None,
    message: str = None,
    history_id: int = None,
    alert_type: str = "price"
):
    """
    Send email notification for triggered alert

    Args:
        alert_id: Alert ID
        symbol: Stock symbol
        condition: Alert condition
        threshold: Threshold value
        current_price: Current price (for price alerts)
        current_sentiment: Current sentiment (for news alerts)
        article_count: Article count (for news alerts)
        message: Custom alert message
        history_id: Alert history record ID
        alert_type: 'price' or 'news'
    """
    print(f"Sending {alert_type} notification for alert {alert_id} ({symbol})...")

    try:
        # Send Discord notification based on alert type
        if alert_type == "news":
            success = send_news_alert_discord(
                alert_id=alert_id,
                symbol=symbol,
                condition=condition,
                threshold=threshold,
                current_sentiment=current_sentiment,
                article_count=article_count,
                message=message
            )
        else:  # price alert
            success = send_price_alert_discord(
                alert_id=alert_id,
                symbol=symbol,
                condition=condition,
                threshold=threshold,
                current_price=current_price,
                message=message
            )

        # Mark notification as sent in database
        if success and history_id:
            AlertService.mark_notification_sent(self.db, history_id)

        return {
            "status": "success" if success else "failed",
            "alert_id": alert_id,
            "symbol": symbol,
            "alert_type": alert_type
        }

    except Exception as e:
        print(f"Error sending notification for alert {alert_id}: {e}")
        return {
            "status": "error",
            "alert_id": alert_id,
            "error": str(e)
        }
