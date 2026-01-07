"""Alert schemas"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.alert import AlertCondition, AlertStatus


class AlertBase(BaseModel):
    """Base alert schema"""
    symbol: str = Field(..., min_length=1, max_length=10, description="Stock symbol")
    condition: AlertCondition = Field(..., description="Alert condition type")
    threshold_value: float = Field(..., description="Threshold value for alert")
    message: Optional[str] = Field(None, max_length=500, description="Custom alert message")


class AlertCreate(AlertBase):
    """Schema for creating an alert"""
    pass


class AlertUpdate(BaseModel):
    """Schema for updating an alert"""
    condition: Optional[AlertCondition] = None
    threshold_value: Optional[float] = Field(None, gt=0)
    status: Optional[AlertStatus] = None
    message: Optional[str] = Field(None, max_length=500)


class AlertResponse(AlertBase):
    """Schema for alert response"""
    id: int
    status: AlertStatus
    created_at: datetime
    triggered_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AlertHistoryResponse(BaseModel):
    """Schema for alert history response"""
    id: int
    alert_id: int
    triggered_at: datetime
    price_at_trigger: Optional[float] = None
    notification_sent: bool
    # News alert fields
    sentiment_at_trigger: Optional[float] = None
    articles_count: Optional[int] = None
    trigger_details: Optional[str] = None

    class Config:
        from_attributes = True


class AlertWithHistory(AlertResponse):
    """Alert with full trigger history"""
    history: list[AlertHistoryResponse] = []

    class Config:
        from_attributes = True
