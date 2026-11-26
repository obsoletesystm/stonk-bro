#!/bin/bash
#
# Hourly data collection script for Stock Research Platform
#
# This script triggers the Celery task to collect data from all sources
# (Reddit, News). Designed to be run via cron every hour.
#
# Usage: ./scripts/collect_hourly.sh
#
# Cron example (every hour):
# 0 * * * * /path/to/stonk-bro/scripts/collect_hourly.sh >> /var/log/stonk-bro/cron.log 2>&1

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="${LOG_DIR:-/var/log/stonk-bro}"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Log function
log() {
    echo "[${TIMESTAMP}] $1" | tee -a "${LOG_DIR}/collect.log"
}

# Error handler
error_exit() {
    log "ERROR: $1"
    exit 1
}

log "=========================================="
log "Starting hourly data collection"
log "=========================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    error_exit "Docker is not running"
fi

# Check if containers are running
cd "$PROJECT_ROOT"

if ! docker compose ps | grep -q "stonk-bro-api"; then
    error_exit "API container is not running. Start with: docker compose up -d"
fi

if ! docker compose ps | grep -q "stonk-bro-celery-worker"; then
    error_exit "Celery worker container is not running. Start with: docker compose up -d"
fi

log "Docker containers are running"

# Trigger data collection via Celery task
# Queues each collector as its own task (no task waits on another)
log "Triggering data collection task..."

TASK_OUTPUT=$(docker compose exec -T api python -c "
from app.tasks.sentiment_tasks import (
    collect_reddit_content_task, collect_news_content_task)
for t in (collect_reddit_content_task, collect_news_content_task):
    r = t.delay()
    print(f'{t.name}: Task ID {r.id}')
" 2>&1)

if [ $? -eq 0 ]; then
    log "Data collection task triggered successfully"
    log "$TASK_OUTPUT"
else
    error_exit "Failed to trigger data collection task: $TASK_OUTPUT"
fi

# Wait a moment for task to start
sleep 2

# Check task status
log "Checking task execution..."

TASK_CHECK=$(docker compose exec -T api python -c "
from app.core.db import SessionLocal
from app.models.sentiment import RawContent, SourceType
from datetime import datetime, timedelta

db = SessionLocal()

# Count recent content (last hour)
cutoff = datetime.utcnow() - timedelta(hours=1)

reddit_count = db.query(RawContent).filter(
    RawContent.source == SourceType.REDDIT.value,
    RawContent.collected_at >= cutoff
).count()

news_count = db.query(RawContent).filter(
    RawContent.source == SourceType.NEWS.value,
    RawContent.collected_at >= cutoff
).count()

print(f'Reddit content (last hour): {reddit_count}')
print(f'News content (last hour): {news_count}')
print(f'Total content (last hour): {reddit_count + news_count}')

db.close()
" 2>&1)

if [ $? -eq 0 ]; then
    log "$TASK_CHECK"
else
    log "WARNING: Could not check task status: $TASK_CHECK"
fi

log "=========================================="
log "Hourly data collection completed"
log "=========================================="

exit 0
