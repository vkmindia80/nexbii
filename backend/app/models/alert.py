from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from ..core.database import Base

class AlertConditionType(str, enum.Enum):
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    BETWEEN = "between"
    CHANGES_BY = "changes_by"

class AlertFrequency(str, enum.Enum):
    ONCE = "once"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"

class AlertStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    TRIGGERED = "triggered"
    SNOOZED = "snoozed"

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    query_id = Column(String, ForeignKey("queries.id"), nullable=False)
    
    # Alert conditions
    condition_type = Column(SQLEnum(AlertConditionType), nullable=False)
    threshold_value = Column(Float)
    threshold_value_2 = Column(Float)  # For BETWEEN condition
    metric_column = Column(String)  # Which column to check
    
    # Notification settings
    frequency = Column(SQLEnum(AlertFrequency), default=AlertFrequency.ONCE)
    notify_emails = Column(JSON)  # Array of email addresses
    notify_slack = Column(Boolean, default=False)
    slack_webhook = Column(String)
    
    # Status and tracking
    status = Column(SQLEnum(AlertStatus), default=AlertStatus.ACTIVE)
    is_active = Column(Boolean, default=True)
    last_checked_at = Column(DateTime(timezone=True))
    last_triggered_at = Column(DateTime(timezone=True))
    next_check_at = Column(DateTime(timezone=True))
    snooze_until = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    history = relationship("AlertHistory", back_populates="alert", cascade="all, delete-orphan")

class AlertHistory(Base):
    __tablename__ = "alert_history"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    alert_id = Column(String, ForeignKey("alerts.id"), nullable=False)
    triggered_at = Column(DateTime(timezone=True), server_default=func.now())
    condition_met = Column(Boolean)
    actual_value = Column(Float)
    threshold_value = Column(Float)
    notification_sent = Column(Boolean, default=False)
    notification_error = Column(Text)
    query_result = Column(JSON)
    
    # Relationships
    alert = relationship("Alert", back_populates="history")
