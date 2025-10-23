from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from ..models.subscription import SubscriptionFrequency

# Subscription Schemas
class EmailSubscriptionBase(BaseModel):
    dashboard_id: str
    frequency: SubscriptionFrequency

class EmailSubscriptionCreate(EmailSubscriptionBase):
    pass

class EmailSubscriptionUpdate(BaseModel):
    frequency: Optional[SubscriptionFrequency] = None
    is_active: Optional[bool] = None

class EmailSubscriptionResponse(EmailSubscriptionBase):
    id: str
    user_id: str
    is_active: bool
    next_send_date: Optional[datetime] = None
    last_sent_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Comment Schemas
class CommentBase(BaseModel):
    content: str
    dashboard_id: Optional[str] = None
    query_id: Optional[str] = None
    mentions: Optional[List[str]] = []
    parent_id: Optional[str] = None

class CommentCreate(CommentBase):
    pass

class CommentUpdate(BaseModel):
    content: str

class CommentResponse(CommentBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Activity Schemas
class ActivityResponse(BaseModel):
    id: str
    user_id: str
    activity_type: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    entity_name: Optional[str] = None
    description: Optional[str] = None
    activity_metadata: Optional[dict] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Alert Schemas
class AlertBase(BaseModel):
    name: str
    description: Optional[str] = None
    query_id: str
    condition_type: str
    threshold_value: Optional[float] = None
    threshold_value_2: Optional[float] = None
    metric_column: str
    frequency: str = "once"
    notify_emails: List[EmailStr] = []
    notify_slack: bool = False
    slack_webhook: Optional[str] = None

class AlertCreate(AlertBase):
    pass

class AlertUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    condition_type: Optional[str] = None
    threshold_value: Optional[float] = None
    threshold_value_2: Optional[float] = None
    metric_column: Optional[str] = None
    frequency: Optional[str] = None
    notify_emails: Optional[List[EmailStr]] = None
    notify_slack: Optional[bool] = None
    slack_webhook: Optional[str] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None

class AlertResponse(AlertBase):
    id: str
    user_id: str
    status: str
    is_active: bool
    last_checked_at: Optional[datetime] = None
    last_triggered_at: Optional[datetime] = None
    next_check_at: Optional[datetime] = None
    snooze_until: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class AlertHistoryResponse(BaseModel):
    id: str
    alert_id: str
    triggered_at: datetime
    condition_met: bool
    actual_value: Optional[float] = None
    threshold_value: Optional[float] = None
    notification_sent: bool
    notification_error: Optional[str] = None
    
    class Config:
        from_attributes = True
