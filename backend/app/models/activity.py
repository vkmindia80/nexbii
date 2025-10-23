from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.sql import func
import uuid
import enum
from ..core.database import Base

class ActivityType(str, enum.Enum):
    DASHBOARD_CREATED = "dashboard_created"
    DASHBOARD_UPDATED = "dashboard_updated"
    DASHBOARD_DELETED = "dashboard_deleted"
    DASHBOARD_SHARED = "dashboard_shared"
    QUERY_CREATED = "query_created"
    QUERY_EXECUTED = "query_executed"
    QUERY_UPDATED = "query_updated"
    QUERY_DELETED = "query_deleted"
    DATASOURCE_CREATED = "datasource_created"
    DATASOURCE_UPDATED = "datasource_updated"
    DATASOURCE_DELETED = "datasource_deleted"
    COMMENT_ADDED = "comment_added"
    USER_MENTIONED = "user_mentioned"
    SUBSCRIPTION_CREATED = "subscription_created"
    ALERT_TRIGGERED = "alert_triggered"

class Activity(Base):
    __tablename__ = "activities"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    activity_type = Column(SQLEnum(ActivityType), nullable=False)
    entity_type = Column(String)  # dashboard, query, datasource, etc.
    entity_id = Column(String)
    entity_name = Column(String)
    description = Column(Text)
    activity_metadata = Column(JSON)  # Additional context
    created_at = Column(DateTime(timezone=True), server_default=func.now())
