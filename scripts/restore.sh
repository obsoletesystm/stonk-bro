#!/bin/bash
#
# Restore script for Stonk Bro
# Usage: ./scripts/restore.sh <backup_file>
#

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file.sql.gz>"
    echo ""
    echo "Available backups:"
    ls -lh /backups/stonk-bro/*.sql.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "=== Stonk Bro Restore ==="
echo "Backup file: $BACKUP_FILE"
echo ""
echo "WARNING: This will replace all data in the database!"
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled"
    exit 0
fi

echo ""
echo "Stopping application..."
docker compose stop api celery-worker

echo "Restoring database..."
gunzip < "$BACKUP_FILE" | docker compose exec -T postgres psql -U stockuser stockdb

if [ $? -eq 0 ]; then
    echo "✓ Restore successful"
else
    echo "✗ Restore failed"
    exit 1
fi

echo ""
echo "Starting application..."
docker compose start api celery-worker

echo "✓ Restore complete"
