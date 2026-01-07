# Discord Webhook Setup for Alerts

This guide shows you how to set up Discord webhooks to receive alert notifications from Stonk Bro.

## Creating a Discord Webhook

1. **Open Discord** and navigate to the server where you want to receive alerts

2. **Access Server Settings**:
   - Right-click on the server name
   - Select "Server Settings"

3. **Create a Webhook**:
   - Click on "Integrations" in the left sidebar
   - Click "Webhooks" or "View Webhooks"
   - Click "New Webhook" or "Create Webhook"

4. **Configure the Webhook**:
   - Give it a name (e.g., "Stonk Bro Alerts")
   - Select the channel where you want alerts to appear
   - (Optional) Upload a custom avatar image
   - Click "Copy Webhook URL"

5. **Add to Environment**:
   - Open your `.env` file
   - Add the webhook URL:
     ```bash
     DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN
     ```

6. **Restart Services**:
   ```bash
   docker compose restart api celery-worker
   ```

## Testing Your Webhook

You can test your Discord webhook using the provided test script:

```bash
# From the backend directory
docker exec stonk-api python test_discord_webhook.py
```

This will send a test message to your Discord channel.

## Alert Types

### Price Alerts
Price alerts appear in Discord with:
- 🚨 Icon for triggered alerts
- Green color for "above" conditions
- Red color for "below" conditions
- Current price vs threshold
- Custom message (if provided)

### News Alerts
News alerts appear in Discord with:
- 📰 Icon for news alerts
- 📈 Green for positive sentiment
- 📉 Red for negative sentiment
- ➡️ Gray for neutral sentiment
- Sentiment score and label
- Number of articles analyzed
- Custom message (if provided)

## Example Alert Messages

### Price Alert Example
```
🚨 Price Alert Triggered: AAPL

Price above $150.00

Symbol: AAPL
Current Price: $152.50
Threshold: $150.00
Alert ID: 5

📝 Your Note
Watch for resistance at $155
```

### News Alert Example
```
📰 News Alert Triggered: MSFT

Sentiment above 0.200

Symbol: MSFT
Current Sentiment: 📈 0.287 (Positive)
Articles Analyzed: 15
Threshold: 0.200
Alert ID: 8

📝 Your Note
Strong positive sentiment on earnings
```

## Troubleshooting

### Webhook URL Not Working
- Verify the URL is complete and starts with `https://discord.com/api/webhooks/`
- Check that the webhook hasn't been deleted in Discord
- Ensure the bot has permissions to post in the selected channel

### Not Receiving Alerts
- Check Celery worker logs: `docker logs stonk-celery-worker --tail 50`
- Verify DISCORD_WEBHOOK_URL is set: `docker exec stonk-api env | grep DISCORD`
- Ensure alerts are being triggered (check alert history in API)

### Rate Limiting
Discord webhooks have rate limits:
- 30 requests per minute per webhook
- If you exceed this, alerts will be queued
- Consider creating multiple webhooks for high-volume alerts

## Security Notes

- **Keep your webhook URL secret** - anyone with the URL can post to your channel
- Don't commit webhook URLs to version control
- Regenerate webhook if compromised (Discord -> Edit Webhook -> Reset Webhook URL)
- Use channel permissions to control who can see alerts

## Advanced: Multiple Webhooks

You can create separate webhooks for different alert types:

```bash
# In .env
DISCORD_WEBHOOK_PRICE_ALERTS=https://discord.com/api/webhooks/...
DISCORD_WEBHOOK_NEWS_ALERTS=https://discord.com/api/webhooks/...
```

Then modify `app/utils/discord.py` to use different webhooks based on alert type.
