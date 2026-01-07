# Price Alerts API Documentation

Complete price alert system for stock monitoring and notifications.

## Features

### ✅ Alert Types
- **Price Above** - Trigger when price goes above threshold
- **Price Below** - Trigger when price drops below threshold
- **Price Change %** - Trigger on percentage price movement
- **Volume Above** - Trigger when volume exceeds threshold

### ✅ Automatic Monitoring
- Cron-based alert checking (every 15 minutes during market hours)
- Manual trigger via API endpoint
- Email notifications when alerts trigger
- Full alert history tracking

### ✅ Smart Management
- Create, update, delete alerts
- Filter by symbol or status
- Active/Triggered/Disabled states
- Custom messages per alert

## Quick Start

### 1. Create an Alert

```bash
# Alert when AAPL goes above $150
curl -X POST http://localhost:8000/api/v1/alerts/ \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "condition": "price_above",
    "threshold_value": 150.0,
    "message": "AAPL broke above $150!"
  }'
```

Response:
```json
{
  "id": 1,
  "symbol": "AAPL",
  "condition": "price_above",
  "threshold_value": 150.0,
  "status": "active",
  "message": "AAPL broke above $150!",
  "created_at": "2026-01-07T12:00:00Z",
  "triggered_at": null
}
```

### 2. List Active Alerts

```bash
curl http://localhost:8000/api/v1/alerts/active
```

### 3. Manually Check Alerts

```bash
curl -X POST http://localhost:8000/api/v1/alerts/check
```

## API Endpoints

### Create Alert

**POST** `/api/v1/alerts/`

Create a new price alert.

**Request Body:**
```json
{
  "symbol": "AAPL",
  "condition": "price_above",  // price_above | price_below | price_change_percent | volume_above
  "threshold_value": 150.0,
  "message": "Optional custom message"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "symbol": "AAPL",
  "condition": "price_above",
  "threshold_value": 150.0,
  "status": "active",
  "message": "AAPL broke above $150!",
  "created_at": "2026-01-07T12:00:00Z",
  "triggered_at": null
}
```

---

### List Alerts

**GET** `/api/v1/alerts/`

List all alerts with optional filtering.

**Query Parameters:**
- `symbol` (optional) - Filter by stock symbol
- `status` (optional) - Filter by status (active, triggered, disabled)
- `skip` (optional, default: 0) - Pagination offset
- `limit` (optional, default: 100) - Max results

**Examples:**
```bash
# All alerts
curl http://localhost:8000/api/v1/alerts/

# Filter by symbol
curl http://localhost:8000/api/v1/alerts/?symbol=AAPL

# Filter by status
curl http://localhost:8000/api/v1/alerts/?status=active

# Pagination
curl http://localhost:8000/api/v1/alerts/?skip=10&limit=20
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "symbol": "AAPL",
    "condition": "price_above",
    "threshold_value": 150.0,
    "status": "active",
    "message": "AAPL broke above $150!",
    "created_at": "2026-01-07T12:00:00Z",
    "triggered_at": null
  }
]
```

---

### List Active Alerts

**GET** `/api/v1/alerts/active`

Get all active alerts (shortcut for `?status=active`).

**Response:** `200 OK` - Array of active alerts

---

### Get Alert Details

**GET** `/api/v1/alerts/{alert_id}`

Get a specific alert with its full trigger history.

**Response:** `200 OK`
```json
{
  "id": 1,
  "symbol": "AAPL",
  "condition": "price_above",
  "threshold_value": 150.0,
  "status": "triggered",
  "message": "AAPL broke above $150!",
  "created_at": "2026-01-07T12:00:00Z",
  "triggered_at": "2026-01-07T14:30:00Z",
  "history": [
    {
      "id": 1,
      "alert_id": 1,
      "triggered_at": "2026-01-07T14:30:00Z",
      "price_at_trigger": 152.50,
      "notification_sent": true
    }
  ]
}
```

**Errors:**
- `404 Not Found` - Alert does not exist

---

### Update Alert

**PUT** `/api/v1/alerts/{alert_id}`

Update an existing alert.

**Request Body:** (all fields optional)
```json
{
  "condition": "price_above",
  "threshold_value": 155.0,
  "status": "active",
  "message": "Updated message"
}
```

**Response:** `200 OK` - Updated alert object

**Errors:**
- `404 Not Found` - Alert does not exist

---

### Delete Alert

**DELETE** `/api/v1/alerts/{alert_id}`

