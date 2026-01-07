# News-Based Alerts

News-based alerts allow you to monitor sentiment changes and news volume for your portfolio holdings. These alerts integrate with the News & Sentiment Analysis system to trigger notifications based on sentiment thresholds, sentiment changes, and news activity spikes.

## Features

- **Sentiment Threshold Alerts**: Get notified when sentiment crosses specific levels
- **Sentiment Change Detection**: Alert on significant sentiment shifts
- **News Volume Monitoring**: Detect unusual news activity
- **Rich Context**: Alerts include recent headlines and sentiment breakdowns
- **Historical Tracking**: Full history of alert triggers with detailed metadata

---

## Alert Types

### 1. SENTIMENT_ABOVE

Triggers when average sentiment rises above a threshold.

**Use Cases:**
- Alert when sentiment becomes positive (> 0.0)
- Notify on highly positive sentiment (> 0.5)
- Track improving market perception

**Example:**
```json
{
  "symbol": "AAPL",
  "condition": "SENTIMENT_ABOVE",
  "threshold_value": 0.2,
  "message": "AAPL sentiment is positive"
}
```

### 2. SENTIMENT_BELOW

Triggers when average sentiment falls below a threshold.

**Use Cases:**
- Alert on negative sentiment (< -0.2)
- Warning on severely negative news (< -0.5)
- Risk management notifications

**Example:**
```json
{
  "symbol": "TSLA",
  "condition": "SENTIMENT_BELOW",
  "threshold_value": -0.3,
  "message": "WARNING: TSLA sentiment turning negative"
}
```

### 3. SENTIMENT_CHANGE

Triggers when sentiment changes significantly from the previous day.

**Use Cases:**
- Detect sudden shifts in market perception
- Identify breaking news impact
- Track sentiment momentum

**Threshold:** Absolute change value (e.g., 0.3 = 30% sentiment change)

**Example:**
```json
{
  "symbol": "NVDA",
  "condition": "SENTIMENT_CHANGE",
  "threshold_value": 0.25,
  "message": "NVDA sentiment changed significantly"
}
```

### 4. NEWS_VOLUME_SPIKE

Triggers when news article volume exceeds normal levels.

**Use Cases:**
- Detect breaking news events
- Identify unusual market attention
- Monitor for potential volatility

**Threshold:** Multiplier of average daily volume (e.g., 2.0 = 2x normal volume)

**Example:**
```json
{
  "symbol": "GOOGL",
  "condition": "NEWS_VOLUME_SPIKE",
  "threshold_value": 3.0,
  "message": "Unusual news activity for GOOGL"
}
```

---

## API Endpoints

### Create News Alert

Create a new news-based alert.

**Endpoint:** `POST /api/v1/alerts/`

**Request Body:**
```json
{
  "symbol": "AAPL",
  "condition": "SENTIMENT_ABOVE",
  "threshold_value": 0.15,
  "message": "AAPL sentiment is positive"
}
```

**Response:**
```json
{
  "symbol": "AAPL",
  "condition": "SENTIMENT_ABOVE",
  "threshold_value": 0.15,
  "message": "AAPL sentiment is positive",
  "id": 5,
  "status": "active",
  "created_at": "2026-01-07T19:04:50.701012Z",
  "triggered_at": null
}
```

### Check News Alerts for Symbol

Check all news-based alerts for a specific symbol.

**Endpoint:** `POST /api/v1/alerts/news/check/{symbol}`

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/alerts/news/check/AAPL"
```

**Example Response:**
```json
{
  "symbol": "AAPL",
  "checked_at": "now",
  "triggered_count": 1,
  "triggered_alerts": [
    {
      "alert_id": 7,
      "symbol": "AAPL",
      "condition": "SENTIMENT_ABOVE",
      "threshold": 0.05,
      "current_sentiment": 0.087,
      "article_count": 9,
      "message": "AAPL sentiment is above 0.05",
      "history_id": 1,
      "details": {
        "sentiment": 0.087,
        "article_count": 9,
        "positive_ratio": 0.556,
        "negative_ratio": 0.222,
        "trend": "declining",
        "recent_headlines": [
          {
            "title": "AAPL beats earnings expectations",
            "sentiment": "positive",
            "score": 0.274
          }
        ]
      }
    }
  ]
}
```

### Check All Alerts (Price + News)

Check all active alerts including both price-based and news-based alerts.

**Endpoint:** `POST /api/v1/alerts/check`

**Query Parameters:**
- `include_news` (default: true): Whether to check news-based alerts

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/alerts/check?include_news=true"
```

