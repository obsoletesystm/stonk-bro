"""Email utility functions"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os


def send_email(
    to_email: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None
) -> bool:
    """
    Send an email using SMTP

    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Plain text email body
        html_body: Optional HTML email body

    Returns:
        True if email sent successfully, False otherwise
    """
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    # Check if email is configured
    if not all([smtp_host, smtp_user, smtp_password]):
        print("Email not configured. Set SMTP_HOST, SMTP_USER, and SMTP_PASSWORD in .env")
        return False

    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = smtp_user
        msg['To'] = to_email
        msg['Subject'] = subject

        # Attach text body
        text_part = MIMEText(body, 'plain')
        msg.attach(text_part)

        # Attach HTML body if provided
        if html_body:
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)

        # Send email
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        print(f"Email sent successfully to {to_email}")
        return True

    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def send_alert_notification(
    alert_id: int,
    symbol: str,
    condition: str,
    threshold: float,
    current_price: Optional[float] = None,
    current_sentiment: Optional[float] = None,
    article_count: Optional[int] = None,
    message: Optional[str] = None,
    alert_type: str = "price"
) -> bool:
    """
    Send alert notification email

    Args:
        alert_id: Alert ID
        symbol: Stock symbol
        condition: Alert condition type
        threshold: Threshold value
        current_price: Current price (for price alerts)
        current_sentiment: Current sentiment score (for news alerts)
        article_count: Number of articles (for news alerts)
        message: Optional custom message
        alert_type: Type of alert ("price" or "news")

    Returns:
        True if email sent successfully, False otherwise
    """
    alert_email = os.getenv("ALERT_EMAIL")
    if not alert_email:
        print("ALERT_EMAIL not configured in .env")
        return False

    # Normalize condition to lowercase for lookup
    condition_lower = condition.lower()

    # Format condition text based on alert type
    if alert_type == "news":
        condition_text = {
            "sentiment_above": f"Sentiment above {threshold:.2f}",
            "sentiment_below": f"Sentiment below {threshold:.2f}",
            "sentiment_change": f"Sentiment changed by {threshold:.2%}",
            "news_volume_spike": f"News volume spiked above {threshold}x normal"
        }.get(condition_lower, condition)

        emoji = "📰"

    else:  # price alert
        condition_text = {
            "price_above": f"Price above ${threshold:.2f}",
            "price_below": f"Price below ${threshold:.2f}",
            "price_change_percent": f"Price changed by {threshold}%",
            "volume_above": f"Volume above {threshold:,.0f}"
        }.get(condition_lower, condition)

        emoji = "🚨"

    subject = f"{emoji} Alert Triggered: {symbol} - {condition_text}"

    # Build plain text body
    if alert_type == "news":
        body = f"""
News Alert Triggered!

Symbol: {symbol}
Condition: {condition_text}
Current Sentiment: {current_sentiment:.3f} ({_sentiment_label(current_sentiment)})
Articles Analyzed: {article_count}
Alert ID: {alert_id}
"""
    else:
        body = f"""
Alert Triggered!

Symbol: {symbol}
Condition: {condition_text}
Current Price: ${current_price:.2f}
Alert ID: {alert_id}
"""

    if message:
        body += f"\nYour Note: {message}"

    body += """

---
Stonk Bro Alert System
"""

    # Build HTML body
    if alert_type == "news":
        sentiment_color = "#2e7d32" if current_sentiment > 0 else "#d32f2f" if current_sentiment < 0 else "#666"
        html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; padding: 20px;">
    <h2 style="color: #1976d2;">{emoji} News Alert Triggered!</h2>

    <table style="border-collapse: collapse; margin: 20px 0;">
        <tr>
            <td style="padding: 8px; font-weight: bold;">Symbol:</td>
            <td style="padding: 8px;">{symbol}</td>
        </tr>
        <tr style="background-color: #f5f5f5;">
            <td style="padding: 8px; font-weight: bold;">Condition:</td>
            <td style="padding: 8px;">{condition_text}</td>
        </tr>
        <tr>
            <td style="padding: 8px; font-weight: bold;">Current Sentiment:</td>
            <td style="padding: 8px; color: {sentiment_color}; font-weight: bold;">
                {current_sentiment:.3f} ({_sentiment_label(current_sentiment)})
            </td>
        </tr>
        <tr style="background-color: #f5f5f5;">
            <td style="padding: 8px; font-weight: bold;">Articles Analyzed:</td>
            <td style="padding: 8px;">{article_count}</td>
        </tr>
        <tr>
            <td style="padding: 8px; font-weight: bold;">Alert ID:</td>
            <td style="padding: 8px;">{alert_id}</td>
        </tr>
    </table>
"""
    else:
        html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; padding: 20px;">
    <h2 style="color: #d32f2f;">{emoji} Alert Triggered!</h2>

    <table style="border-collapse: collapse; margin: 20px 0;">
        <tr>
            <td style="padding: 8px; font-weight: bold;">Symbol:</td>
            <td style="padding: 8px;">{symbol}</td>
        </tr>
        <tr style="background-color: #f5f5f5;">
            <td style="padding: 8px; font-weight: bold;">Condition:</td>
            <td style="padding: 8px;">{condition_text}</td>
        </tr>
        <tr>
            <td style="padding: 8px; font-weight: bold;">Current Price:</td>
            <td style="padding: 8px; color: #2e7d32; font-weight: bold;">${current_price:.2f}</td>
        </tr>
        <tr style="background-color: #f5f5f5;">
            <td style="padding: 8px; font-weight: bold;">Alert ID:</td>
            <td style="padding: 8px;">{alert_id}</td>
        </tr>
    </table>
"""

    if message:
        html_body += f"""
    <div style="margin: 20px 0; padding: 15px; background-color: #fff3cd; border-left: 4px solid #ffc107;">
        <strong>Your Note:</strong><br>
        {message}
    </div>
"""

    html_body += """
    <hr style="margin: 30px 0; border: none; border-top: 1px solid #ccc;">
    <p style="color: #666; font-size: 12px;">
        Stonk Bro Alert System<br>
        This is an automated notification. Do not reply to this email.
    </p>
</body>
</html>
"""

    return send_email(alert_email, subject, body, html_body)


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
