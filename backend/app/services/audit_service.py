"""
Audit Logging Service
Comprehensive audit logging for security and compliance
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.security import AuditLog, AuditEventCategory
from app.models.user import User
import uuid


class AuditService:
    """Service for creating and managing audit logs"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_event(
        self,
        event_type: str,
        event_category: AuditEventCategory,
        action: str,
        status: str,
        tenant_id: str,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        user_role: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        resource_name: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_method: Optional[str] = None,
        request_path: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        duration_ms: Optional[int] = None
    ) -> AuditLog:
        """
        Create an audit log entry
        
        Args:
            event_type: Type of event (login, query_executed, etc.)
            event_category: Category (authentication, data_access, etc.)
            action: Action performed (create, read, update, delete, execute)
            status: Status (success, failure, denied)
            tenant_id: Tenant ID
            user_id: User ID (optional for system events)
            username: Username
            user_role: User role
            resource_type: Type of resource affected
            resource_id: ID of resource
            resource_name: Name of resource
            ip_address: IP address of request
            user_agent: User agent string
            request_method: HTTP method
            request_path: Request path
            details: Additional details
            error_message: Error message if failed
            duration_ms: Duration in milliseconds
            
        Returns:
            Created AuditLog
        """
        log = AuditLog(
            id=str(uuid.uuid4()),
            event_type=event_type,
            event_category=event_category,
            action=action,
            status=status,
            tenant_id=tenant_id,
            user_id=user_id,
            username=username,
            user_role=user_role,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            ip_address=ip_address,
            user_agent=user_agent,
            request_method=request_method,
            request_path=request_path,
            details=details or {},
            error_message=error_message,
            duration_ms=duration_ms,
            created_at=datetime.utcnow()
        )
        
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        
        return log
    
    # Authentication Events
    
    def log_login_attempt(
        self,
        email: str,
        success: bool,
        tenant_id: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """Log login attempt"""
        return self.log_event(
            event_type="login_attempt",
            event_category=AuditEventCategory.AUTHENTICATION,
            action="login",
            status="success" if success else "failure",
            tenant_id=tenant_id,
            user_id=user_id,
            username=email,
            ip_address=ip_address,
            user_agent=user_agent,
            error_message=error_message
        )
    
    def log_logout(
        self,
        user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log logout"""
        return self.log_event(
            event_type="logout",
            event_category=AuditEventCategory.AUTHENTICATION,
            action="logout",
            status="success",
            tenant_id=user.tenant_id,
            user_id=user.id,
            username=user.email,
            user_role=user.role,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def log_password_change(
        self,
        user: User,
        success: bool,
        ip_address: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """Log password change"""
        return self.log_event(
            event_type="password_change",
            event_category=AuditEventCategory.AUTHENTICATION,
            action="update",
            status="success" if success else "failure",
            tenant_id=user.tenant_id,
            user_id=user.id,
            username=user.email,
            user_role=user.role,
            ip_address=ip_address,
            error_message=error_message
        )
    
    # Data Access Events
    
    def log_query_execution(
        self,
        user: User,
        query_id: str,
        query_name: str,
        datasource_id: str,
        success: bool,
        duration_ms: int,
        row_count: Optional[int] = None,
        ip_address: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """Log query execution"""
        return self.log_event(
            event_type="query_executed",
            event_category=AuditEventCategory.DATA_ACCESS,
            action="execute",
            status="success" if success else "failure",
            tenant_id=user.tenant_id,
            user_id=user.id,
            username=user.email,
            user_role=user.role,
            resource_type="query",
            resource_id=query_id,
            resource_name=query_name,
            ip_address=ip_address,
            duration_ms=duration_ms,
            details={
                "datasource_id": datasource_id,
                "row_count": row_count
            },
            error_message=error_message
        )
    
    def log_dashboard_view(
        self,
        user: User,
        dashboard_id: str,
        dashboard_name: str,
        ip_address: Optional[str] = None
    ):
        """Log dashboard view"""
        return self.log_event(
            event_type="dashboard_viewed",
            event_category=AuditEventCategory.DATA_ACCESS,
            action="read",
            status="success",
            tenant_id=user.tenant_id,
            user_id=user.id,
            username=user.email,
            user_role=user.role,
            resource_type="dashboard",
            resource_id=dashboard_id,
            resource_name=dashboard_name,
            ip_address=ip_address
        )
    
    def log_data_export(
        self,
        user: User,
        resource_type: str,
        resource_id: str,
        export_format: str,
        success: bool,
        ip_address: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """Log data export"""
        return self.log_event(
            event_type="data_exported",
            event_category=AuditEventCategory.DATA_ACCESS,
            action="export",
            status="success" if success else "failure",
            tenant_id=user.tenant_id,
            user_id=user.id,
            username=user.email,
            user_role=user.role,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            details={"format": export_format},
            error_message=error_message
        )
    
    # Security Events
    
    def log_security_policy_change(
        self,
        user: User,
        policy_id: str,
        policy_name: str,
        action: str,
        ip_address: Optional[str] = None
    ):
        """Log security policy changes"""
        return self.log_event(
            event_type="security_policy_changed",
            event_category=AuditEventCategory.SECURITY_CHANGE,
            action=action,
            status="success",
            tenant_id=user.tenant_id,
            user_id=user.id,
            username=user.email,
            user_role=user.role,
            resource_type="security_policy",
            resource_id=policy_id,
            resource_name=policy_name,
            ip_address=ip_address
        )
    
    def log_mfa_enrollment(
        self,
        user: User,
        success: bool,
        ip_address: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """Log MFA enrollment"""
        return self.log_event(
            event_type="mfa_enrolled",
            event_category=AuditEventCategory.SECURITY_CHANGE,
            action="create",
            status="success" if success else "failure",
            tenant_id=user.tenant_id,
            user_id=user.id,
            username=user.email,
            user_role=user.role,
            ip_address=ip_address,
            error_message=error_message
        )
    
    def log_mfa_verification(
        self,
        user: User,
        success: bool,
        ip_address: Optional[str] = None
    ):
        """Log MFA verification"""
        return self.log_event(
            event_type="mfa_verified",
            event_category=AuditEventCategory.AUTHENTICATION,
            action="verify",
            status="success" if success else "failure",
            tenant_id=user.tenant_id,
            user_id=user.id,
            username=user.email,
            user_role=user.role,
            ip_address=ip_address
        )
    
    # User Management Events
    
    def log_user_created(
        self,
        creator: User,
        new_user_id: str,
        new_user_email: str,
        new_user_role: str,
        ip_address: Optional[str] = None
    ):
        """Log user creation"""
        return self.log_event(
            event_type="user_created",
            event_category=AuditEventCategory.USER_MANAGEMENT,
            action="create",
            status="success",
            tenant_id=creator.tenant_id,
            user_id=creator.id,
            username=creator.email,
            user_role=creator.role,
            resource_type="user",
            resource_id=new_user_id,
            resource_name=new_user_email,
            ip_address=ip_address,
            details={"new_user_role": new_user_role}
        )
    
    def log_user_deleted(
        self,
        deleter: User,
        deleted_user_id: str,
        deleted_user_email: str,
        ip_address: Optional[str] = None
    ):
        """Log user deletion"""
        return self.log_event(
            event_type="user_deleted",
            event_category=AuditEventCategory.USER_MANAGEMENT,
            action="delete",
            status="success",
            tenant_id=deleter.tenant_id,
            user_id=deleter.id,
            username=deleter.email,
            user_role=deleter.role,
            resource_type="user",
            resource_id=deleted_user_id,
            resource_name=deleted_user_email,
            ip_address=ip_address
        )
    
    # Compliance Events
    
    def log_gdpr_export(
        self,
        user: User,
        ip_address: Optional[str] = None
    ):
        """Log GDPR data export"""
        return self.log_event(
            event_type="gdpr_data_export",
            event_category=AuditEventCategory.COMPLIANCE,
            action="export",
            status="success",
            tenant_id=user.tenant_id,
            user_id=user.id,
            username=user.email,
            user_role=user.role,
            ip_address=ip_address
        )
    
    def log_gdpr_deletion(
        self,
        user: User,
        ip_address: Optional[str] = None
    ):
        """Log GDPR data deletion (right to be forgotten)"""
        return self.log_event(
            event_type="gdpr_data_deletion",
            event_category=AuditEventCategory.COMPLIANCE,
            action="delete",
            status="success",
            tenant_id=user.tenant_id,
            user_id=user.id,
            username=user.email,
            user_role=user.role,
            ip_address=ip_address
        )
    
    # Query Methods
    
    def get_logs(
        self,
        tenant_id: str,
        event_category: Optional[AuditEventCategory] = None,
        event_type: Optional[str] = None,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        action: Optional[str] = None,
        status: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        """Get audit logs with filters"""
        query = self.db.query(AuditLog).filter(
            AuditLog.tenant_id == tenant_id
        )
        
        if event_category:
            query = query.filter(AuditLog.event_category == event_category)
        
        if event_type:
            query = query.filter(AuditLog.event_type == event_type)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        
        if action:
            query = query.filter(AuditLog.action == action)
        
        if status:
            query = query.filter(AuditLog.status == status)
        
        if from_date:
            query = query.filter(AuditLog.created_at >= from_date)
        
        if to_date:
            query = query.filter(AuditLog.created_at <= to_date)
        
        query = query.order_by(AuditLog.created_at.desc())
        query = query.offset(skip).limit(limit)
        
        return query.all()
    
    def get_statistics(
        self,
        tenant_id: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get audit log statistics"""
        query = self.db.query(AuditLog).filter(
            AuditLog.tenant_id == tenant_id
        )
        
        if from_date:
            query = query.filter(AuditLog.created_at >= from_date)
        
        if to_date:
            query = query.filter(AuditLog.created_at <= to_date)
        
        total_events = query.count()
        
        # Count by category
        from sqlalchemy import func
        category_counts = self.db.query(
            AuditLog.event_category,
            func.count(AuditLog.id)
        ).filter(
            AuditLog.tenant_id == tenant_id
        )
        
        if from_date:
            category_counts = category_counts.filter(
                AuditLog.created_at >= from_date
            )
        
        if to_date:
            category_counts = category_counts.filter(
                AuditLog.created_at <= to_date
            )
        
        category_counts = category_counts.group_by(
            AuditLog.event_category
        ).all()
        
        # Count by status
        status_counts = self.db.query(
            AuditLog.status,
            func.count(AuditLog.id)
        ).filter(
            AuditLog.tenant_id == tenant_id
        )
        
        if from_date:
            status_counts = status_counts.filter(
                AuditLog.created_at >= from_date
            )
        
        if to_date:
            status_counts = status_counts.filter(
                AuditLog.created_at <= to_date
            )
        
        status_counts = status_counts.group_by(AuditLog.status).all()
        
        return {
            "total_events": total_events,
            "by_category": {cat: count for cat, count in category_counts},
            "by_status": {status: count for status, count in status_counts}
        }
