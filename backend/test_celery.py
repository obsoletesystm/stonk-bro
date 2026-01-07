"""Test Celery tasks"""
from app.celery_app import celery_app
from app.tasks.alert_tasks import check_all_alerts_task, check_news_alerts_task
from app.tasks.news_tasks import fetch_news_task
from app.tasks.data_tasks import fetch_daily_data_task

print("Testing Celery tasks...")
print("=" * 70)

# Test 1: Check news alerts
print("\n1. Testing news alerts check...")
result = check_news_alerts_task.delay()
print(f"   Task ID: {result.id}")
print(f"   Task state: {result.state}")
print(f"   Waiting for result...")
try:
    task_result = result.get(timeout=30)
    print(f"   Result: {task_result}")
except Exception as e:
    print(f"   Error: {e}")

# Test 2: Check all alerts (price + news)
print("\n2. Testing all alerts check...")
result = check_all_alerts_task.delay()
print(f"   Task ID: {result.id}")
print(f"   Task state: {result.state}")
try:
    task_result = result.get(timeout=30)
    print(f"   Result: {task_result}")
except Exception as e:
    print(f"   Error: {e}")

# Test 3: Fetch news (with specific symbols)
print("\n3. Testing news fetch...")
result = fetch_news_task.delay(symbols=['AAPL', 'MSFT'], days=1)
print(f"   Task ID: {result.id}")
print(f"   Task state: {result.state}")
try:
    task_result = result.get(timeout=60)
    print(f"   Result: {task_result}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 70)
print("Celery test complete!")
