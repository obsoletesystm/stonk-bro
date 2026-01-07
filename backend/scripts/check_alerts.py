#!/usr/bin/env python3
"""
Check price alerts and send notifications

This script checks all active alerts and triggers/notifies when conditions are met.

Usage:
    python scripts/check_alerts.py
    python scripts/check_alerts.py --dry-run  # Don't send emails, just check
"""
import argparse
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import SessionLocal
from app.services.alert_service import AlertService
from app.utils.email import send_alert_notification


def main():
    parser = argparse.ArgumentParser(description="Check price alerts")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Check alerts but don't send notifications"
    )

    args = parser.parse_args()

    print(f"=== Checking Alerts ({datetime.now()}) ===")
    if args.dry_run:
        print("DRY RUN MODE - No notifications will be sent")
    print("")

    db = SessionLocal()

    try:
        # Check all active alerts
        triggered = AlertService.check_all_active_alerts(db)

        print(f"Active alerts checked: ✓")
        print(f"Triggered alerts: {len(triggered)}")
        print("")

        if not triggered:
            print("No alerts triggered")
            return

        # Process each triggered alert
        for i, alert_info in enumerate(triggered, 1):
            print(f"[{i}/{len(triggered)}] Alert #{alert_info['alert_id']}")
            print(f"  Symbol: {alert_info['symbol']}")
            print(f"  Condition: {alert_info['condition']}")
            print(f"  Threshold: {alert_info['threshold']}")
            print(f"  Current Price: ${alert_info['current_price']:.2f}")

            if alert_info['message']:
                print(f"  Note: {alert_info['message']}")

            if not args.dry_run:
                # Send email notification
                success = send_alert_notification(
                    alert_id=alert_info['alert_id'],
                    symbol=alert_info['symbol'],
                    condition=alert_info['condition'],
                    threshold=alert_info['threshold'],
                    current_price=alert_info['current_price'],
                    message=alert_info['message']
                )

                if success:
                    print(f"  ✓ Notification sent")
                    # Mark as sent
                    AlertService.mark_notification_sent(db, alert_info['history_id'])
                else:
                    print(f"  ✗ Failed to send notification")
            else:
                print(f"  [DRY RUN] Would send notification")

            print("")

        print("=== Summary ===")
        print(f"Triggered: {len(triggered)}")
        if not args.dry_run:
            print(f"Notifications sent successfully")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        db.close()


if __name__ == "__main__":
    main()
