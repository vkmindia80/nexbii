from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from ..core.database import Base

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    content = Column(Text, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    dashboard_id = Column(String, ForeignKey("dashboards.id"), nullable=True)
    query_id = Column(String, ForeignKey("queries.id"), nullable=True)
    mentions = Column(JSON)  # Array of user IDs mentioned
    parent_id = Column(String, ForeignKey("comments.id"), nullable=True)  # For replies
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    replies = relationship("Comment", backref="parent", remote_side=[id])
