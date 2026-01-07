"""Test news alert notification via Celery task"""
from app.tasks.alert_tasks import check_news_alerts_task
import time

print("Testing News Alert Notification via Celery")
print("=" * 70)

# Trigger the task
print("\nTriggering news alerts check via Celery...")
result = check_news_alerts_task.delay()

print(f"Task ID: {result.id}")
print(f"Task state: {result.state}")
print(f"Waiting for result...\n")

try:
    task_result = result.get(timeout=30)
    print(f"Status: {task_result['status']}")
    print(f"Triggered count: {task_result['triggered_count']}")

    if task_result['triggered_count'] > 0:
        print("\nTriggered alerts:")
        for alert in task_result['alerts']:
            print(f"  - Alert ID: {alert['alert_id']}")
            print(f"    Symbol: {alert['symbol']}")
            print(f"    Condition: {alert['condition']}")
            print(f"    Current Sentiment: {alert.get('current_sentiment', 'N/A')}")
            print(f"    Article Count: {alert.get('article_count', 'N/A')}")
            print()

        # Wait a moment for notification tasks to process
        print("Waiting for notification tasks to complete...")
        time.sleep(3)
        print("\nCheck Celery worker logs for notification status")

    else:
        print("\nNo alerts triggered.")

except Exception as e:
    print(f"Error: {e}")

print("=" * 70)
