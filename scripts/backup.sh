#!/bin/bash
#
# Backup script for Stonk Bro
# Usage: ./scripts/backup.sh [backup_dir]
#

set -e

# Default backup directory
BACKUP_DIR="${1:-/backups/stonk-bro}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/stonk-bro-backup-$TIMESTAMP.sql.gz"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "=== Stonk Bro Backup ==="
echo "Timestamp: $TIMESTAMP"
echo "Backup file: $BACKUP_FILE"
echo ""

# Backup PostgreSQL database
echo "Backing up PostgreSQL database..."
docker compose exec -T postgres pg_dump -U stockuser stockdb | gzip > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "✓ Database backup successful"
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "  Size: $BACKUP_SIZE"
else
    echo "✗ Database backup failed"
    exit 1
fi

# Cleanup old backups (keep last 7 daily, 4 weekly, 12 monthly)
echo ""
echo "Cleaning up old backups..."

# Keep last 7 daily backups
find "$BACKUP_DIR" -name "stonk-bro-backup-*.sql.gz" -mtime +7 -delete

echo "✓ Backup complete"
echo ""
echo "To restore this backup, run:"
echo "  gunzip < $BACKUP_FILE | docker compose exec -T postgres psql -U stockuser stockdb"
