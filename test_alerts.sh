#!/bin/bash
#
# Test alert system
#

set -e

API_URL="http://localhost:8000/api/v1"

echo "=== Testing Alert System ==="
echo ""

# Test 1: Create alerts
echo "1. Creating test alerts..."

# Alert: AAPL price above $150
ALERT1=$(curl -s -X POST "$API_URL/alerts/" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "condition": "price_above",
    "threshold_value": 150.0,
    "message": "AAPL broke above $150!"
  }')

ALERT1_ID=$(echo $ALERT1 | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "✓ Created alert #$ALERT1_ID: AAPL price above \$150"

# Alert: GOOGL price below $200
ALERT2=$(curl -s -X POST "$API_URL/alerts/" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "GOOGL",
    "condition": "price_below",
    "threshold_value": 200.0,
    "message": "GOOGL dropped below $200"
  }')

ALERT2_ID=$(echo $ALERT2 | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "✓ Created alert #$ALERT2_ID: GOOGL price below \$200"

# Alert: MSFT volume above 1 million
ALERT3=$(curl -s -X POST "$API_URL/alerts/" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "MSFT",
    "condition": "volume_above",
    "threshold_value": 1000000,
    "message": "High volume on MSFT"
  }')

ALERT3_ID=$(echo $ALERT3 | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "✓ Created alert #$ALERT3_ID: MSFT volume above 1M"

# Test 2: List all alerts
echo ""
echo "2. Listing all alerts..."
curl -s "$API_URL/alerts/" | python3 -m json.tool | head -30

# Test 3: Get specific alert
echo ""
echo "3. Getting alert #$ALERT1_ID details..."
curl -s "$API_URL/alerts/$ALERT1_ID" | python3 -m json.tool

# Test 4: List active alerts
echo ""
echo "4. Listing active alerts..."
ACTIVE=$(curl -s "$API_URL/alerts/active")
ACTIVE_COUNT=$(echo $ACTIVE | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
echo "✓ Found $ACTIVE_COUNT active alerts"

# Test 5: Filter by symbol
echo ""
echo "5. Filtering alerts by symbol (AAPL)..."
curl -s "$API_URL/alerts/?symbol=AAPL" | python3 -m json.tool

# Test 6: Update alert
echo ""
echo "6. Updating alert #$ALERT1_ID..."
curl -s -X PUT "$API_URL/alerts/$ALERT1_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "threshold_value": 155.0,
    "message": "AAPL broke above $155! (updated)"
  }' | python3 -m json.tool

# Test 7: Check alerts manually (dry run)
echo ""
echo "7. Testing alert checking (may hit rate limits)..."
echo "Note: This checks current prices and may trigger alerts if conditions are met"
echo ""

# Use the script for dry run
docker compose exec -T api python scripts/check_alerts.py --dry-run

# Test 8: Manually trigger alert check via API
echo ""
echo "8. Triggering manual alert check via API..."
curl -s -X POST "$API_URL/alerts/check" | python3 -m json.tool

# Test 9: Get alert history
echo ""
echo "9. Checking alert history for alert #$ALERT1_ID..."
curl -s "$API_URL/alerts/$ALERT1_ID/history" | python3 -m json.tool

# Test 10: Delete an alert
echo ""
echo "10. Deleting alert #$ALERT3_ID..."
curl -s -X DELETE "$API_URL/alerts/$ALERT3_ID"
echo "✓ Alert deleted"

# Verify deletion
echo ""
echo "11. Verifying deletion..."
REMAINING=$(curl -s "$API_URL/alerts/active")
REMAINING_COUNT=$(echo $REMAINING | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
echo "✓ Active alerts remaining: $REMAINING_COUNT"

echo ""
echo "=== Alert System Tests Complete ==="
echo ""
echo "Alert endpoints available:"
echo "  POST   /api/v1/alerts/              - Create alert"
echo "  GET    /api/v1/alerts/              - List alerts"
echo "  GET    /api/v1/alerts/active        - List active alerts"
echo "  GET    /api/v1/alerts/{id}          - Get alert with history"
echo "  PUT    /api/v1/alerts/{id}          - Update alert"
echo "  DELETE /api/v1/alerts/{id}          - Delete alert"
echo "  GET    /api/v1/alerts/{id}/history  - Get alert history"
echo "  POST   /api/v1/alerts/check         - Manually check alerts"
echo ""
echo "To check alerts via cron script:"
echo "  docker compose exec api python scripts/check_alerts.py"
echo "  docker compose exec api python scripts/check_alerts.py --dry-run"
