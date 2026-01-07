"""Celery application configuration"""
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery_app = Celery(
    "stonk_bro",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Import tasks
celery_app.autodiscover_tasks(['app.tasks'])

# Periodic task schedule
celery_app.conf.beat_schedule = {
    # Fetch daily stock data
    'fetch-daily-data': {
        'task': 'app.tasks.data_tasks.fetch_daily_data_task',
        'schedule': crontab(hour=20, minute=0),  # 8 PM UTC (after market close)
    },

    # Check all alerts every 15 minutes during market hours
    'check-all-alerts': {
        'task': 'check_alerts',
        'schedule': crontab(minute='*/15', hour='14-21', day_of_week='1-5'),  # Market hours
    },

    # Check news alerts every 30 minutes
    'check-news-alerts': {
        'task': 'check_news_alerts',
        'schedule': crontab(minute='*/30'),
    },

    # Fetch news hourly during market hours
    'fetch-news': {
        'task': 'app.tasks.news_tasks.fetch_news_task',
        'schedule': crontab(minute=0, hour='14-22', day_of_week='1-5'),
    },

    # Update sentiment history daily
    'update-sentiment-history': {
        'task': 'app.tasks.news_tasks.update_sentiment_history_task',
        'schedule': crontab(hour=23, minute=0),  # 11 PM UTC
    },
}