### Get News Alert Statistics

Get statistics about news-based alerts.

**Endpoint:** `GET /api/v1/alerts/news/stats`

**Query Parameters:**
- `symbol` (optional): Filter by symbol

**Example Response:**
```json
{
  "total_news_alerts": 4,
  "active": 3,
  "triggered": 1,
  "by_condition": {
    "SENTIMENT_ABOVE": 2,
    "SENTIMENT_BELOW": 1,
    "SENTIMENT_CHANGE": 1
  }
}
```

### Get Alert with History

Retrieve a specific alert with its full trigger history.

**Endpoint:** `GET /api/v1/alerts/{alert_id}`

**Example Response:**
```json
{
  "symbol": "AAPL",
  "condition": "SENTIMENT_ABOVE",
  "threshold_value": 0.05,
  "message": "AAPL sentiment is above 0.05",
  "id": 7,
  "status": "triggered",
  "created_at": "2026-01-07T19:05:20.865010Z",
  "triggered_at": "2026-01-07T19:05:30.043332Z",
  "history": [
    {
      "id": 1,
      "alert_id": 7,
      "triggered_at": "2026-01-07T19:05:30.038644Z",
      "price_at_trigger": null,
      "notification_sent": false,
      "sentiment_at_trigger": 0.087,
      "articles_count": 9,
      "trigger_details": "{...}"
    }
  ]
}
```

---

## Alert Trigger Details

When a news alert triggers, it captures comprehensive context:

### Trigger Metadata

```json
{
  "sentiment": 0.087,
  "article_count": 9,
  "positive_ratio": 0.556,
  "negative_ratio": 0.222,
  "trend": "declining",
  "recent_headlines": [
    {
      "title": "Stock surges on earnings beat",
      "sentiment": "positive",
      "score": 0.85
    }
  ]
}
```

**Fields:**
- `sentiment`: Current average sentiment score (-1 to 1)
- `article_count`: Number of articles in the analysis period
- `positive_ratio`: Ratio of positive articles (0 to 1)
- `negative_ratio`: Ratio of negative articles (0 to 1)
- `trend`: Sentiment trend (improving, declining, stable)
- `recent_headlines`: Up to 3 most recent article headlines with sentiment

---

## Threshold Guidelines

### Sentiment Thresholds

Recommended values for sentiment alerts:

```
Very Negative:  < -0.5
Negative:       < -0.2
Neutral:        -0.2 to 0.2
Positive:       > 0.2
Very Positive:  > 0.5
```

**Examples:**
```json
// Conservative positive alert
{"condition": "SENTIMENT_ABOVE", "threshold_value": 0.3}

// Early warning negative alert
{"condition": "SENTIMENT_BELOW", "threshold_value": -0.15}

// Neutral threshold crossover
{"condition": "SENTIMENT_ABOVE", "threshold_value": 0.0}
```

### Sentiment Change Thresholds

Recommended values for detecting significant changes:

```
Minor Change:       0.1 to 0.2
Moderate Change:    0.2 to 0.3
Significant Change: 0.3 to 0.5
Major Shift:        > 0.5
```

**Example:**
```json
{
  "condition": "SENTIMENT_CHANGE",
  "threshold_value": 0.25
}
// Triggers when sentiment changes by ±0.25 from previous day
```

### News Volume Thresholds

Recommended multipliers for volume spike detection:

```
Moderate Activity: 1.5x to 2x
High Activity:     2x to 3x
Unusual Activity:  3x to 5x
Breaking News:     > 5x
```

**Example:**
```json
{
  "condition": "NEWS_VOLUME_SPIKE",
  "threshold_value": 2.5
}
// Triggers when article count is 2.5x the 7-day average
```

---

## Integration Examples

### Python Integration

