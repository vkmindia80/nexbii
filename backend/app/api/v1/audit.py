"""
Audit API Endpoints
Handles audit log viewing and export
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.security import (
    AuditLogResponse,
    AuditLogFilters,
    AuditEventCategory
)
from app.services.audit_service import AuditService

router = APIRouter()


@router.get("/logs", response_model=List[AuditLogResponse])
def list_audit_logs(
    event_category: AuditEventCategory = None,
    event_type: str = None,
    user_id: str = None,
    resource_type: str = None,
    action: str = None,
    status: str = None,
    from_date: datetime = None,
    to_date: datetime = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List audit logs with filters"""
    audit_service = AuditService(db)
    
    logs = audit_service.get_logs(
        tenant_id=current_user.tenant_id,
        event_category=event_category,
        event_type=event_type,
        user_id=user_id,
        resource_type=resource_type,
        action=action,
        status=status,
        from_date=from_date,
        to_date=to_date,
        skip=skip,
        limit=limit
    )
    
    return logs


@router.get("/logs/{log_id}", response_model=AuditLogResponse)
def get_audit_log(
    log_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get audit log details"""
    from app.models.security import AuditLog
    
    log = db.query(AuditLog).filter(
        AuditLog.id == log_id,
        AuditLog.tenant_id == current_user.tenant_id
    ).first()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found"
        )
    
    return log


@router.post("/logs/export")
def export_audit_logs(
    from_date: datetime = None,
    to_date: datetime = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export audit logs to CSV/JSON"""
    audit_service = AuditService(db)
    
    logs = audit_service.get_logs(
        tenant_id=current_user.tenant_id,
        from_date=from_date,
        to_date=to_date,
        skip=0,
        limit=10000  # Max export limit
    )
    
    # Convert to export format
    import json
    export_data = [{
        "id": log.id,
        "event_type": log.event_type,
        "event_category": log.event_category,
        "user": log.username,
        "action": log.action,
        "status": log.status,
        "resource_type": log.resource_type,
        "resource_id": log.resource_id,
        "created_at": log.created_at.isoformat() if log.created_at else None
    } for log in logs]
    
    return {
        "total": len(export_data),
        "data": export_data
    }


@router.get("/events")
def list_event_types(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all event types"""
    from app.models.security import AuditLog
    from sqlalchemy import func, distinct
    
    event_types = db.query(
        distinct(AuditLog.event_type)
    ).filter(
        AuditLog.tenant_id == current_user.tenant_id
    ).all()
    
    return {
        "event_types": [et[0] for et in event_types if et[0]]
    }


@router.get("/stats")
def get_audit_statistics(
    from_date: datetime = None,
    to_date: datetime = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get audit log statistics"""
    audit_service = AuditService(db)
    
    stats = audit_service.get_statistics(
        tenant_id=current_user.tenant_id,
        from_date=from_date,
        to_date=to_date
    )
    
    return stats
