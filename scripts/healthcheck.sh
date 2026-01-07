#!/bin/bash
#
# Health check script for Stonk Bro
# Checks all services and reports status
#

set -e

echo "=== Stonk Bro Health Check ==="
echo ""

# Check if containers are running
echo "Container Status:"
docker compose ps

echo ""
echo "=== Service Health ==="

# Check API health
echo -n "API: "
if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ Healthy"
else
    echo "✗ Unhealthy"
fi

# Check PostgreSQL
echo -n "PostgreSQL: "
if docker compose exec -T postgres pg_isready -U stockuser > /dev/null 2>&1; then
    echo "✓ Healthy"
else
    echo "✗ Unhealthy"
fi

# Check Redis
echo -n "Redis: "
if docker compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✓ Healthy"
else
    echo "✗ Unhealthy"
fi

# Check detailed health endpoint
echo ""
echo "=== Detailed Health Check ==="
curl -s http://localhost:8000/api/v1/health/detailed | python3 -m json.tool

# Resource usage
echo ""
echo "=== Resource Usage ==="
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