```python
import requests

BASE_URL = "http://localhost:8000/api/v1/alerts"

# Create news alert
def create_sentiment_alert(symbol: str, threshold: float, condition: str = "SENTIMENT_ABOVE"):
    response = requests.post(
        f"{BASE_URL}/",
        json={
            "symbol": symbol,
            "condition": condition,
            "threshold_value": threshold,
            "message": f"{symbol} sentiment alert"
        }
    )
    return response.json()

# Check news alerts for a symbol
def check_news_alerts(symbol: str):
    response = requests.post(f"{BASE_URL}/news/check/{symbol}")
    return response.json()

# Get alert statistics
def get_alert_stats(symbol: str = None):
    params = {"symbol": symbol} if symbol else {}
    response = requests.get(f"{BASE_URL}/news/stats", params=params)
    return response.json()

# Example usage
alert = create_sentiment_alert("AAPL", 0.2, "SENTIMENT_ABOVE")
print(f"Created alert: {alert['id']}")

# Check for triggers
result = check_news_alerts("AAPL")
print(f"Triggered: {result['triggered_count']} alerts")

# Get stats
stats = get_alert_stats()
print(f"Total news alerts: {stats['total_news_alerts']}")
print(f"Active: {stats['active']}, Triggered: {stats['triggered']}")
```

### JavaScript Integration

```javascript
const BASE_URL = 'http://localhost:8000/api/v1/alerts';

// Create sentiment alert
async function createSentimentAlert(symbol, threshold, condition = 'SENTIMENT_ABOVE') {
  const response = await fetch(`${BASE_URL}/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      symbol,
      condition,
      threshold_value: threshold,
      message: `${symbol} sentiment alert`
    })
  });
  return response.json();
}

// Check news alerts
async function checkNewsAlerts(symbol) {
  const response = await fetch(`${BASE_URL}/news/check/${symbol}`, {
    method: 'POST'
  });
  return response.json();
}

// Get alert stats
async function getAlertStats(symbol = null) {
  const url = symbol
    ? `${BASE_URL}/news/stats?symbol=${symbol}`
    : `${BASE_URL}/news/stats`;
  const response = await fetch(url);
  return response.json();
}

// Example usage
const alert = await createSentimentAlert('AAPL', 0.2);
console.log(`Created alert: ${alert.id}`);

const result = await checkNewsAlerts('AAPL');
console.log(`Triggered: ${result.triggered_count} alerts`);

const stats = await getAlertStats();
console.log(`Active alerts: ${stats.active}`);
```

---

## Best Practices

### 1. Alert Configuration

**DO:**
- Set reasonable thresholds based on historical sentiment patterns
- Use SENTIMENT_ABOVE/BELOW for absolute level monitoring
- Use SENTIMENT_CHANGE for volatility detection
- Combine multiple alert types for comprehensive monitoring

**DON'T:**
- Set thresholds too tight (avoid alert fatigue)
- Create duplicate alerts for the same condition
- Ignore historical sentiment trends when setting thresholds

### 2. Alert Management

**DO:**
- Regularly review and update alert thresholds
- Delete or disable alerts that aren't actionable
- Monitor alert trigger frequency
- Use meaningful alert messages

**DON'T:**
- Leave triggered alerts in the system indefinitely
- Create alerts without a clear action plan
- Set alerts for symbols you don't actively monitor

### 3. Monitoring Strategy

**Example Portfolio Monitoring:**
```json
// Conservative long-term investor
{
  "symbol": "AAPL",
  "condition": "SENTIMENT_BELOW",
  "threshold_value": -0.3,
  "message": "Consider reviewing AAPL position"
}

// Active trader
{
  "symbol": "TSLA",
  "condition": "SENTIMENT_CHANGE",
  "threshold_value": 0.2,
  "message": "TSLA sentiment shift - check news"
}

// News-driven strategy
{
  "symbol": "NVDA",
  "condition": "NEWS_VOLUME_SPIKE",
  "threshold_value": 3.0,
  "message": "Breaking news for NVDA"
}
```

---

## Automated Alert Checking

### Background Task Setup

For production use, set up automated alert checking:

```python
from app.core.db import SessionLocal
from app.services.alert_service import AlertService
import schedule
import time

def check_all_alerts():
    """Periodic alert checking"""
    db = SessionLocal()
    try:
        triggered = AlertService.check_all_active_alerts(db, include_news=True)

        for alert in triggered:
            print(f"Alert triggered: {alert['symbol']} - {alert['condition']}")
            # Send notification (email, webhook, etc.)

    finally:
        db.close()

