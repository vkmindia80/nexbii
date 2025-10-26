"""
Admin models for Phase 4.5 - Enterprise Admin
Includes: SystemMetrics, UserActivity, BackupJob
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum
import uuid


class MetricType(str, enum.Enum):
    """Metric storage type"""
    REDIS = "redis"
    INFLUXDB = "influxdb"
    DATABASE = "database"


class BackupType(str, enum.Enum):
    """Backup type enumeration"""
    FULL = "full"
    INCREMENTAL = "incremental"
    CONFIGURATION = "configuration"


class BackupStatus(str, enum.Enum):
    """Backup job status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class BackupStorageType(str, enum.Enum):
    """Backup storage location"""
    LOCAL = "local"
    S3 = "s3"
    AZURE = "azure"


class SystemMetrics(Base):
    """
    System metrics for monitoring
    Stores system performance data
    """
    __tablename__ = "system_metrics"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # System metrics
    cpu_usage = Column(Float, nullable=False)  # Percentage 0-100
    memory_usage = Column(Float, nullable=False)  # Percentage 0-100
    disk_usage = Column(Float, nullable=False)  # Percentage 0-100
    
    # Application metrics
    active_users = Column(Integer, default=0)
    api_requests = Column(Integer, default=0)
    query_count = Column(Integer, default=0)
    cache_hit_rate = Column(Float, default=0.0)  # Percentage 0-100
    
    # Performance metrics
    avg_query_time = Column(Float, nullable=True)  # Milliseconds
    avg_api_response_time = Column(Float, nullable=True)  # Milliseconds
    error_count = Column(Integer, default=0)
    
    # Additional data
    additional_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserActivity(Base):
    """
    Detailed user activity tracking
    Used for advanced user management and analytics
    """
    __tablename__ = "user_activities"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=True, index=True)
    
    # Activity details
    action = Column(String, nullable=False, index=True)  # login, query_execute, dashboard_create, etc.
    resource = Column(String, nullable=True)  # Resource type (query, dashboard, datasource)
    resource_id = Column(String, nullable=True)  # ID of the resource
    
    # Session information
    session_id = Column(String, nullable=True, index=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    location = Column(String, nullable=True)  # City, Country
    
    # Performance
    duration = Column(Integer, nullable=True)  # Duration in milliseconds
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Additional data
    additional_data = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship("User", backref="detailed_activities")
    tenant = relationship("Tenant", backref="user_activities")


class UserSession(Base):
    """
    Active user sessions tracking
    For monitoring concurrent users and session management
    """
    __tablename__ = "user_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=True, index=True)
    
    # Session details
    session_token = Column(String, nullable=False, unique=True, index=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    
    # Relationships
    user = relationship("User", backref="sessions")
    tenant = relationship("Tenant", backref="user_sessions")


class TenantUsageMetrics(Base):
    """
    Daily tenant usage metrics for billing and analytics
    Aggregated daily to avoid excessive data
    """
    __tablename__ = "tenant_usage_metrics"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    
    # User metrics
    active_users = Column(Integer, default=0)
    total_users = Column(Integer, default=0)
    new_users = Column(Integer, default=0)
    
    # Usage metrics
    query_count = Column(Integer, default=0)
    dashboard_count = Column(Integer, default=0)
    datasource_count = Column(Integer, default=0)
    api_calls = Column(Integer, default=0)
    
    # Storage metrics
    storage_used = Column(Float, default=0.0)  # MB
    
    # Performance metrics
    avg_query_time = Column(Float, nullable=True)
    cache_hit_rate = Column(Float, nullable=True)
    
    # Billing data
    billable_amount = Column(Float, default=0.0)
    
    # Additional data
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", backref="usage_metrics")


class BackupJob(Base):
    """
    Backup job tracking
    Manages database backups and configuration exports
    """
    __tablename__ = "backup_jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=True, index=True)
    
    # Backup details
    backup_type = Column(SQLEnum(BackupType), nullable=False)
    storage_type = Column(SQLEnum(BackupStorageType), nullable=False)
    status = Column(SQLEnum(BackupStatus), default=BackupStatus.PENDING, index=True)
    
    # File information
    file_path = Column(String, nullable=True)  # Local path or S3 key
    file_name = Column(String, nullable=True)
    file_size = Column(Float, nullable=True)  # Size in MB
    
    # S3 information (if applicable)
    s3_bucket = Column(String, nullable=True)
    s3_key = Column(String, nullable=True)
    s3_region = Column(String, nullable=True)
    
    # Backup scope
    includes_data = Column(Boolean, default=True)
    includes_config = Column(Boolean, default=True)
    tables_included = Column(JSON, nullable=True)  # List of table names
    
    # Encryption
    is_encrypted = Column(Boolean, default=True)
    encryption_key_id = Column(String, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Metadata
    metadata = Column(JSON, nullable=True)
    created_by = Column(String, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    tenant = relationship("Tenant", backref="backups")
    creator = relationship("User", backref="created_backups")


class ConfigurationVersion(Base):
    """
    Configuration versioning for rollback capability
    Stores snapshots of tenant configurations
    """
    __tablename__ = "configuration_versions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Version information
    version = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    
    # Configuration data
    configuration = Column(JSON, nullable=False)  # Full configuration snapshot
    
    # Change tracking
    changes = Column(JSON, nullable=True)  # Diff from previous version
    changed_by = Column(String, ForeignKey("users.id"), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=False)  # Current active version
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    tenant = relationship("Tenant", backref="config_versions")
    changer = relationship("User", backref="config_changes")


class SystemHealthCheck(Base):
    """
    System health check results
    Tracks health of various system components
    """
    __tablename__ = "system_health_checks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Component status
    database_status = Column(String, nullable=False)  # healthy, degraded, down
    redis_status = Column(String, nullable=False)
    api_status = Column(String, nullable=False)
    
    # External integrations
    email_service_status = Column(String, nullable=True)
    slack_service_status = Column(String, nullable=True)
    
    # Response times
    database_response_time = Column(Float, nullable=True)  # ms
    redis_response_time = Column(Float, nullable=True)  # ms
    api_response_time = Column(Float, nullable=True)  # ms
    
    # Overall health
    overall_status = Column(String, nullable=False, index=True)  # healthy, degraded, critical
    
    # Alerts triggered
    alerts_triggered = Column(JSON, nullable=True)
    
    # Additional data
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
