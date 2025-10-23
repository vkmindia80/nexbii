from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from ..core.database import Base

class SubscriptionFrequency(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class EmailSubscription(Base):
    __tablename__ = "email_subscriptions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    dashboard_id = Column(String, ForeignKey("dashboards.id"), nullable=False)
    frequency = Column(SQLEnum(SubscriptionFrequency), nullable=False)
    is_active = Column(Boolean, default=True)
    next_send_date = Column(DateTime(timezone=True))
    last_sent_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    # user = relationship("User", back_populates="subscriptions")
    # dashboard = relationship("Dashboard", back_populates="subscriptions")