# Run every 15 minutes
schedule.every(15).minutes.do(check_all_alerts)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Celery Integration (Recommended)

```python
from celery import Celery
from app.services.alert_service import AlertService
from app.core.db import SessionLocal

celery_app = Celery('alerts', broker='redis://localhost:6379/0')

@celery_app.task
def check_news_alerts_task():
    """Celery task to check news alerts"""
    db = SessionLocal()
    try:
        from app.services.news_alert_service import NewsAlertService
        triggered = NewsAlertService.check_all_news_alerts(db)

        # Process triggered alerts
        for alert_data in triggered:
            # Send notifications
            send_alert_notification(alert_data)

        return {
            'checked_at': datetime.now(),
            'triggered_count': len(triggered)
        }
    finally:
        db.close()

# Schedule task
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Check news alerts every 30 minutes
    sender.add_periodic_task(
        1800.0,  # 30 minutes
        check_news_alerts_task.s(),
        name='check news alerts every 30 minutes'
    )
```

---

## Troubleshooting

### Common Issues

**1. Alert Not Triggering**

*Problem:* Alert created but never triggers

*Solutions:*
- Check if there are recent articles for the symbol
- Verify sentiment is calculated (check `/news/{symbol}/sentiment`)
- Ensure threshold is reasonable for current sentiment levels
- Check alert status (may already be triggered)

**2. Too Many Triggers**

*Problem:* Alert triggering too frequently

*Solutions:*
- Increase threshold value
- Use SENTIMENT_CHANGE instead of SENTIMENT_ABOVE/BELOW
- Add cooldown period (manual management currently)
- Review and adjust based on historical patterns

**3. No Recent Articles**

*Problem:* "No recent articles found" when checking alerts

*Solutions:*
- Run news fetcher: `python scripts/fetch_news.py --symbols AAPL`
- Check if symbol is covered by news sources
- Verify news fetching is working: `GET /api/v1/news/stats`

**4. Sentiment Data Missing**

*Problem:* Alert check returns errors about missing sentiment

*Solutions:*
- Ensure articles have sentiment analysis
- Run sentiment analysis on existing articles
- Check sentiment analyzer is configured
- Verify database has sentiment_history records

---

## Performance Considerations

### Alert Checking Frequency

Recommended checking frequencies based on use case:

```
Real-time Trading:    Every 5-15 minutes
Active Monitoring:    Every 30 minutes
Portfolio Tracking:   Every 1-2 hours
Long-term Investing:  Daily
```

### Database Impact

- News alert checks query sentiment_history and news_articles tables
- Use indexes on `symbol` and `date` fields (already configured)
- Limit alert checking to reasonable frequencies
- Consider caching sentiment summaries for frequently checked symbols

### Optimization Tips

1. **Batch Processing**: Check all alerts for a symbol at once
2. **Smart Scheduling**: Align checks with news fetching schedule
3. **Selective Checking**: Only check alerts for symbols with recent news
4. **Caching**: Cache sentiment summaries for 5-15 minutes

---

## Future Enhancements

Planned improvements:

1. **Alert Cooldown**: Prevent re-triggering within a time period
2. **Multi-Symbol Alerts**: Alert on sector or portfolio sentiment
3. **Trend Alerts**: Trigger on sustained sentiment trends (3+ days)
4. **Confidence Threshold**: Only trigger on high-confidence sentiment
5. **Custom Aggregation**: User-defined sentiment calculation windows
6. **Alert Groups**: Organize alerts by strategy or portfolio
7. **Notification Channels**: Email, SMS, webhook, push notifications
8. **Alert Templates**: Pre-configured alert sets for common strategies

---

## Related Documentation

- [News & Sentiment API](NEWS_API.md) - Full news and sentiment analysis documentation
- [Alerts API](../api/v1/endpoints/alerts.py) - Price-based alerts
- [Alert Models](../models/alert.py) - Database models

---

## Support

For issues or questions:
- Check API documentation at `/docs` (Swagger UI)
- Review logs for error messages
- Test with `/alerts/news/check/{symbol}` endpoint
- Verify sentiment data with `/news/{symbol}/sentiment`
