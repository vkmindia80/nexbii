from sqlalchemy import Column, String, Boolean, DateTime, Integer, JSON, Text, Index
from sqlalchemy.sql import func
import uuid
from ..core.database import Base

class Webhook(Base):
    """Webhook configuration model"""
    __tablename__ = "webhooks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Ownership
    tenant_id = Column(String, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=False)
    
    # Configuration
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    url = Column(String, nullable=False)  # Webhook endpoint URL
    secret = Column(String, nullable=False)  # For HMAC signature
    
    # Events to trigger on
    events = Column(JSON, nullable=False, default=list)
    # Available events:
    # - datasource.created, datasource.updated, datasource.deleted
    # - query.created, query.updated, query.deleted, query.executed
    # - dashboard.created, dashboard.updated, dashboard.deleted, dashboard.viewed
    # - alert.triggered, alert.resolved
    # - export.completed
    # - user.created, user.updated, user.deleted
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Retry configuration
    max_retries = Column(Integer, default=3)
    retry_backoff_seconds = Column(Integer, default=60)  # Base backoff time
    
    # Statistics
    total_deliveries = Column(Integer, default=0)
    successful_deliveries = Column(Integer, default=0)
    failed_deliveries = Column(Integer, default=0)
    last_triggered_at = Column(DateTime(timezone=True), nullable=True)
    last_success_at = Column(DateTime(timezone=True), nullable=True)
    last_failure_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_webhook_tenant_user', 'tenant_id', 'user_id'),
        Index('idx_webhook_active', 'is_active'),
    )


class WebhookDelivery(Base):
    """Webhook delivery log for tracking and retries"""
    __tablename__ = "webhook_deliveries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    webhook_id = Column(String, index=True, nullable=False)
    
    # Event details
    event_type = Column(String, nullable=False, index=True)
    event_data = Column(JSON, nullable=False)
    
    # Delivery details
    status = Column(String, nullable=False, index=True)  # pending, success, failed, retrying
    attempt_count = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    
    # Response details
    response_status_code = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Retry timing
    next_retry_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_webhook_delivery_status_retry', 'status', 'next_retry_at'),
        Index('idx_webhook_delivery_webhook_time', 'webhook_id', 'created_at'),
    )
