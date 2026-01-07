#!/bin/bash
#
# Test script for Portfolio API
# Run after: docker compose up -d && docker compose exec api alembic upgrade head
#

set -e

API_URL="http://localhost:8000/api/v1"

echo "=== Testing Portfolio API ==="
echo ""

# Test 1: Create a portfolio
echo "1. Creating portfolio..."
PORTFOLIO_RESPONSE=$(curl -s -X POST "$API_URL/portfolio/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My TFSA Portfolio",
    "description": "Long-term growth stocks",
    "is_tfsa": true
  }')

PORTFOLIO_ID=$(echo $PORTFOLIO_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "✓ Created portfolio ID: $PORTFOLIO_ID"
echo ""

# Test 2: Get all portfolios
echo "2. Getting all portfolios..."
curl -s "$API_URL/portfolio/" | python3 -m json.tool
echo ""

# Test 3: Create a transaction (buy)
echo "3. Creating BUY transaction for AAPL..."
curl -s -X POST "$API_URL/portfolio/$PORTFOLIO_ID/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio_id": '$PORTFOLIO_ID',
    "symbol": "AAPL",
    "transaction_type": "buy",
    "shares": 10,
    "price_per_share": 150.00,
    "fees": 1.99,
    "transaction_date": "2024-01-15T10:30:00Z",
    "notes": "Initial purchase"
  }' | python3 -m json.tool
echo ""

# Test 4: Create another transaction (buy different stock)
echo "4. Creating BUY transaction for GOOGL..."
curl -s -X POST "$API_URL/portfolio/$PORTFOLIO_ID/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio_id": '$PORTFOLIO_ID',
    "symbol": "GOOGL",
    "transaction_type": "buy",
    "shares": 5,
    "price_per_share": 140.00,
    "fees": 1.99,
    "transaction_date": "2024-01-20T14:30:00Z",
    "notes": "Diversification"
  }' | python3 -m json.tool
echo ""

# Test 5: Get holdings
echo "5. Getting portfolio holdings..."
curl -s "$API_URL/portfolio/$PORTFOLIO_ID/holdings" | python3 -m json.tool
echo ""

# Test 6: Get portfolio performance
echo "6. Getting portfolio performance..."
curl -s "$API_URL/portfolio/$PORTFOLIO_ID/performance" | python3 -m json.tool
echo ""

# Test 7: Get transactions
echo "7. Getting transaction history..."
curl -s "$API_URL/portfolio/$PORTFOLIO_ID/transactions" | python3 -m json.tool
echo ""

# Test 8: Create a SELL transaction
echo "8. Creating SELL transaction for AAPL..."
curl -s -X POST "$API_URL/portfolio/$PORTFOLIO_ID/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio_id": '$PORTFOLIO_ID',
    "symbol": "AAPL",
    "transaction_type": "sell",
    "shares": 3,
    "price_per_share": 160.00,
    "fees": 1.99,
    "transaction_date": "2024-02-15T11:00:00Z",
    "notes": "Taking profits"
  }' | python3 -m json.tool
echo ""

# Test 9: Get updated holdings
echo "9. Getting updated holdings after sell..."
curl -s "$API_URL/portfolio/$PORTFOLIO_ID/holdings" | python3 -m json.tool
echo ""

# Test 10: Get updated performance
echo "10. Getting updated performance..."
curl -s "$API_URL/portfolio/$PORTFOLIO_ID/performance" | python3 -m json.tool
echo ""

echo "=== Tests Complete ==="
echo ""
echo "Portfolio ID: $PORTFOLIO_ID"
echo "To view in browser: http://localhost:8000/docs"
