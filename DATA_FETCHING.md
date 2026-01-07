# Data Fetching Documentation

Complete data fetching infrastructure for populating historical stock data.

## Features

### ✅ Smart Data Fetcher
- **Rate limiting** - Respects API limits (Alpha Vantage: 5/min, yfinance: 1/sec)
- **Caching** - Redis-backed caching to minimize API calls
- **Multiple sources** - yfinance (primary), Alpha Vantage (fallback)
- **Auto-save** - Saves data to TimescaleDB automatically

### ✅ Three Main Scripts

1. **fetch_historical_data.py** - Initial data population
2. **update_daily_prices.py** - Daily updates (for cron)
3. **backfill_data.py** - Fill gaps in historical data

### ✅ Automatic Scheduling
- Cron job configuration included
- Daily updates after market close
- Weekly ML model training
- Automated backups

## Quick Start

### 1. Fetch Historical Data

```bash
# Fetch 1 year of data for specific symbols
docker compose exec api python scripts/fetch_historical_data.py \
  --symbols AAPL,GOOGL,MSFT \
  --years 1

# Fetch 5 years of data
docker compose exec api python scripts/fetch_historical_data.py \
  --symbols AAPL \
  --years 5

# Fetch maximum available history
docker compose exec api python scripts/fetch_historical_data.py \
  --symbols AAPL \
  --period max

# Fetch data for all stocks in your portfolio
docker compose exec api python scripts/fetch_historical_data.py \
  --from-portfolio \
  --years 2
```

### 2. Daily Updates

```bash
# Update all portfolio holdings with latest prices
docker compose exec api python scripts/update_daily_prices.py

# Update specific symbols
docker compose exec api python scripts/update_daily_prices.py \
  --symbols AAPL,GOOGL
```

### 3. Backfill Missing Data

```bash
# Fill gaps from a specific date
docker compose exec api python scripts/backfill_data.py \
  --symbols AAPL \
  --start-date 2020-01-01

# Backfill all portfolio holdings
docker compose exec api python scripts/backfill_data.py \
  --from-portfolio \
  --start-date 2023-01-01
```

## Data Sources

### Primary: yfinance (Unlimited, Free)
- No rate limits (be respectful)
- Historical data: up to 100+ years
- Real-time quotes
- Adjusted prices included
- **Best for:** All use cases

### Fallback: Alpha Vantage (25 requests/day, Free)
- 5 calls per minute
- 25 calls per day (free tier)
- More reliable for certain symbols
- **Best for:** When yfinance fails

```bash
# Use Alpha Vantage instead
docker compose exec api python scripts/fetch_historical_data.py \
  --symbols AAPL \
  --source alpha_vantage \
  --years 1
```

## Caching Strategy

The system caches data in Redis to minimize API calls:

- **Historical data:** 24-hour TTL
- **Real-time quotes:** 5-minute TTL during market hours
- **Fundamental data:** 1-week TTL

## Automated Scheduling

### Install Cron Jobs

```bash
# Review and install cron jobs
./scripts/setup_cron.sh
```

### Cron Schedule

**Daily:**
- `5:00 PM ET (Mon-Fri)` - Update daily prices

**Weekly:**
- `Sunday 2:00 AM` - Train ML models
- `Sunday 4:00 AM` - Cleanup old data
- `Sunday 5:00 AM` - Health check

**Continuous:**
- `Every 6 hours` - Fetch news (optional)
- `Every 15 min` - Check alerts (optional, during market hours)

**Maintenance:**
- `Daily 3:00 AM` - Database backup
- `Monthly` - Cleanup old backups (keep 90 days)

### Manual Cron Setup

```bash
# Edit crontab
crontab -e

# Add this line for daily updates:
0 17 * * 1-5 cd /path/to/stonk-bro && docker compose exec -T api python scripts/update_daily_prices.py >> /var/log/stonk-bro/daily-update.log 2>&1
```

## Database Schema

### stock_quotes Table (TimescaleDB Hypertable)

```sql
CREATE TABLE stock_quotes (
    symbol VARCHAR(10),
    timestamp TIMESTAMPTZ,
    open NUMERIC(12, 4),
    high NUMERIC(12, 4),
    low NUMERIC(12, 4),
    close NUMERIC(12, 4),
    volume BIGINT,
    adjusted_close NUMERIC(12, 4),
    PRIMARY KEY (symbol, timestamp)
);

-- Optimized for time-series queries
SELECT create_hypertable('stock_quotes', 'timestamp');
```

### Query Examples

