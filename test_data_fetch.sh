#!/bin/bash
#
# Test data fetching scripts
# Run after: docker compose up -d && migrations applied
#

set -e

API_URL="http://localhost:8000/api/v1"

echo "=== Testing Data Fetching ==="
echo ""

# Test 1: Create a portfolio with holdings first
echo "1. Setting up test portfolio..."
PORTFOLIO_RESPONSE=$(curl -s -X POST "$API_URL/portfolio/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Data Fetch Portfolio",
    "is_tfsa": true
  }')

PORTFOLIO_ID=$(echo $PORTFOLIO_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "✓ Created portfolio ID: $PORTFOLIO_ID"

# Add holdings
echo ""
echo "2. Adding holdings (AAPL, GOOGL, MSFT)..."
curl -s -X POST "$API_URL/portfolio/$PORTFOLIO_ID/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio_id": '$PORTFOLIO_ID',
    "symbol": "AAPL",
    "transaction_type": "buy",
    "shares": 10,
    "price_per_share": 150.00,
    "fees": 0,
    "transaction_date": "2024-01-15T10:00:00Z"
  }' > /dev/null

curl -s -X POST "$API_URL/portfolio/$PORTFOLIO_ID/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio_id": '$PORTFOLIO_ID',
    "symbol": "GOOGL",
    "transaction_type": "buy",
    "shares": 5,
    "price_per_share": 140.00,
    "fees": 0,
    "transaction_date": "2024-01-15T10:00:00Z"
  }' > /dev/null

curl -s -X POST "$API_URL/portfolio/$PORTFOLIO_ID/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio_id": '$PORTFOLIO_ID',
    "symbol": "MSFT",
    "transaction_type": "buy",
    "shares": 8,
    "price_per_share": 380.00,
    "fees": 0,
    "transaction_date": "2024-01-15T10:00:00Z"
  }' > /dev/null

echo "✓ Added holdings"

# Test 3: Fetch historical data for specific symbols
echo ""
echo "3. Fetching 1 month of historical data for AAPL..."
docker compose exec -T api python scripts/fetch_historical_data.py \
  --symbols AAPL \
  --period 1mo

# Test 4: Fetch data for all portfolio holdings
echo ""
echo "4. Fetching 3 months of data for all portfolio holdings..."
docker compose exec -T api python scripts/fetch_historical_data.py \
  --from-portfolio \
  --period 3mo

# Test 5: Check database
echo ""
echo "5. Checking database records..."
docker compose exec -T postgres psql -U stockuser stockdb -c \
  "SELECT symbol, COUNT(*) as records, MIN(timestamp) as earliest, MAX(timestamp) as latest
   FROM stock_quotes
   GROUP BY symbol
   ORDER BY symbol;"

# Test 6: Update daily prices
echo ""
echo "6. Testing daily price update..."
docker compose exec -T api python scripts/update_daily_prices.py

# Test 7: Backfill test
echo ""
echo "7. Testing backfill (should fill any gaps)..."
docker compose exec -T api python scripts/backfill_data.py \
  --symbols AAPL \
  --start-date 2024-01-01

# Test 8: Verify portfolio performance uses real data
echo ""
echo "8. Getting portfolio performance (should use fetched data)..."
curl -s "$API_URL/portfolio/$PORTFOLIO_ID/performance" | python3 -m json.tool

echo ""
echo "=== Data Fetch Tests Complete ==="
echo ""
echo "To manually test scripts:"
echo "  docker compose exec api python scripts/fetch_historical_data.py --help"
echo "  docker compose exec api python scripts/update_daily_prices.py --help"
echo "  docker compose exec api python scripts/backfill_data.py --help"
echo ""
echo "To check database:"
echo "  docker compose exec postgres psql -U stockuser stockdb"
echo "  SELECT COUNT(*) FROM stock_quotes;"
