# Portfolio API Documentation

Complete CRUD operations for managing portfolios, holdings, and transactions.

## API Endpoints

### Portfolios

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/portfolio/` | Create a new portfolio |
| GET | `/api/v1/portfolio/` | List all portfolios |
| GET | `/api/v1/portfolio/{id}` | Get specific portfolio |
| PUT | `/api/v1/portfolio/{id}` | Update portfolio |
| DELETE | `/api/v1/portfolio/{id}` | Delete portfolio (and all holdings/transactions) |
| GET | `/api/v1/portfolio/{id}/performance` | Get portfolio performance with current prices |

### Holdings

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/portfolio/{id}/holdings` | List holdings with current prices |
| POST | `/api/v1/portfolio/{id}/holdings` | Manually create holding (not recommended) |
| PUT | `/api/v1/portfolio/holdings/{id}` | Update holding |
| DELETE | `/api/v1/portfolio/holdings/{id}` | Delete holding |

### Transactions

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/portfolio/{id}/transactions` | Create transaction (BUY/SELL) - automatically updates holdings |
| GET | `/api/v1/portfolio/{id}/transactions` | List transaction history |

## Features

### ✅ Complete Portfolio Management
- Create/Read/Update/Delete portfolios
- TFSA tracking (is_tfsa flag)
- Portfolio descriptions and metadata

### ✅ Smart Transaction Handling
- **BUY transactions:**
  - Creates new holding if doesn't exist
  - Updates average cost using cost-basis method
  - Automatically calculates total amount (shares × price + fees)

- **SELL transactions:**
  - Validates sufficient shares exist
  - Reduces share count
  - Auto-deletes holding if shares = 0
  - Calculates realized gains

### ✅ Real-Time Performance
- Fetches current prices via yfinance
- Calculates:
  - Current value
  - Total cost basis
  - Gain/loss ($ and %)
  - Per-holding and total portfolio metrics

### ✅ Business Logic
- Average cost calculation on multiple buys
- Validates sell quantity against holdings
- Automatic holding creation/updates via transactions
- Transaction history tracking

## Quick Test

### 1. Start the services

```bash
cd /Users/willmcnaughton/Documents/code/stonk-bro

# Create .env from example
cp .env.example .env
nano .env  # Set DB_PASSWORD

# Start services
docker compose up -d --build

# Watch logs
docker compose logs -f api
```

### 2. Initialize database

```bash
# Create migration
docker compose exec api alembic revision --autogenerate -m "Initial schema"

# Apply migration
docker compose exec api alembic upgrade head
```

### 3. Run automated tests

```bash
./test_portfolio.sh
```

This will:
1. Create a portfolio
2. Buy 10 shares of AAPL @ $150
3. Buy 5 shares of GOOGL @ $140
4. Get holdings with current prices
5. Get portfolio performance
6. Sell 3 shares of AAPL @ $160
7. Show updated holdings and performance

### 4. Manual testing via browser

Open: http://localhost:8000/docs

Try these operations:

**Create Portfolio:**
```json
POST /api/v1/portfolio/
{
  "name": "My TFSA",
  "description": "Tax-free growth stocks",
  "is_tfsa": true
}
```

**Buy Stock:**
```json
POST /api/v1/portfolio/1/transactions
{
  "portfolio_id": 1,
  "symbol": "AAPL",
  "transaction_type": "buy",
  "shares": 10,
  "price_per_share": 150.00,
  "fees": 1.99,
  "transaction_date": "2024-01-15T10:30:00Z",
  "notes": "Initial buy"
}
```

**Get Performance:**
```
GET /api/v1/portfolio/1/performance
```

Returns:
```json
{
  "portfolio_id": 1,
  "portfolio_name": "My TFSA",
  "total_value": 1750.00,    // Current value at market prices
  "total_cost": 1501.99,     // What you paid
  "total_gain_loss": 248.01, // Profit/loss in $
  "total_gain_loss_percent": 16.52,
  "holdings_count": 1,
  "holdings": [
    {
      "symbol": "AAPL",
      "shares": 10,
      "average_cost": 150.199,
      "current_price": 175.00,
      "current_value": 1750.00,
      "total_cost": 1501.99,
      "gain_loss": 248.01,
      "gain_loss_percent": 16.52
    }
  ]
}
```

## Example Workflow

### Build a Portfolio

```bash
# 1. Create portfolio
curl -X POST http://localhost:8000/api/v1/portfolio/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Growth Portfolio",
    "is_tfsa": true
  }'
# Response: {"id": 1, "name": "Growth Portfolio", ...}

# 2. Buy some stocks
curl -X POST http://localhost:8000/api/v1/portfolio/1/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio_id": 1,
    "symbol": "AAPL",
    "transaction_type": "buy",
    "shares": 10,
    "price_per_share": 150.00,
    "fees": 1.99,
    "transaction_date": "2024-01-15T10:30:00Z"
  }'

# 3. Check performance
curl http://localhost:8000/api/v1/portfolio/1/performance | python3 -m json.tool

# 4. View transaction history
curl http://localhost:8000/api/v1/portfolio/1/transactions | python3 -m json.tool

# 5. Sell some shares
curl -X POST http://localhost:8000/api/v1/portfolio/1/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio_id": 1,
    "symbol": "AAPL",
    "transaction_type": "sell",
    "shares": 3,
    "price_per_share": 160.00,
    "fees": 1.99,
    "transaction_date": "2024-02-15T11:00:00Z"
  }'
```

## Business Logic Details

### Average Cost Calculation

When buying the same stock multiple times:

```
Example:
- Buy 10 shares @ $100 = $1000 total
- Buy 5 shares @ $110 = $550 total
- Average cost = ($1000 + $550) / 15 shares = $103.33
```

The system automatically calculates and updates this on each BUY transaction.

### Sell Validation

```python
# System checks:
1. Does holding exist?
2. Do you have enough shares?
3. Updates share count
4. Removes holding if shares = 0
```

### Performance Metrics

```python
# Calculated in real-time:
current_value = shares × current_price
total_cost = shares × average_cost
gain_loss = current_value - total_cost
gain_loss_percent = (gain_loss / total_cost) × 100
```

## Database Schema

### portfolios
- id, name, description, is_tfsa, created_at, updated_at

### portfolio_holdings
- id, portfolio_id, symbol, shares, average_cost, created_at, updated_at

### transactions
- id, portfolio_id, symbol, transaction_type, shares, price_per_share
- total_amount, fees, transaction_date, notes, created_at

## Next Steps

You can now:
- ✅ Track multiple portfolios (TFSA, non-registered, etc.)
- ✅ Record all buy/sell transactions
- ✅ View real-time portfolio value
- ✅ Calculate gains/losses
- ✅ Track transaction history

### Coming Next:
- TFSA contribution room tracking
- Dividend transactions
- Stock splits handling
- Performance charts
- Tax reporting
- Alerts on holdings
