"""Test news alert notification after fixing email function"""
import requests
import time

API_BASE = "http://localhost:8000/api/v1"

print("Testing News Alert Notification")
print("=" * 70)

# Step 1: Check current sentiment for AAPL
print("\n1. Checking current sentiment for AAPL...")
response = requests.get(f"{API_BASE}/news/AAPL/sentiment")
if response.status_code == 200:
    data = response.json()
    current_sentiment = data.get('avg_sentiment', 0)
    article_count = data.get('total_articles', 0)
    print(f"   Current sentiment: {current_sentiment:.4f}")
    print(f"   Articles: {article_count}")
else:
    print(f"   Error: {response.status_code}")
    exit(1)

# Step 2: Create an alert that should trigger
print("\n2. Creating a news alert that should trigger...")
alert_data = {
    "symbol": "AAPL",
    "condition": "SENTIMENT_ABOVE",
    "threshold_value": current_sentiment - 0.05,  # Set below current sentiment
    "message": "Test alert for notification fix"
}

response = requests.post(f"{API_BASE}/alerts", json=alert_data)
if response.status_code in [200, 201]:
    alert = response.json()
    alert_id = alert['id']
    print(f"   Alert created: ID={alert_id}")
    print(f"   Threshold: {alert['threshold_value']:.4f}")
else:
    print(f"   Error creating alert: {response.status_code} - {response.text}")
    exit(1)

# Step 3: Trigger alert check via API
print("\n3. Triggering news alert check...")
response = requests.post(f"{API_BASE}/alerts/news/check/AAPL")
if response.status_code == 200:
    result = response.json()

    # Handle both list and dict response formats
    if isinstance(result, list):
        triggered_alerts = result
        triggered_count = len(result)
    else:
        triggered_count = result.get('triggered_count', 0)
        triggered_alerts = result.get('alerts', [])

    print(f"   Triggered: {triggered_count} alerts")

    if triggered_count > 0:
        print("\n   Alert Details:")
        for alert in triggered_alerts:
            print(f"     - Alert ID: {alert.get('alert_id', alert.get('id'))}")
            print(f"     - Symbol: {alert.get('symbol', 'N/A')}")
            print(f"     - Condition: {alert.get('condition', 'N/A')}")
            print(f"     - Current Sentiment: {alert.get('current_sentiment', alert.get('sentiment', 'N/A'))}")
            print(f"     - Article Count: {alert.get('article_count', 'N/A')}")
            print(f"     - Notification Status: {alert.get('notification_status', 'N/A')}")
    else:
        print("   WARNING: Alert should have triggered but didn't!")
else:
    print(f"   Error: {response.status_code} - {response.text}")

# Step 4: Verify alert history
print("\n4. Verifying alert history...")
response = requests.get(f"{API_BASE}/alerts/{alert_id}/history")
if response.status_code == 200:
    history = response.json()
    print(f"   History records: {len(history)}")

    if len(history) > 0:
        latest = history[0]
        print(f"\n   Latest trigger:")
        print(f"     - Triggered at: {latest['triggered_at']}")
        print(f"     - Sentiment: {latest.get('sentiment_at_trigger', 'N/A')}")
        print(f"     - Articles: {latest.get('articles_count', 'N/A')}")
        if latest.get('trigger_details'):
            print(f"     - Details: {latest['trigger_details'][:100]}...")
else:
    print(f"   Error: {response.status_code}")

# Step 5: Check alert status
print("\n5. Checking alert status...")
response = requests.get(f"{API_BASE}/alerts/{alert_id}")
if response.status_code == 200:
    alert = response.json()
    print(f"   Status: {alert['status']}")
    print(f"   Triggered at: {alert.get('triggered_at', 'Not triggered')}")
else:
    print(f"   Error: {response.status_code}")

print("\n" + "=" * 70)
print("Test complete!")
