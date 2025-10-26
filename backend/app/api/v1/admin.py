"""
Admin API Endpoints for Phase 4.5 - Enterprise Admin
System monitoring, user management, backups, configuration
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import User
from app.schemas.admin import (
    # System Metrics
    SystemMetricsResponse, SystemMetricsQuery, MetricTypeEnum,
    # Health Check
    SystemHealthCheckResponse, HealthCheckRequest,
    # User Activity
    UserActivityResponse, UserActivityQuery,
    # User Sessions
    UserSessionResponse,
    # Tenant Usage
    TenantUsageMetricsResponse, TenantUsageQuery, UsageAnalyticsSummary,
    # User Management
    BulkUserImport, UserOffboardingRequest, UserManagementStats,
    # Backup
    BackupJobCreate, BackupJobResponse, BackupJobQuery, BackupRestoreRequest,
    BackupScheduleConfig,
    # Configuration
    ConfigurationVersionResponse, ConfigurationExportRequest,
    ConfigurationImportRequest,
    # Performance
    PerformanceAnalyticsResponse, QueryPerformanceStats, APIEndpointPerformance
)
from app.services.monitoring_service import MonitoringService
from app.services.user_management_service import get_user_management_service
from app.services.usage_analytics_service import get_usage_analytics_service
from app.services.backup_service import get_backup_service
from app.services.configuration_service import get_configuration_service

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ============================================================================
# SYSTEM MONITORING & HEALTH
# ============================================================================

@router.get("/health", response_model=SystemHealthCheckResponse)
def check_system_health(
    check_database: bool = Query(True),
    check_redis: bool = Query(True),
    check_integrations: bool = Query(False),
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """
    Perform comprehensive system health check
    Admin only
    """
    monitoring_service = MonitoringService(db)
    
    request = HealthCheckRequest(
        check_database=check_database,
        check_redis=check_redis,
        check_integrations=check_integrations
    )
    
    health_check = monitoring_service.perform_health_check(request)
    return health_check


@router.get("/metrics/system", response_model=List[SystemMetricsResponse])
def get_system_metrics(
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    metric_type: MetricTypeEnum = Query(MetricTypeEnum.DATABASE),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """
    Get system performance metrics
    Admin only
    """
    monitoring_service = MonitoringService(db, metric_storage=metric_type.value)
    
    query = SystemMetricsQuery(
        start_time=start_time,
        end_time=end_time,
        metric_type=metric_type,
        limit=limit
    )
    
    metrics = monitoring_service.get_metrics(query)
    return metrics


@router.post("/metrics/collect")
def collect_metrics_now(
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """
    Manually trigger metrics collection
    Admin only
    """
    monitoring_service = MonitoringService(db)
    metrics = monitoring_service.collect_system_metrics()
    monitoring_service.store_metrics(metrics)
    
    return {
        "status": "success",
        "message": "Metrics collected successfully",
        "metrics": metrics
    }


@router.delete("/metrics/cleanup")
def cleanup_old_metrics(
    days: int = Query(90, ge=30, le=365),
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """
    Clean up old metrics data
    Admin only
    """
    monitoring_service = MonitoringService(db)
    deleted_count = monitoring_service.cleanup_old_metrics(days)
    
    return {
        "status": "success",
        "deleted_count": deleted_count,
        "message": f"Cleaned up metrics older than {days} days"
    }


# ============================================================================
# USER MANAGEMENT
# ============================================================================

@router.get("/users/stats", response_model=UserManagementStats)
def get_user_stats(
    tenant_id: Optional[str] = Query(None),
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """
    Get user management statistics
    Admin only
    """
    service = get_user_management_service(db)
    return service.get_user_management_stats(tenant_id)


@router.get("/users/{user_id}/activity", response_model=List[UserActivityResponse])
def get_user_activity(
    user_id: str,
    limit: int = Query(100, ge=1, le=500),
    action: Optional[str] = Query(None),
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """
    Get activity history for a specific user
    Admin only
    """
    service = get_user_management_service(db)
    activities = service.get_user_activity_history(user_id, limit, action)
    return activities


@router.get("/users/{user_id}/sessions", response_model=List[UserSessionResponse])
def get_user_sessions(
    user_id: str,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """
    Get active sessions for a user
    Admin only
    """
    service = get_user_management_service(db)
    sessions = service.get_active_sessions(user_id)
    return sessions


@router.post("/users/{user_id}/sessions/{session_id}/terminate")
def terminate_user_session(
    user_id: str,
    session_id: str,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """
    Terminate a user session
    Admin only
    """
    service = get_user_management_service(db)
    success = service.terminate_session(session_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"status": "success", "message": "Session terminated"}


@router.post("/users/bulk-import")
def bulk_import_users(
    import_request: BulkUserImport,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """
    Bulk import users from CSV data
    Admin only
    """
    service = get_user_management_service(db)
    result = service.bulk_import_users(import_request, current_user.id)
    return result


@router.post("/users/{user_id}/offboard")
def offboard_user(
    user_id: str,
    request: UserOffboardingRequest,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """
    Offboard a user with asset transfer and data management
    Admin only
    """
    service = get_user_management_service(db)
    result = service.offboard_user(request, current_user.id)
    return result


@router.post("/users/{user_id}/lock")
def lock_user_account(
    user_id: str,
    reason: str = Query(..., min_length=1),
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """
    Lock a user account (prevent login)
    Admin only
    """
    service = get_user_management_service(db)
    user = service.lock_user_account(user_id, reason, current_user.id)
    
    return {
        "status": "success",
        "message": f"User {user.email} has been locked",
        "reason": reason
    }


@router.post("/users/{user_id}/unlock")
def unlock_user_account(
    user_id: str,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """
    Unlock a user account
    Admin only
    """
    service = get_user_management_service(db)
    user = service.unlock_user_account(user_id, current_user.id)
    
    return {
        "status": "success",
        "message": f"User {user.email} has been unlocked"
    }


@router.post("/sessions/cleanup")
def cleanup_expired_sessions(
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """
    Clean up expired sessions
    Admin only
    """
    service = get_user_management_service(db)
    cleaned = service.cleanup_expired_sessions()
    
    return {
        "status": "success",
        "cleaned_count": cleaned,
        "message": f"Cleaned up {cleaned} expired sessions"
    }


# ============================================================================
# USAGE ANALYTICS
# ============================================================================

@router.get("/usage/tenant/{tenant_id}", response_model=UsageAnalyticsSummary)
def get_tenant_usage_summary(
    tenant_id: str,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """
    Get usage analytics summary for a tenant
    Admin only
    """
    service = get_usage_analytics_service(db)
    
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
    summary = service.get_usage_summary(tenant_id, start_date, end_date)
    return summary


@router.get("/usage/metrics", response_model=List[TenantUsageMetricsResponse])
def get_usage_metrics(
    tenant_id: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(30, ge=1, le=365),
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """
    Get detailed usage metrics
    Admin only
    """
    service = get_usage_analytics_service(db)
    
    query = TenantUsageQuery(
        tenant_id=tenant_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )
    
    metrics = service.get_usage_metrics(query)
    return metrics


@router.post("/usage/aggregate")
def aggregate_usage(
    tenant_id: Optional[str] = Query(None),
    date: Optional[datetime] = Query(None),
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """
    Manually trigger usage aggregation
    Admin only
    """
    service = get_usage_analytics_service(db)
    
    if not date:
        date = datetime.utcnow() - timedelta(days=1)
    
    if tenant_id:
        metrics = service.aggregate_daily_usage(tenant_id, date)
        stored = service.store_usage_metrics(metrics)
        return {
            "status": "success",
            "tenant_id": tenant_id,
            "metrics": stored
        }
    else:
        results = service.aggregate_all_tenants_usage(date)
        return {
            "status": "success",
            "tenants_processed": len(results),
            "date": date.isoformat()
        }


@router.get("/usage/billing/{tenant_id}")
def get_billing_report(
    tenant_id: str,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """
    Generate billing report for a tenant
    Admin only
    """
    service = get_usage_analytics_service(db)
    
    if not start_date:
        start_date = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
    if not end_date:
        end_date = datetime.utcnow()
    
    report = service.get_billing_report(tenant_id, start_date, end_date)
    return report


# ============================================================================
# BACKUP & RESTORE
# ============================================================================

@router.post("/backups", response_model=BackupJobResponse)
def create_backup(
    backup_request: BackupJobCreate,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """
    Create a new backup
    Admin only
    """
    service = get_backup_service(db)
    backup = service.create_backup(backup_request, current_user.id)
    return backup


@router.get("/backups", response_model=List[BackupJobResponse])
def list_backups(
    tenant_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """
    List available backups
    Admin only
    """
    service = get_backup_service(db)
    backups = service.list_backups(tenant_id, limit)
    return backups


@router.post("/backups/{backup_id}/restore")
def restore_backup(
    backup_id: str,
    restore_request: BackupRestoreRequest,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """
    Restore from a backup
    DANGEROUS - Admin only
    """
    service = get_backup_service(db)
    restore_request.backup_id = backup_id
    result = service.restore_backup(restore_request, current_user.id)
    return result


@router.delete("/backups/cleanup")
def cleanup_old_backups(
    retention_days: int = Query(30, ge=7, le=365),
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """
    Clean up old backups
    Admin only
    """
    service = get_backup_service(db)
    deleted = service.cleanup_old_backups(retention_days)
    
    return {
        "status": "success",
        "deleted_count": deleted,
        "message": f"Cleaned up backups older than {retention_days} days"
    }


# ============================================================================
# CONFIGURATION MANAGEMENT
# ============================================================================

@router.post("/config/export")
def export_configuration(
    export_request: ConfigurationExportRequest,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """
    Export configuration
    Admin only
    """
    service = get_configuration_service(db)
    config = service.export_configuration(export_request)
    return config


@router.post("/config/import")
def import_configuration(
    import_request: ConfigurationImportRequest,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """
    Import configuration
    Admin only
    """
    service = get_configuration_service(db)
    result = service.import_configuration(import_request, current_user.id)
    return result


@router.get("/config/versions/{tenant_id}", response_model=List[ConfigurationVersionResponse])
def get_configuration_versions(
    tenant_id: str,
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """
    Get configuration version history
    Admin only
    """
    service = get_configuration_service(db)
    versions = service.get_versions(tenant_id, limit)
    return versions


@router.post("/config/rollback/{tenant_id}/{version_id}")
def rollback_configuration(
    tenant_id: str,
    version_id: str,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """
    Rollback configuration to a previous version
    Admin only
    """
    service = get_configuration_service(db)
    
    try:
        version = service.rollback_to_version(tenant_id, version_id, current_user.id)
        return {
            "status": "success",
            "message": f"Configuration rolled back to version {version.version}",
            "version_id": version.id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
