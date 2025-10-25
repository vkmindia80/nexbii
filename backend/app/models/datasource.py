from sqlalchemy import Column, String, JSON, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from ..core.database import Base

class DataSourceType(str, enum.Enum):
    # Relational Databases
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MSSQL = "mssql"  # Microsoft SQL Server
    ORACLE = "oracle"
    MARIADB = "mariadb"
    
    # NoSQL Databases
    MONGODB = "mongodb"
    CASSANDRA = "cassandra"
    DYNAMODB = "dynamodb"
    COUCHDB = "couchdb"
    
    # Cloud Data Warehouses
    SNOWFLAKE = "snowflake"
    REDSHIFT = "redshift"
    BIGQUERY = "bigquery"
    SYNAPSE = "synapse"  # Azure Synapse Analytics
    
    # Analytics & Search
    ELASTICSEARCH = "elasticsearch"
    CLICKHOUSE = "clickhouse"
    DRUID = "druid"
    
    # Time Series
    TIMESCALEDB = "timescaledb"
    INFLUXDB = "influxdb"
    
    # Other Popular Sources
    REDIS = "redis"
    PRESTO = "presto"
    TRINO = "trino"
    
    # File-based
    CSV = "csv"
    EXCEL = "excel"
    JSON_FILE = "json"
    PARQUET = "parquet"

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