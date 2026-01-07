# Discord Integration Summary

## What Changed

The alert notification system has been updated to use Discord webhooks instead of email.

### Files Created

1. **`backend/app/utils/discord.py`** - Discord webhook integration
   - `send_price_alert_discord()` - Send price alert to Discord with rich embeds
   - `send_news_alert_discord()` - Send news/sentiment alert to Discord with rich embeds
   - Color-coded messages (green for positive, red for negative, gray for neutral)
   - Emoji indicators (🚨 for price, 📰 for news, 📈📉➡️ for sentiment trends)

2. **`backend/docs/DISCORD_SETUP.md`** - Detailed setup guide
   - Step-by-step webhook creation instructions
   - Troubleshooting guide
   - Security notes

3. **`backend/test_discord_webhook.py`** - Test script
   - Tests simple messages
   - Tests price alerts (positive/negative)
   - Tests news alerts (positive/negative/neutral sentiment)

4. **`DISCORD_ALERTS.md`** - Quick start guide
   - Setup instructions
   - Testing examples
   - Troubleshooting tips

### Files Modified

1. **`backend/app/tasks/alert_tasks.py`**
   - Replaced email imports with Discord imports
   - Updated `send_alert_notification_task()` to use Discord functions
   - Separate functions for price vs news alerts

2. **`.env.example`**
   - Removed email settings (SMTP_HOST, SMTP_USER, etc.)
   - Added `DISCORD_WEBHOOK_URL` configuration

## Setup Instructions

### 1. Get Discord Webhook URL

1. Open Discord → Server Settings → Integrations → Webhooks
2. Create a new webhook
3. Copy the webhook URL

### 2. Configure Environment

Add to your `.env` file:
```bash
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN
```

### 3. Restart Services

```bash
docker compose restart api celery-worker
```

### 4. Test It

```bash
docker exec stonk-api python test_discord_webhook.py
```

Check your Discord channel - you should see test messages!

## How It Works

### Price Alerts

When a price alert triggers:
1. Celery task `check_all_alerts_task` runs (every 15 min during market hours)
2. Finds triggered alerts
3. Calls `send_alert_notification_task` with price data
4. `send_price_alert_discord()` formats a rich Discord embed
5. Message appears in your Discord channel

### News Alerts

When a news/sentiment alert triggers:
1. Celery task `check_news_alerts_task` runs (every 30 min)
2. Analyzes recent sentiment data
3. Finds triggered alerts
4. Calls `send_alert_notification_task` with sentiment data
5. `send_news_alert_discord()` formats a rich Discord embed with sentiment info
6. Message appears in your Discord channel

## Message Format

### Price Alert Example
```
🚨 Price Alert Triggered: AAPL
Price above $150.00

┌─────────────────┬──────────┐
│ Symbol          │ AAPL     │
│ Current Price   │ $152.50  │
│ Threshold       │ $150.00  │
│ Alert ID        │ 5        │
└─────────────────┴──────────┘

📝 Your Note
Watch for resistance at $155

Stonk Bro Alert System
```

### News Alert Example
```
📰 News Alert Triggered: MSFT
Sentiment above 0.200

┌─────────────────────┬────────────────────────────┐
│ Symbol              │ MSFT                       │
│ Current Sentiment   │ 📈 0.287 (Positive)       │
│ Articles Analyzed   │ 15                         │
│ Threshold           │ 0.200                      │
│ Alert ID            │ 8                          │
└─────────────────────┴────────────────────────────┘

📝 Your Note
Strong positive sentiment on earnings

Stonk Bro Alert System
```

## Benefits of Discord vs Email

✅ **Instant notifications** - No email delays
✅ **Rich formatting** - Colors, emojis, structured data
✅ **Mobile & Desktop** - Discord apps on all platforms
✅ **No SMTP setup** - Just a webhook URL
✅ **Free** - No email service required
✅ **Organized** - Dedicated channel for alerts
✅ **Searchable** - Easy to find past alerts

## Next Steps

1. Set up your Discord webhook (see DISCORD_ALERTS.md)
2. Test with the test script
3. Create some alerts
4. Watch for notifications in Discord!

## Removed

- Email notification system (`app/utils/email.py` - still exists but not used)
- SMTP environment variables from .env.example
- Email-related code from alert tasks

## Notes

- The old email system is still in the codebase if you ever want to switch back
- You can easily add both Discord AND email by calling both functions in the task
- Discord webhooks have a rate limit of 30 requests/minute - more than enough for typical usage
