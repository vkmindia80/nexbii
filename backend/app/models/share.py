from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from app.core.database import Base
import secrets
import uuid


class SharedDashboard(Base):
    __tablename__ = "shared_dashboards"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dashboard_id = Column(String, ForeignKey("dashboards.id", ondelete="CASCADE"), nullable=False)
    share_token = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=True)  # Hashed password, optional
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    allow_interactions = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, ForeignKey("users.id"))
    
    # Relationships
    dashboard = relationship("Dashboard", back_populates="shared_links")
    creator = relationship("User")

    @staticmethod
    def generate_token():
        """Generate a secure random token for sharing"""
        return secrets.token_urlsafe(32)
