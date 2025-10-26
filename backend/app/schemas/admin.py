"""
Admin schemas for Phase 4.5 - Enterprise Admin
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class MetricTypeEnum(str, Enum):
    REDIS = "redis"
    INFLUXDB = "influxdb"
    DATABASE = "database"


class BackupTypeEnum(str, Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    CONFIGURATION = "configuration"


class BackupStatusEnum(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class BackupStorageTypeEnum(str, Enum):
    LOCAL = "local"
    S3 = "s3"
    AZURE = "azure"


# System Metrics Schemas
class SystemMetricsBase(BaseModel):
    cpu_usage: float = Field(..., ge=0, le=100, description="CPU usage percentage")
    memory_usage: float = Field(..., ge=0, le=100, description="Memory usage percentage")
    disk_usage: float = Field(..., ge=0, le=100, description="Disk usage percentage")
    active_users: int = Field(default=0, ge=0)
    api_requests: int = Field(default=0, ge=0)
    query_count: int = Field(default=0, ge=0)
    cache_hit_rate: float = Field(default=0.0, ge=0, le=100)
    avg_query_time: Optional[float] = None
    avg_api_response_time: Optional[float] = None
    error_count: int = Field(default=0, ge=0)
    additional_data: Optional[Dict[str, Any]] = None


class SystemMetricsCreate(SystemMetricsBase):
    pass


class SystemMetricsResponse(SystemMetricsBase):
    id: str
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class SystemMetricsQuery(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metric_type: MetricTypeEnum = MetricTypeEnum.DATABASE
    limit: int = Field(default=100, ge=1, le=1000)


# User Activity Schemas
class UserActivityBase(BaseModel):
    action: str
    resource: Optional[str] = None
    resource_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    location: Optional[str] = None
    duration: Optional[int] = None
    additional_data: Optional[Dict[str, Any]] = None


class UserActivityCreate(UserActivityBase):
    user_id: str
    tenant_id: Optional[str] = None


class UserActivityResponse(UserActivityBase):
    id: str
    user_id: str
    tenant_id: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True


class UserActivityQuery(BaseModel):
    user_id: Optional[str] = None
    action: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)


# User Session Schemas
class UserSessionResponse(BaseModel):
    id: str
    user_id: str
    tenant_id: Optional[str]
    session_token: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    location: Optional[str]
    is_active: bool
    last_activity: datetime
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True


# Tenant Usage Metrics Schemas
class TenantUsageMetricsBase(BaseModel):
    active_users: int = 0
    total_users: int = 0
    new_users: int = 0
    query_count: int = 0
    dashboard_count: int = 0
    datasource_count: int = 0
    api_calls: int = 0
    storage_used: float = 0.0
    avg_query_time: Optional[float] = None
    cache_hit_rate: Optional[float] = None
    billable_amount: float = 0.0
    metadata: Optional[Dict[str, Any]] = None


class TenantUsageMetricsCreate(TenantUsageMetricsBase):
    tenant_id: str
    date: datetime


class TenantUsageMetricsResponse(TenantUsageMetricsBase):
    id: str
    tenant_id: str
    date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class TenantUsageQuery(BaseModel):
    tenant_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(default=30, ge=1, le=365)


# Backup Job Schemas
class BackupJobBase(BaseModel):
    backup_type: BackupTypeEnum
    storage_type: BackupStorageTypeEnum
    includes_data: bool = True
    includes_config: bool = True
    tables_included: Optional[List[str]] = None
    is_encrypted: bool = True


class BackupJobCreate(BackupJobBase):
    tenant_id: Optional[str] = None
    s3_bucket: Optional[str] = None
    s3_region: Optional[str] = None
    description: Optional[str] = None


class BackupJobResponse(BackupJobBase):
    id: str
    tenant_id: Optional[str]
    status: BackupStatusEnum
    file_path: Optional[str]
    file_name: Optional[str]
    file_size: Optional[float]
    s3_bucket: Optional[str]
    s3_key: Optional[str]
    s3_region: Optional[str]
    encryption_key_id: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    error_message: Optional[str]
    retry_count: int
    metadata: Optional[Dict[str, Any]]
    created_by: Optional[str]

    class Config:
        from_attributes = True


class BackupJobQuery(BaseModel):
    tenant_id: Optional[str] = None
    status: Optional[BackupStatusEnum] = None
    backup_type: Optional[BackupTypeEnum] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(default=50, ge=1, le=200)


class BackupRestoreRequest(BaseModel):
    backup_id: str
    restore_data: bool = True
    restore_config: bool = True
    tables_to_restore: Optional[List[str]] = None
    tenant_id: Optional[str] = None


class BackupScheduleConfig(BaseModel):
    enabled: bool = True
    backup_type: BackupTypeEnum
    storage_type: BackupStorageTypeEnum
    frequency: str = Field(..., description="Cron expression")
    retention_days: int = Field(default=30, ge=1, le=365)
    includes_data: bool = True
    includes_config: bool = True


# Configuration Version Schemas
class ConfigurationVersionBase(BaseModel):
    description: Optional[str] = None
    configuration: Dict[str, Any]


class ConfigurationVersionCreate(ConfigurationVersionBase):
    tenant_id: str


class ConfigurationVersionResponse(ConfigurationVersionBase):
    id: str
    tenant_id: str
    version: int
    changes: Optional[Dict[str, Any]]
    changed_by: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ConfigurationExportRequest(BaseModel):
    tenant_id: Optional[str] = None
    include_secrets: bool = False
    sections: Optional[List[str]] = None  # ["branding", "integrations", "security", etc.]


class ConfigurationImportRequest(BaseModel):
    tenant_id: Optional[str] = None
    configuration: Dict[str, Any]
    merge: bool = False  # If False, replace all; if True, merge with existing
    create_version: bool = True


# Health Check Schemas
class SystemHealthCheckResponse(BaseModel):
    id: str
    timestamp: datetime
    database_status: str
    redis_status: str
    api_status: str
    email_service_status: Optional[str]
    slack_service_status: Optional[str]
    database_response_time: Optional[float]
    redis_response_time: Optional[float]
    api_response_time: Optional[float]
    overall_status: str
    alerts_triggered: Optional[List[Dict[str, Any]]]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


class HealthCheckRequest(BaseModel):
    check_database: bool = True
    check_redis: bool = True
    check_integrations: bool = False


# Performance Analytics Schemas
class QueryPerformanceStats(BaseModel):
    query_id: str
    query_name: Optional[str]
    avg_execution_time: float
    max_execution_time: float
    min_execution_time: float
    execution_count: int
    error_count: int
    cache_hit_rate: float
    last_executed: datetime


class APIEndpointPerformance(BaseModel):
    endpoint: str
    method: str
    avg_response_time: float
    p50_response_time: float
    p95_response_time: float
    p99_response_time: float
    request_count: int
    error_count: int
    error_rate: float


class PerformanceAnalyticsResponse(BaseModel):
    period_start: datetime
    period_end: datetime
    slowest_queries: List[QueryPerformanceStats]
    api_endpoints: List[APIEndpointPerformance]
    cache_statistics: Dict[str, Any]
    error_summary: Dict[str, int]


# Advanced User Management Schemas
class BulkUserImport(BaseModel):
    users: List[Dict[str, Any]]
    tenant_id: Optional[str] = None
    send_invitations: bool = True


class UserOffboardingRequest(BaseModel):
    user_id: str
    transfer_assets_to: Optional[str] = None  # User ID to transfer ownership
    delete_data: bool = False
    archive_data: bool = True
    revoke_access: bool = True


class UserManagementStats(BaseModel):
    total_users: int
    active_users: int
    inactive_users: int
    locked_users: int
    users_by_role: Dict[str, int]
    recent_logins: int
    failed_login_attempts: int


class UsageAnalyticsSummary(BaseModel):
    tenant_id: str
    period_start: datetime
    period_end: datetime
    total_users: int
    active_users: int
    total_queries: int
    total_dashboards: int
    total_api_calls: int
    storage_used_mb: float
    estimated_cost: float
    usage_trend: List[Dict[str, Any]]
