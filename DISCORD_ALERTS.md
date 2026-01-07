# Discord Alert Integration

Stonk Bro now sends alert notifications directly to Discord using webhooks! 🎉

## Quick Setup

### 1. Create a Discord Webhook

1. Open Discord and go to your server
2. Right-click the server name → **Server Settings**
3. Click **Integrations** → **Webhooks**
4. Click **New Webhook** or **Create Webhook**
5. Configure:
   - Name: `Stonk Bro Alerts` (or any name you prefer)
   - Channel: Select where you want alerts to appear
   - (Optional) Set a custom avatar
6. Click **Copy Webhook URL**

### 2. Add Webhook to Environment

Edit your `.env` file and add:

```bash
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN
```

Replace with the URL you copied from Discord.

### 3. Restart Services

```bash
docker compose restart api celery-worker
```

### 4. Test the Integration

Run the test script to verify everything works:

```bash
docker exec stonk-api python test_discord_webhook.py
```

You should see test messages in your Discord channel! 🎊

## What You'll Receive

### Price Alerts 🚨

When a price alert triggers, you'll get a rich Discord message with:
- Stock symbol
- Current price
- Threshold value
- Alert ID
- Your custom note (if provided)
- Color-coded: 🟢 Green for "above", 🔴 Red for "below"

**Example:**
```
🚨 Price Alert Triggered: AAPL
Price above $150.00

Symbol: AAPL
Current Price: $152.50
Threshold: $150.00
Alert ID: 5
```

### News Alerts 📰

When a news/sentiment alert triggers, you'll get:
- Stock symbol
- Current sentiment score and label
- Number of articles analyzed
- Threshold value
- Alert ID
- Your custom note (if provided)
- Color-coded by sentiment: 📈 Green (positive), 📉 Red (negative), ➡️ Gray (neutral)

**Example:**
```
📰 News Alert Triggered: MSFT
Sentiment above 0.200

Symbol: MSFT
Current Sentiment: 📈 0.287 (Positive)
Articles Analyzed: 15
Threshold: 0.200
Alert ID: 8
```

## Testing with Real Alerts

### Test Price Alert

```bash
curl -X POST "http://localhost:8000/api/v1/alerts" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "condition": "PRICE_ABOVE",
    "threshold_value": 1.00,
    "message": "Test Discord notification"
  }'
```

### Test News Alert

```bash
curl -X POST "http://localhost:8000/api/v1/alerts" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "MSFT",
    "condition": "SENTIMENT_ABOVE",
    "threshold_value": -1.00,
    "message": "Test Discord news alert"
  }'
```

Then trigger a check:

```bash
# For news alerts
curl -X POST "http://localhost:8000/api/v1/alerts/news/check/MSFT"
```

## Troubleshooting

### Not receiving notifications?

1. **Check webhook URL is set:**
   ```bash
   docker exec stonk-api env | grep DISCORD_WEBHOOK_URL
   ```

2. **Verify services restarted:**
   ```bash
   docker compose ps
   ```

3. **Check Celery worker logs:**
   ```bash
   docker logs stonk-celery-worker --tail 50
   ```

4. **Test webhook directly:**
   ```bash
   docker exec stonk-api python test_discord_webhook.py
   ```

### Webhook URL not working?

- Ensure URL starts with `https://discord.com/api/webhooks/`
- Check the webhook hasn't been deleted in Discord
- Verify you copied the complete URL (it's long!)
- Try creating a new webhook

### Messages not formatted correctly?

- Update to the latest code: `git pull`
- Restart services: `docker compose restart api celery-worker`

## Rate Limits

Discord webhooks are rate-limited to:
- **30 requests per minute** per webhook

If you have many alerts, consider:
- Creating multiple webhooks for different stocks/types
- Batching notifications (future feature)

## Security

⚠️ **Keep your webhook URL secret!**

- Anyone with the URL can post to your Discord channel
- Don't commit it to version control (it's in `.gitignore`)
- If compromised, regenerate it in Discord Server Settings

## Advanced Configuration

### Separate Webhooks for Different Alert Types

In `.env`:
```bash
DISCORD_WEBHOOK_PRICE=https://discord.com/api/webhooks/...
DISCORD_WEBHOOK_NEWS=https://discord.com/api/webhooks/...
```

Modify `backend/app/utils/discord.py` to use different URLs based on alert type.

### Custom Formatting

Edit `backend/app/utils/discord.py` to customize:
- Colors (hex color codes in `color` field)
- Emojis
- Field layout
- Message content

## Documentation

Full setup guide: `backend/docs/DISCORD_SETUP.md`

## Questions?

Open an issue on GitHub or check the documentation!

---

**Happy trading! 📊💰**
