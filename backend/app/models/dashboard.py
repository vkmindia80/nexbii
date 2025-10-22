from sqlalchemy import Column, String, Text, JSON, Boolean, DateTime
from sqlalchemy.sql import func
import uuid
from ..core.database import Base

class Dashboard(Base):
    __tablename__ = "dashboards"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    layout = Column(JSON)  # Dashboard grid layout configuration
    widgets = Column(JSON)  # Array of widget configurations
    filters = Column(JSON)  # Global filters
    is_public = Column(Boolean, default=False)
    created_by = Column(String)  # User ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())