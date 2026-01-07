#!/bin/bash
#
# Setup cron jobs for Stonk Bro
#
# Usage: ./scripts/setup_cron.sh
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CRON_FILE="$PROJECT_DIR/cron/stonk-bro-cron"
LOG_DIR="/var/log/stonk-bro"

echo "=== Setting up Stonk Bro Cron Jobs ==="
echo ""
echo "Project directory: $PROJECT_DIR"
echo "Cron file: $CRON_FILE"
echo "Log directory: $LOG_DIR"
echo ""

# Create log directory
if [ ! -d "$LOG_DIR" ]; then
    echo "Creating log directory..."
    sudo mkdir -p "$LOG_DIR"
    sudo chown $USER:$USER "$LOG_DIR"
    echo "✓ Created $LOG_DIR"
else
    echo "✓ Log directory exists: $LOG_DIR"
fi

# Update paths in cron file
echo ""
echo "Updating paths in cron file..."
TEMP_CRON=$(mktemp)
sed "s|STONK_DIR=.*|STONK_DIR=$PROJECT_DIR|g" "$CRON_FILE" | \
sed "s|LOG_DIR=.*|LOG_DIR=$LOG_DIR|g" > "$TEMP_CRON"

echo "✓ Paths updated"

# Show what will be installed
echo ""
echo "=== Cron jobs to be installed ==="
echo ""
grep -v "^#" "$TEMP_CRON" | grep -v "^$" || true
echo ""

# Ask for confirmation
read -p "Install these cron jobs? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Installation cancelled"
    rm "$TEMP_CRON"
    exit 0
fi

# Install cron jobs
echo ""
echo "Installing cron jobs..."
crontab "$TEMP_CRON"
rm "$TEMP_CRON"

echo "✓ Cron jobs installed"

# Verify installation
echo ""
echo "=== Installed cron jobs ==="
crontab -l | grep -v "^#" | grep -v "^$" || true

echo ""
echo "✓ Setup complete!"
echo ""
echo "To view cron jobs: crontab -l"
echo "To edit cron jobs: crontab -e"
echo "To view logs: tail -f $LOG_DIR/*.log"
