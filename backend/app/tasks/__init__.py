"""Celery tasks"""
from app.tasks.alert_tasks import (
    check_all_alerts_task,
    check_news_alerts_task,
    send_alert_notification_task
)
from app.tasks.data_tasks import (
    fetch_daily_data_task,
    fetch_stock_data_task,
    backfill_historical_data_task
)
from app.tasks.news_tasks import (
    fetch_news_task,
    fetch_news_for_symbol_task,
    update_sentiment_history_task,
    analyze_sentiment_batch_task
)
from app.tasks.sentiment_tasks import (
    collect_reddit_content_task,
    collect_news_content_task,
    process_unprocessed_content_task
)

__all__ = [
    # Alert tasks
    "check_all_alerts_task",
    "check_news_alerts_task",
    "send_alert_notification_task",
    # Data tasks
    "fetch_daily_data_task",
    "fetch_stock_data_task",
    "backfill_historical_data_task",
    # News tasks
    "fetch_news_task",
    "fetch_news_for_symbol_task",
    "update_sentiment_history_task",
    "analyze_sentiment_batch_task",
    # Sentiment collection tasks
    "collect_reddit_content_task",
    "collect_news_content_task",
    "process_unprocessed_content_task",
]
