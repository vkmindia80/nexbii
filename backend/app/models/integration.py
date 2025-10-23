from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
import uuid
from ..core.database import Base

class Integration(Base):
    __tablename__ = "integrations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Email Configuration (encrypted)
    smtp_host = Column(String, nullable=True)
    smtp_port = Column(String, nullable=True)
    smtp_user = Column(String, nullable=True)  # Encrypted
    smtp_password = Column(Text, nullable=True)  # Encrypted
    from_email = Column(String, nullable=True)
    from_name = Column(String, nullable=True)
    mock_email = Column(Boolean, default=True)
    
    # Slack Configuration (encrypted)
    slack_webhook_url = Column(Text, nullable=True)  # Encrypted
    mock_slack = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String, nullable=True)  # User ID who created/updated
