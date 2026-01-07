"""Alert models"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.db import Base
import enum


class AlertCondition(str, enum.Enum):
    """Alert condition types"""
    PRICE_ABOVE = "PRICE_ABOVE"
    PRICE_BELOW = "PRICE_BELOW"
    PRICE_CHANGE_PERCENT = "PRICE_CHANGE_PERCENT"
    VOLUME_ABOVE = "VOLUME_ABOVE"
    # News & Sentiment conditions
    SENTIMENT_ABOVE = "SENTIMENT_ABOVE"
    SENTIMENT_BELOW = "SENTIMENT_BELOW"
    SENTIMENT_CHANGE = "SENTIMENT_CHANGE"
    NEWS_VOLUME_SPIKE = "NEWS_VOLUME_SPIKE"


class AlertStatus(str, enum.Enum):
    """Alert status"""
    ACTIVE = "active"
    TRIGGERED = "triggered"
    DISABLED = "disabled"


class Alert(Base):
    """Price and condition alerts"""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), nullable=False, index=True)
    condition = Column(SQLEnum(AlertCondition), nullable=False)
    threshold_value = Column(Float, nullable=False)
    status = Column(SQLEnum(AlertStatus), default=AlertStatus.ACTIVE)
    message = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    triggered_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    history = relationship("AlertHistory", back_populates="alert", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Alert {self.symbol} {self.condition} {self.threshold_value}>"


class AlertHistory(Base):
    """Alert trigger history"""
    __tablename__ = "alert_history"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=False)
    triggered_at = Column(DateTime(timezone=True), server_default=func.now())
    price_at_trigger = Column(Float, nullable=True)  # Nullable for news alerts
    notification_sent = Column(Boolean, default=False)

    # News & Sentiment trigger data
    sentiment_at_trigger = Column(Float, nullable=True)
    articles_count = Column(Integer, nullable=True)
    trigger_details = Column(String(1000), nullable=True)  # JSON string for additional details

    # Relationships
    alert = relationship("Alert", back_populates="history")

    def __repr__(self):
        return f"<AlertHistory {self.alert_id} @ {self.triggered_at}>"
