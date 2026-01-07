"""Test complete Celery notification flow for news alerts"""
from app.core.db import SessionLocal
from app.models.alert import Alert, AlertStatus, AlertCondition
from app.services.news_service import NewsService
from app.tasks.alert_tasks import check_news_alerts_task
import time

db = SessionLocal()

print("Testing Complete Celery News Alert Notification Flow")
print("=" * 70)

try:
    # Step 1: Get current sentiment for MSFT
    print("\n1. Getting current sentiment for MSFT...")
    summary = NewsService.get_sentiment_summary(db, "MSFT", days=1)
    current_sentiment = summary.get('avg_sentiment', 0.0)
    article_count = summary.get('total_articles', 0)

    print(f"   Current sentiment: {current_sentiment:.4f}")
    print(f"   Articles: {article_count}")

    # Step 2: Create a new alert with threshold below current sentiment
    print("\n2. Creating new alert that should trigger...")
    threshold = current_sentiment - 0.1  # Set threshold below current

    new_alert = Alert(
        symbol="MSFT",
        condition=AlertCondition.SENTIMENT_ABOVE,
        threshold_value=threshold,
        status=AlertStatus.ACTIVE,
        message="Celery notification test alert"
    )

    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)

    print(f"   Alert created: ID={new_alert.id}")
    print(f"   Threshold: {threshold:.4f}")
    print(f"   Should trigger: {current_sentiment > threshold}")

    # Step 3: Trigger Celery task to check alerts
    print("\n3. Triggering Celery news alerts check task...")
    result = check_news_alerts_task.delay()

    print(f"   Task ID: {result.id}")
    print(f"   Waiting for result...")

    task_result = result.get(timeout=30)

    print(f"\n   Status: {task_result['status']}")
    print(f"   Triggered count: {task_result['triggered_count']}")

    if task_result['triggered_count'] > 0:
        print("\n   Triggered alerts:")
        for alert in task_result['alerts']:
            print(f"     - Alert ID: {alert['alert_id']}")
            print(f"     - Symbol: {alert['symbol']}")
            print(f"     - Condition: {alert['condition']}")
            print(f"     - Current Sentiment: {alert.get('current_sentiment', 'N/A'):.4f}")
            print(f"     - Article Count: {alert.get('article_count', 'N/A')}")

        # Wait for notification tasks
        print("\n4. Waiting for notification tasks to complete...")
        time.sleep(2)
        print("   Check Celery worker logs with:")
        print("   docker logs stonk-celery-worker --tail 50 | grep -E 'notification|ALERT_EMAIL'")
    else:
        print("\n   ERROR: Alert should have triggered but didn't!")
        print(f"   Debug: current_sentiment={current_sentiment:.4f}, threshold={threshold:.4f}")

except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()

finally:
    db.close()

print("\n" + "=" * 70)
print("Test complete!")
