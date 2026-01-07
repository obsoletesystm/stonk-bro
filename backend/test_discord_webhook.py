"""Test Discord webhook integration"""
import os
from app.utils.discord import (
    send_discord_webhook,
    send_price_alert_discord,
    send_news_alert_discord
)

print("Testing Discord Webhook Integration")
print("=" * 70)

webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

if not webhook_url:
    print("\n❌ ERROR: DISCORD_WEBHOOK_URL not set in environment")
    print("\nTo set up Discord webhooks:")
    print("1. Go to your Discord server")
    print("2. Server Settings -> Integrations -> Webhooks")
    print("3. Create a new webhook and copy the URL")
    print("4. Add to .env file:")
    print("   DISCORD_WEBHOOK_URL=your_webhook_url_here")
    print("\nSee docs/DISCORD_SETUP.md for detailed instructions")
    exit(1)

print(f"✓ Webhook URL configured: {webhook_url[:50]}...")

# Test 1: Simple message
print("\n" + "=" * 70)
print("Test 1: Sending simple test message...")
print("-" * 70)

success = send_discord_webhook(
    webhook_url,
    content="🧪 **Test Message from Stonk Bro**\nIf you can see this, your Discord webhook is working correctly!"
)

if success:
    print("✓ Simple message sent successfully")
else:
    print("❌ Failed to send simple message")

# Test 2: Price alert
print("\n" + "=" * 70)
print("Test 2: Sending price alert notification...")
print("-" * 70)

success = send_price_alert_discord(
    alert_id=999,
    symbol="AAPL",
    condition="PRICE_ABOVE",
    threshold=150.00,
    current_price=152.50,
    message="This is a test price alert"
)

if success:
    print("✓ Price alert sent successfully")
else:
    print("❌ Failed to send price alert")

# Test 3: News alert (positive sentiment)
print("\n" + "=" * 70)
print("Test 3: Sending positive news alert...")
print("-" * 70)

success = send_news_alert_discord(
    alert_id=998,
    symbol="MSFT",
    condition="SENTIMENT_ABOVE",
    threshold=0.200,
    current_sentiment=0.287,
    article_count=15,
    message="This is a test news alert (positive sentiment)"
)

if success:
    print("✓ Positive news alert sent successfully")
else:
    print("❌ Failed to send positive news alert")

# Test 4: News alert (negative sentiment)
print("\n" + "=" * 70)
print("Test 4: Sending negative news alert...")
print("-" * 70)

success = send_news_alert_discord(
    alert_id=997,
    symbol="TSLA",
    condition="SENTIMENT_BELOW",
    threshold=-0.100,
    current_sentiment=-0.245,
    article_count=22,
    message="This is a test news alert (negative sentiment)"
)

if success:
    print("✓ Negative news alert sent successfully")
else:
    print("❌ Failed to send negative news alert")

# Test 5: News alert (neutral sentiment)
print("\n" + "=" * 70)
print("Test 5: Sending neutral news alert...")
print("-" * 70)

success = send_news_alert_discord(
    alert_id=996,
    symbol="GOOGL",
    condition="NEWS_VOLUME_SPIKE",
    threshold=3.0,
    current_sentiment=0.02,
    article_count=45
)

if success:
    print("✓ Neutral news alert sent successfully")
else:
    print("❌ Failed to send neutral news alert")

print("\n" + "=" * 70)
print("✅ Discord webhook test complete!")
print("\nCheck your Discord channel for the test messages.")
print("=" * 70)
