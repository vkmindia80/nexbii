from sqlalchemy import Column, String, JSON, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from ..core.database import Base

class DataSourceType(str, enum.Enum):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    SQLITE = "sqlite"
    CSV = "csv"
    EXCEL = "excel"
    JSON_FILE = "json"

class DataSource(Base):
    __tablename__ = "datasources"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    type = Column(SQLEnum(DataSourceType), nullable=False)
    connection_config = Column(JSON)  # Encrypted connection details
    created_by = Column(String)  # User ID
    is_active = Column(Boolean, default=True)
    
    # Multi-tenancy
    tenant_id = Column(String, index=True, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    analyses = relationship("SavedAnalysis", back_populates="datasource")