"""Discord notification utility functions"""
import os
import requests
from typing import Optional
from datetime import datetime


def send_discord_webhook(
    webhook_url: str,
    content: Optional[str] = None,
    embeds: Optional[list] = None
) -> bool:
    """
    Send a message to Discord via webhook

    Args:
        webhook_url: Discord webhook URL
        content: Simple text message
        embeds: List of embed objects for rich messages

    Returns:
        True if message sent successfully, False otherwise
    """
    try:
        payload = {}

        if content:
            payload['content'] = content

        if embeds:
            payload['embeds'] = embeds

        response = requests.post(
            webhook_url,
            json=payload,
            timeout=10
        )

        if response.status_code in [200, 204]:
            print(f"Discord webhook sent successfully")
            return True
        else:
            print(f"Discord webhook failed: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"Failed to send Discord webhook: {e}")
        return False


def send_price_alert_discord(
    alert_id: int,
    symbol: str,
    condition: str,
    threshold: float,
    current_price: float,
    message: Optional[str] = None
) -> bool:
    """
    Send price alert notification to Discord

    Args:
        alert_id: Alert ID
        symbol: Stock symbol
        condition: Alert condition type
        threshold: Threshold value
        current_price: Current price that triggered alert
        message: Optional custom message

    Returns:
        True if notification sent successfully, False otherwise
    """
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("DISCORD_WEBHOOK_URL not configured in .env")
        return False

    # Format condition nicely
    condition_lower = condition.lower()
    condition_text_map = {
        "price_above": f"Price above ${threshold:.2f}",
        "price_below": f"Price below ${threshold:.2f}",
        "price_change_percent": f"Price changed by {threshold}%",
        "volume_above": f"Volume above {threshold:,.0f}"
    }
    condition_text = condition_text_map.get(condition_lower, condition)

    # Determine color based on condition
    if "above" in condition_lower or "change" in condition_lower:
        color = 0x2ecc71  # Green
    elif "below" in condition_lower:
        color = 0xe74c3c  # Red
    else:
        color = 0x3498db  # Blue

    # Create Discord embed
    embed = {
        "title": f"🚨 Price Alert Triggered: {symbol}",
        "description": f"**{condition_text}**",
        "color": color,
        "fields": [
            {
                "name": "Symbol",
                "value": symbol,
                "inline": True
            },
            {
                "name": "Current Price",
                "value": f"${current_price:.2f}",
                "inline": True
            },
            {
                "name": "Threshold",
                "value": f"${threshold:.2f}",
                "inline": True
            },
            {
                "name": "Alert ID",
                "value": str(alert_id),
                "inline": True
            }
        ],
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {
            "text": "Stonk Bro Alert System"
        }
    }

    # Add custom message if provided
    if message:
        embed["fields"].insert(0, {
            "name": "📝 Your Note",
            "value": message,
            "inline": False
        })

    return send_discord_webhook(webhook_url, embeds=[embed])


def send_news_alert_discord(
    alert_id: int,
    symbol: str,
    condition: str,
    threshold: float,
    current_sentiment: float,
    article_count: int,
    message: Optional[str] = None
) -> bool:
    """
    Send news alert notification to Discord

    Args:
        alert_id: Alert ID
        symbol: Stock symbol
        condition: Alert condition type
        threshold: Threshold value
        current_sentiment: Current sentiment score
        article_count: Number of articles analyzed
        message: Optional custom message

    Returns:
        True if notification sent successfully, False otherwise
    """
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("DISCORD_WEBHOOK_URL not configured in .env")
        return False

    # Format condition nicely
    condition_lower = condition.lower()
    condition_text_map = {
        "sentiment_above": f"Sentiment above {threshold:.2f}",
        "sentiment_below": f"Sentiment below {threshold:.2f}",
        "sentiment_change": f"Sentiment changed by {threshold:.2%}",
        "news_volume_spike": f"News volume spiked above {threshold}x normal"
    }
    condition_text = condition_text_map.get(condition_lower, condition)

    # Get sentiment label and color
    sentiment_label = _sentiment_label(current_sentiment)

    if current_sentiment >= 0.1:
        color = 0x2ecc71  # Green for positive
        emoji = "📈"
    elif current_sentiment <= -0.1:
        color = 0xe74c3c  # Red for negative
        emoji = "📉"
    else:
        color = 0x95a5a6  # Gray for neutral
        emoji = "➡️"

    # Create Discord embed
    embed = {
        "title": f"📰 News Alert Triggered: {symbol}",
        "description": f"**{condition_text}**",
        "color": color,
        "fields": [
            {
                "name": "Symbol",
                "value": symbol,
                "inline": True
            },
            {
                "name": "Current Sentiment",
                "value": f"{emoji} {current_sentiment:.3f} ({sentiment_label})",
                "inline": True
            },
            {
                "name": "Articles Analyzed",
                "value": str(article_count),
                "inline": True
            },
            {
                "name": "Threshold",
                "value": f"{threshold:.3f}",
                "inline": True
            },
            {
                "name": "Alert ID",
                "value": str(alert_id),
                "inline": True
            }
        ],
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {
            "text": "Stonk Bro Alert System"
        }
    }

    # Add custom message if provided
    if message:
        embed["fields"].insert(0, {
            "name": "📝 Your Note",
            "value": message,
            "inline": False
        })

    return send_discord_webhook(webhook_url, embeds=[embed])


def _sentiment_label(score: float) -> str:
    """Get human-readable sentiment label"""
    if score >= 0.3:
        return "Very Positive"
    elif score >= 0.1:
        return "Positive"
    elif score >= -0.1:
        return "Neutral"
    elif score >= -0.3:
        return "Negative"
    else:
        return "Very Negative"
