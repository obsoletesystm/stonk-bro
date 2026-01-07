"""News-based alert service"""
import logging
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from app.models.alert import Alert, AlertHistory, AlertCondition, AlertStatus
from app.services.news_service import NewsService
from app.models.news import SentimentHistory

logger = logging.getLogger(__name__)


class NewsAlertService:
    """Service for checking and triggering news-based alerts"""

    @staticmethod
    def check_sentiment_condition(
        db: Session,
        alert: Alert,
        current_sentiment: float,
        article_count: int
    ) -> bool:
        """
        Check if a sentiment alert condition is met

        Args:
            db: Database session
            alert: The alert to check
            current_sentiment: Current sentiment score (-1 to 1)
            article_count: Number of articles in the period

        Returns:
            True if alert should trigger, False otherwise
        """
        if alert.condition == AlertCondition.SENTIMENT_ABOVE:
            return current_sentiment > alert.threshold_value

        elif alert.condition == AlertCondition.SENTIMENT_BELOW:
            return current_sentiment < alert.threshold_value

        elif alert.condition == AlertCondition.SENTIMENT_CHANGE:
            # Check sentiment change over last 24 hours
            yesterday = datetime.now() - timedelta(days=1)

            # Get sentiment from 24 hours ago
            prev_history = db.query(SentimentHistory).filter(
                SentimentHistory.symbol == alert.symbol,
                SentimentHistory.date >= yesterday.replace(hour=0, minute=0, second=0),
                SentimentHistory.date < yesterday.replace(hour=23, minute=59, second=59)
            ).first()

            if not prev_history or prev_history.avg_sentiment is None:
                # No previous data, can't detect change
                return False

            sentiment_change = abs(current_sentiment - prev_history.avg_sentiment)
            # threshold_value represents the minimum change (e.g., 0.3 for 30% change)
            return sentiment_change >= alert.threshold_value

        elif alert.condition == AlertCondition.NEWS_VOLUME_SPIKE:
            # Check for unusual news volume
            # Get average article count over past 7 days
            week_ago = datetime.now() - timedelta(days=7)

            history_records = db.query(SentimentHistory).filter(
                SentimentHistory.symbol == alert.symbol,
                SentimentHistory.date >= week_ago,
                SentimentHistory.total_articles.isnot(None)
            ).all()

            if len(history_records) < 3:
                # Not enough data to determine baseline
                return False

            avg_daily_articles = sum(h.total_articles for h in history_records) / len(history_records)

            # threshold_value represents the multiplier (e.g., 2.0 for 2x normal volume)
            return article_count >= (avg_daily_articles * alert.threshold_value)

        return False

    @staticmethod
    def trigger_news_alert(
        db: Session,
        alert: Alert,
        sentiment: float,
        article_count: int,
        details: Optional[Dict[str, Any]] = None
    ) -> AlertHistory:
        """
        Trigger a news-based alert and create history record

        Args:
            db: Database session
            alert: Alert to trigger
            sentiment: Sentiment score that triggered the alert
            article_count: Number of articles
            details: Additional details about the trigger

        Returns:
            AlertHistory record
        """
        # Update alert status
        alert.status = AlertStatus.TRIGGERED
        alert.triggered_at = datetime.now()

        # Create history record
        history = AlertHistory(
            alert_id=alert.id,
            sentiment_at_trigger=sentiment,
            articles_count=article_count,
            trigger_details=json.dumps(details) if details else None,
            price_at_trigger=None,  # No price for news alerts
            notification_sent=False
        )

        db.add(history)
        db.commit()
        db.refresh(history)

        logger.info(f"Triggered news alert {alert.id} for {alert.symbol}: "
                   f"{alert.condition.value} (sentiment: {sentiment:.3f})")

        return history

    @staticmethod
    def check_news_alerts_for_symbol(db: Session, symbol: str) -> List[Dict[str, Any]]:
        """
        Check all news-based alerts for a specific symbol

        Args:
            db: Database session
            symbol: Stock symbol

        Returns:
            List of triggered alerts with details
        """
        triggered = []

        # Get active news alerts for this symbol
        news_conditions = [
            AlertCondition.SENTIMENT_ABOVE,
            AlertCondition.SENTIMENT_BELOW,
            AlertCondition.SENTIMENT_CHANGE,
            AlertCondition.NEWS_VOLUME_SPIKE
        ]

        active_alerts = db.query(Alert).filter(
            Alert.symbol == symbol.upper(),
            Alert.status == AlertStatus.ACTIVE,
            Alert.condition.in_(news_conditions)
        ).all()

        if not active_alerts:
            return triggered

        # Get current sentiment data
        try:
            # Get sentiment for last 24 hours
            summary = NewsService.get_sentiment_summary(db, symbol, days=1)

            current_sentiment = summary.get('avg_sentiment', 0.0)
            article_count = summary.get('total_articles', 0)

            if article_count == 0:
                # No recent articles, skip checks
                logger.debug(f"No recent articles for {symbol}, skipping news alert checks")
                return triggered

            # Check each alert
            for alert in active_alerts:
                try:
                    if NewsAlertService.check_sentiment_condition(
                        db, alert, current_sentiment, article_count
                    ):
                        # Get recent articles for context
                        recent_articles = NewsService.get_recent_news(
                            db, symbols=[symbol], hours=24, limit=5
                        )

                        details = {
                            'sentiment': current_sentiment,
                            'article_count': article_count,
                            'positive_ratio': summary.get('positive_ratio', 0.0),
                            'negative_ratio': summary.get('negative_ratio', 0.0),
                            'trend': summary.get('sentiment_trend', 'unknown'),
                            'recent_headlines': [
                                {
                                    'title': a.title,
                                    'sentiment': a.sentiment_label,
                                    'score': a.sentiment_score
                                }
                                for a in recent_articles[:3]
                            ]
                        }

                        history = NewsAlertService.trigger_news_alert(
                            db, alert, current_sentiment, article_count, details
                        )

                        triggered.append({
                            "alert_id": alert.id,
                            "symbol": alert.symbol,
                            "condition": alert.condition.value,
                            "threshold": alert.threshold_value,
                            "current_sentiment": current_sentiment,
                            "article_count": article_count,
                            "message": alert.message,
                            "history_id": history.id,
                            "details": details
                        })

                except Exception as e:
                    logger.error(f"Error checking news alert {alert.id}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error getting sentiment data for {symbol}: {e}")

        return triggered

    @staticmethod
    def check_all_news_alerts(db: Session) -> List[Dict[str, Any]]:
        """
        Check all active news-based alerts across all symbols

        Returns:
            List of triggered alerts with details
        """
        triggered = []

        # Get all unique symbols with active news alerts
        news_conditions = [
            AlertCondition.SENTIMENT_ABOVE,
            AlertCondition.SENTIMENT_BELOW,
            AlertCondition.SENTIMENT_CHANGE,
            AlertCondition.NEWS_VOLUME_SPIKE
        ]

        active_alerts = db.query(Alert.symbol).filter(
            Alert.status == AlertStatus.ACTIVE,
            Alert.condition.in_(news_conditions)
        ).distinct().all()

        symbols = [alert.symbol for alert in active_alerts]

        logger.info(f"Checking news alerts for {len(symbols)} symbols: {symbols}")

        for symbol in symbols:
            symbol_triggered = NewsAlertService.check_news_alerts_for_symbol(db, symbol)
            triggered.extend(symbol_triggered)

        return triggered

    @staticmethod
    def get_news_alert_stats(db: Session, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics about news alerts

        Args:
            db: Database session
            symbol: Optional symbol filter

        Returns:
            Dictionary with alert statistics
        """
        news_conditions = [
            AlertCondition.SENTIMENT_ABOVE,
            AlertCondition.SENTIMENT_BELOW,
            AlertCondition.SENTIMENT_CHANGE,
            AlertCondition.NEWS_VOLUME_SPIKE
        ]

        query = db.query(Alert).filter(Alert.condition.in_(news_conditions))

        if symbol:
            query = query.filter(Alert.symbol == symbol.upper())

        total_alerts = query.count()
        active_alerts = query.filter(Alert.status == AlertStatus.ACTIVE).count()
        triggered_alerts = query.filter(Alert.status == AlertStatus.TRIGGERED).count()

        # Count by condition type
        by_condition = {}
        for condition in news_conditions:
            count = query.filter(Alert.condition == condition).count()
            if count > 0:
                by_condition[condition.value] = count

        return {
            'total_news_alerts': total_alerts,
            'active': active_alerts,
            'triggered': triggered_alerts,
            'by_condition': by_condition
        }