Delete an alert permanently.

**Response:** `204 No Content`

**Errors:**
- `404 Not Found` - Alert does not exist

---

### Get Alert History

**GET** `/api/v1/alerts/{alert_id}/history`

Get trigger history for a specific alert.

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "alert_id": 1,
    "triggered_at": "2026-01-07T14:30:00Z",
    "price_at_trigger": 152.50,
    "notification_sent": true
  },
  {
    "id": 2,
    "alert_id": 1,
    "triggered_at": "2026-01-07T15:45:00Z",
    "price_at_trigger": 153.75,
    "notification_sent": true
  }
]
```

**Errors:**
- `404 Not Found` - Alert does not exist

---

### Check Alerts Now

**POST** `/api/v1/alerts/check`

Manually trigger alert checking (useful for testing).

**Response:** `200 OK`
```json
{
  "checked_at": "now",
  "triggered_count": 2,
  "triggered_alerts": [
    {
      "alert_id": 1,
      "symbol": "AAPL",
      "condition": "price_above",
      "threshold": 150.0,
      "current_price": 152.50,
      "message": "AAPL broke above $150!",
      "history_id": 1
    }
  ]
}
```

---

## Alert Conditions

### Price Above

Triggers when current price exceeds threshold.

```json
{
  "condition": "price_above",
  "threshold_value": 150.0
}
```

**Use case:** Breakout alerts, profit targets

---

### Price Below

Triggers when current price drops below threshold.

```json
{
  "condition": "price_below",
  "threshold_value": 145.0
}
```

**Use case:** Stop-loss alerts, buying opportunities

---

### Price Change Percent

Triggers when price changes by percentage (up or down).

```json
{
  "condition": "price_change_percent",
  "threshold_value": 5.0  // 5% change
}
```

**Use case:** Volatility alerts, significant movements

---

### Volume Above

Triggers when trading volume exceeds threshold.

```json
{
  "condition": "volume_above",
  "threshold_value": 50000000  // 50M shares
}
```

**Use case:** Unusual activity, breakouts

---

## Alert States

| State | Description |
|-------|-------------|
| **active** | Alert is monitoring and will trigger when condition is met |
| **triggered** | Alert condition has been met and notification sent |
| **disabled** | Alert is paused and won't check conditions |

---

## Email Notifications

### Setup

Configure email settings in `.env`:

```bash
# Email Settings (for alerts)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_specific_password
ALERT_EMAIL=your_email@gmail.com
```

### Gmail App Password

For Gmail, create an app-specific password:
1. Go to Google Account settings
2. Security → 2-Step Verification
3. App passwords → Generate password
4. Use this password in `SMTP_PASSWORD`

### Notification Format

Alerts send both plain text and HTML emails:

**Subject:** `🚨 Alert Triggered: AAPL - Price above $150.00`

**Body includes:**
- Symbol
- Condition description
- Current price
- Alert ID
- Custom message (if provided)

---

## Automated Checking

### Cron Script

The system includes a script for automated alert checking:

```bash
# Check alerts and send notifications
docker compose exec api python scripts/check_alerts.py

# Dry run (check without sending emails)
docker compose exec api python scripts/check_alerts.py --dry-run
```

### Cron Schedule

Add to your crontab (already in `cron/stonk-bro-cron`):

```bash
# Check alerts every 15 minutes during market hours (9:30 AM - 4:00 PM ET)
*/15 9-16 * * 1-5 cd /path/to/stonk-bro && docker compose exec -T api python scripts/check_alerts.py >> /var/log/stonk-bro/alerts.log 2>&1
```

### Celery Task (Alternative)

For asynchronous processing, use Celery:

```python
from app.tasks.alert_tasks import check_alerts_task

# Trigger alert check
check_alerts_task.delay()
```

---

## Common Workflows

### Breakout Alert

Monitor for price breaking above resistance:

```bash
curl -X POST http://localhost:8000/api/v1/alerts/ \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "TSLA",
    "condition": "price_above",
    "threshold_value": 250.0,
    "message": "TSLA broke resistance at $250"
  }'
```

---

### Stop-Loss Alert

Get notified when stock drops below support:

```bash
curl -X POST http://localhost:8000/api/v1/alerts/ \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "NVDA",
    "condition": "price_below",
    "threshold_value": 475.0,
    "message": "NVDA hit stop-loss at $475"
  }'