```sql
-- Get latest price for AAPL
SELECT * FROM stock_quotes
WHERE symbol = 'AAPL'
ORDER BY timestamp DESC
LIMIT 1;

-- Get 1 year of AAPL data
SELECT * FROM stock_quotes
WHERE symbol = 'AAPL'
  AND timestamp >= NOW() - INTERVAL '1 year'
ORDER BY timestamp;

-- Get all symbols with data
SELECT symbol, COUNT(*) as records
FROM stock_quotes
GROUP BY symbol
ORDER BY symbol;

-- Check data coverage
SELECT
    symbol,
    COUNT(*) as records,
    MIN(timestamp) as earliest,
    MAX(timestamp) as latest
FROM stock_quotes
GROUP BY symbol;
```

## Testing

### Run Automated Tests

```bash
# Full test suite
./test_data_fetch.sh
```

This will:
1. Create test portfolio
2. Add holdings (AAPL, GOOGL, MSFT)
3. Fetch historical data
4. Update daily prices
5. Test backfill
6. Verify database records
7. Check portfolio performance

### Manual Testing

```bash
# Check how many records you have
docker compose exec postgres psql -U stockuser stockdb -c \
  "SELECT COUNT(*) FROM stock_quotes;"

# View records for AAPL
docker compose exec postgres psql -U stockuser stockdb -c \
  "SELECT * FROM stock_quotes WHERE symbol = 'AAPL' ORDER BY timestamp DESC LIMIT 10;"

# Check cache
docker compose exec redis redis-cli KEYS "stock:*"
```

## Performance

### Expected Fetching Speed

- **yfinance:** ~1-2 seconds per symbol per year
- **Alpha Vantage:** ~12 seconds per symbol (rate limited)

### Storage Requirements

- **Daily data:** ~20 bytes per record
- **1 year, 1 symbol:** ~250 records × 20 bytes = 5 KB
- **5 years, 100 symbols:** 125K records × 20 bytes = 2.5 MB
- **Very efficient** - can store decades of data

### Rate Limit Management

The system automatically:
- Tracks last request time per source
- Enforces minimum intervals between requests
- Caches aggressively to avoid repeat calls
- Provides clear feedback when rate limited

## Common Operations

### Initial Setup (New Installation)

```bash
# 1. Add your first stocks
docker compose exec api python scripts/fetch_historical_data.py \
  --symbols AAPL,GOOGL,MSFT,TSLA,AMZN \
  --years 5

# 2. Verify data
docker compose exec postgres psql -U stockuser stockdb -c \
  "SELECT symbol, COUNT(*) as records FROM stock_quotes GROUP BY symbol;"

# 3. Setup cron for daily updates
./scripts/setup_cron.sh
```

### Adding New Stocks

```bash
# Add to portfolio first (via transaction)
curl -X POST http://localhost:8000/api/v1/portfolio/1/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio_id": 1,
    "symbol": "NVDA",
    "transaction_type": "buy",
    "shares": 10,
    "price_per_share": 500.00,
    "fees": 0,
    "transaction_date": "2024-01-15T10:00:00Z"
  }'

# Fetch historical data
docker compose exec api python scripts/fetch_historical_data.py \
  --symbols NVDA \
  --years 5

# Daily updates will automatically include it
```

### Monitoring

```bash
# Check logs
tail -f /var/log/stonk-bro/daily-update.log

# Check last update time
docker compose exec postgres psql -U stockuser stockdb -c \
  "SELECT symbol, MAX(timestamp) as last_update
   FROM stock_quotes
   GROUP BY symbol
   ORDER BY last_update DESC;"
```

## Troubleshooting

### No data fetched

```bash
# Check if yfinance is working
docker compose exec api python -c "import yfinance as yf; print(yf.Ticker('AAPL').history(period='1d'))"

# Try Alpha Vantage
docker compose exec api python scripts/fetch_historical_data.py \
  --symbols AAPL \
  --source alpha_vantage \
  --years 1
```

### Rate limited

```bash
# Alpha Vantage: Wait 1 minute between requests (5 per minute)
# yfinance: Wait 1 second (automatic in code)

# Check cache to see if data is already available
docker compose exec redis redis-cli GET "stock:AAPL:history_1y_1d"
```

### Missing data gaps

```bash
# Use backfill script
docker compose exec api python scripts/backfill_data.py \
  --symbols AAPL \
  --start-date 2020-01-01
```

## API Integration

The portfolio performance endpoint automatically uses fetched data:

```bash
# Get portfolio with real-time prices from database
curl http://localhost:8000/api/v1/portfolio/1/performance
```

If data is in database, it uses that. Otherwise, it fetches live from yfinance.

## Next Steps

You can now:
- ✅ Populate historical data for any stock
- ✅ Keep data updated daily (automated)
- ✅ Fill gaps in historical records
- ✅ Track portfolio with real historical data
- ✅ Run ML predictions on historical data

### Coming Next:
- Technical indicators calculation
- News aggregation
- Sentiment analysis
- Price alerts
- ML model training on historical data
