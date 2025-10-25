from sqlalchemy import Column, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
import uuid
from ..core.database import Base

class Query(Base):
    __tablename__ = "queries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    datasource_id = Column(String, ForeignKey("datasources.id"))
    query_type = Column(String)  # 'visual' or 'sql'
    query_config = Column(JSON)  # Visual query builder config
    sql_query = Column(Text)  # Raw SQL query
    created_by = Column(String)  # User ID
    
    # Multi-tenancy
    tenant_id = Column(String, index=True, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())