```

---

### High Volume Alert

Detect unusual trading activity:

```bash
curl -X POST http://localhost:8000/api/v1/alerts/ \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "GME",
    "condition": "volume_above",
    "threshold_value": 100000000,
    "message": "GME volume exceeded 100M - unusual activity"
  }'
```

---

### Portfolio Monitoring

Set multiple alerts for portfolio positions:

```bash
# Alert for each holding at key levels
for symbol in AAPL GOOGL MSFT; do
  curl -X POST http://localhost:8000/api/v1/alerts/ \
    -H "Content-Type: application/json" \
    -d "{
      \"symbol\": \"$symbol\",
      \"condition\": \"price_change_percent\",
      \"threshold_value\": 3.0,
      \"message\": \"$symbol moved 3% - check portfolio\"
    }"
done
```

---

## Testing

### Run Test Suite

```bash
# Full test suite
./test_alerts.sh
```

### Manual Testing

```bash
# 1. Create test alert
ALERT=$(curl -s -X POST http://localhost:8000/api/v1/alerts/ \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "condition": "price_above",
    "threshold_value": 1.0,
    "message": "Test alert"
  }')

# 2. Get alert ID
ALERT_ID=$(echo $ALERT | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")

# 3. Manually trigger check (will trigger because threshold is $1)
curl -X POST http://localhost:8000/api/v1/alerts/check

# 4. Check history
curl http://localhost:8000/api/v1/alerts/$ALERT_ID/history | python3 -m json.tool

# 5. Clean up
curl -X DELETE http://localhost:8000/api/v1/alerts/$ALERT_ID
```

---

## Database Schema

### alerts Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| symbol | VARCHAR(10) | Stock symbol |
| condition | ENUM | Alert condition type |
| threshold_value | FLOAT | Threshold for condition |
| status | ENUM | active/triggered/disabled |
| message | VARCHAR(500) | Custom message |
| created_at | TIMESTAMP | Creation time |
| triggered_at | TIMESTAMP | Last trigger time |

### alert_history Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| alert_id | INTEGER | Foreign key to alerts |
| triggered_at | TIMESTAMP | Trigger timestamp |
| price_at_trigger | FLOAT | Price when triggered |
| notification_sent | BOOLEAN | Email sent flag |

---

## Troubleshooting

### Alerts Not Triggering

**Check alert status:**
```bash
curl http://localhost:8000/api/v1/alerts/active
```

**Manually trigger check:**
```bash
curl -X POST http://localhost:8000/api/v1/alerts/check
```

**Check logs:**
```bash
docker compose logs api --tail=50
```

---

### Email Not Sending

**Verify email configuration:**
```bash
# Check .env has all settings
grep SMTP .env
grep ALERT_EMAIL .env
```

**Test email manually:**
```python
from app.utils.email import send_alert_notification

send_alert_notification(
    alert_id=1,
    symbol="AAPL",
    condition="price_above",
    threshold=150.0,
    current_price=152.5,
    message="Test"
)
```

---

### Rate Limiting

Yahoo Finance may rate limit requests. Solutions:

1. **Reduce check frequency** - Check every 30-60 minutes instead of 15
2. **Add delays** - Built-in 1-second delay between symbols
3. **Use caching** - Redis caches recent prices
4. **Alpha Vantage fallback** - Switch to Alpha Vantage for alerts

---

## Performance

### Expected Throughput

- Alert creation: < 10ms
- Alert checking (per symbol): ~1-2 seconds (API call)
- Email sending: ~500ms
- Database queries: < 5ms

### Scaling Recommendations

| Alerts | Strategy |
|--------|----------|
| < 100 | Cron script every 15 minutes |
| 100-1000 | Celery with distributed checking |
| > 1000 | Partition by symbol, multiple workers |

---

## Security

### Best Practices

1. **Validate thresholds** - Ensure positive values
2. **Rate limit API** - Prevent abuse of alert creation
3. **Sanitize messages** - Prevent XSS in email messages
4. **Secure SMTP** - Use app-specific passwords, not main password
5. **Alert limits** - Set max alerts per user (when auth added)

---

## Next Steps

- [ ] Add webhook notifications (Slack, Discord)
- [ ] SMS notifications via Twilio
- [ ] Alert templates and presets
- [ ] Multi-user support with alert ownership
- [ ] Alert performance analytics
- [ ] Mobile app push notifications

---

## Related Documentation

- [Portfolio API](PORTFOLIO_API.md)
- [Data Fetching](DATA_FETCHING.md)
- [Main README](README.md)
