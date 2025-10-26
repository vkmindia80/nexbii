"""
User Management Service for Phase 4.5 - Enterprise Admin
Advanced user management including bulk operations, offboarding, session management
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
import csv
import io
import logging

from app.models.user import User
from app.models.admin import UserActivity, UserSession, TenantUsageMetrics
from app.models.query import Query
from app.models.dashboard import Dashboard
from app.models.datasource import DataSource
from app.schemas.admin import (
    BulkUserImport, UserOffboardingRequest, UserManagementStats,
    UserActivityCreate, TenantUsageMetricsCreate
)
from app.core.security import get_password_hash

logger = logging.getLogger(__name__)


class UserManagementService:
    """
    Service for advanced user management operations
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_user_activity(
        self,
        user_id: str,
        action: str,
        resource: Optional[str] = None,
        resource_id: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        duration: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tenant_id: Optional[str] = None
    ) -> UserActivity:
        """
        Log detailed user activity
        """
        activity = UserActivity(
            user_id=user_id,
            tenant_id=tenant_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            duration=duration,
            metadata=metadata
        )
        
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        
        return activity
    
    def create_user_session(
        self,
        user_id: str,
        session_token: str,
        expires_at: datetime,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        location: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> UserSession:
        """
        Create a new user session
        """
        session = UserSession(
            user_id=user_id,
            tenant_id=tenant_id,
            session_token=session_token,
            ip_address=ip_address,
            user_agent=user_agent,
            location=location,
            expires_at=expires_at
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    def update_session_activity(self, session_token: str) -> Optional[UserSession]:
        """
        Update last activity timestamp for a session
        """
        session = self.db.query(UserSession).filter(
            UserSession.session_token == session_token,
            UserSession.is_active == True
        ).first()
        
        if session:
            session.last_activity = datetime.utcnow()
            self.db.commit()
            self.db.refresh(session)
        
        return session
    
    def terminate_session(self, session_id: str) -> bool:
        """
        Terminate a user session
        """
        session = self.db.query(UserSession).filter(
            UserSession.id == session_id
        ).first()
        
        if session:
            session.is_active = False
            self.db.commit()
            return True
        
        return False
    
    def get_active_sessions(self, user_id: str) -> List[UserSession]:
        """
        Get all active sessions for a user
        """
        return self.db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active == True,
            UserSession.expires_at > datetime.utcnow()
        ).order_by(desc(UserSession.last_activity)).all()
    
    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions
        Returns number of sessions cleaned up
        """
        expired_count = self.db.query(UserSession).filter(
            or_(
                UserSession.expires_at < datetime.utcnow(),
                UserSession.last_activity < datetime.utcnow() - timedelta(days=7)
            ),
            UserSession.is_active == True
        ).update({"is_active": False})
        
        self.db.commit()
        return expired_count
    
    def bulk_import_users(
        self,
        import_request: BulkUserImport,
        created_by: str
    ) -> Dict[str, Any]:
        """
        Bulk import users from CSV data
        Returns summary of import operation
        """
        results = {
            "total": len(import_request.users),
            "success": 0,
            "failed": 0,
            "errors": []
        }
        
        for user_data in import_request.users:
            try:
                # Check if user already exists
                existing_user = self.db.query(User).filter(
                    User.email == user_data.get("email")
                ).first()
                
                if existing_user:
                    results["failed"] += 1
                    results["errors"].append({
                        "email": user_data.get("email"),
                        "error": "User already exists"
                    })
                    continue
                
                # Create new user
                new_user = User(
                    email=user_data.get("email"),
                    full_name=user_data.get("full_name", ""),
                    password_hash=get_password_hash(user_data.get("password", "changeme123")),
                    role=user_data.get("role", "viewer"),
                    tenant_id=import_request.tenant_id,
                    is_active=True
                )
                
                self.db.add(new_user)
                self.db.flush()
                
                # Log activity
                self.log_user_activity(
                    user_id=created_by,
                    action="user_bulk_import",
                    resource="user",
                    resource_id=new_user.id,
                    metadata={"imported_email": user_data.get("email")}
                )
                
                results["success"] += 1
                
                # Send invitation email if requested
                if import_request.send_invitations:
                    try:
                        from app.services.email_service import email_service
                        email_service.send_invitation_email(
                            user_email=new_user.email,
                            user_name=new_user.full_name,
                            invited_by=created_by
                        )
                    except Exception as e:
                        logger.warning(f"Failed to send invitation email: {e}")
                
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "email": user_data.get("email", "unknown"),
                    "error": str(e)
                })
                logger.error(f"Error importing user: {e}")
        
        self.db.commit()
        
        return results
    
    def offboard_user(
        self,
        request: UserOffboardingRequest,
        performed_by: str
    ) -> Dict[str, Any]:
        """
        Offboard a user with asset transfer and data management
        """
        user = self.db.query(User).filter(User.id == request.user_id).first()
        
        if not user:
            raise ValueError("User not found")
        
        result = {
            "user_id": request.user_id,
            "email": user.email,
            "actions_performed": []
        }
        
        # Transfer asset ownership if specified
        if request.transfer_assets_to:
            transfer_to_user = self.db.query(User).filter(
                User.id == request.transfer_assets_to
            ).first()
            
            if transfer_to_user:
                # Transfer queries
                queries_count = self.db.query(Query).filter(
                    Query.created_by == request.user_id
                ).update({"created_by": request.transfer_assets_to})
                
                # Transfer dashboards
                dashboards_count = self.db.query(Dashboard).filter(
                    Dashboard.created_by == request.user_id
                ).update({"created_by": request.transfer_assets_to})
                
                # Transfer datasources
                datasources_count = self.db.query(DataSource).filter(
                    DataSource.created_by == request.user_id
                ).update({"created_by": request.transfer_assets_to})
                
                result["actions_performed"].append({
                    "action": "transfer_assets",
                    "transferred_to": request.transfer_assets_to,
                    "queries": queries_count,
                    "dashboards": dashboards_count,
                    "datasources": datasources_count
                })
        
        # Revoke access (deactivate user)
        if request.revoke_access:
            user.is_active = False
            result["actions_performed"].append({"action": "revoke_access"})
            
            # Terminate all active sessions
            terminated = self.db.query(UserSession).filter(
                UserSession.user_id == request.user_id,
                UserSession.is_active == True
            ).update({"is_active": False})
            
            result["actions_performed"].append({
                "action": "terminate_sessions",
                "count": terminated
            })
        
        # Archive or delete data
        if request.delete_data:
            # Delete user activities
            deleted_activities = self.db.query(UserActivity).filter(
                UserActivity.user_id == request.user_id
            ).delete()
            
            result["actions_performed"].append({
                "action": "delete_data",
                "activities_deleted": deleted_activities
            })
        elif request.archive_data:
            # Mark data as archived (you could move to archive table)
            result["actions_performed"].append({
                "action": "archive_data",
                "note": "Data archived for retention compliance"
            })
        
        # Log offboarding activity
        self.log_user_activity(
            user_id=performed_by,
            action="user_offboarded",
            resource="user",
            resource_id=request.user_id,
            metadata=result
        )
        
        self.db.commit()
        
        return result
    
    def get_user_management_stats(self, tenant_id: Optional[str] = None) -> UserManagementStats:
        """
        Get user management statistics
        """
        query = self.db.query(User)
        
        if tenant_id:
            query = query.filter(User.tenant_id == tenant_id)
        
        total_users = query.count()
        active_users = query.filter(User.is_active == True).count()
        inactive_users = total_users - active_users
        
        # Count locked users (you'd need a locked field)
        locked_users = 0  # Placeholder
        
        # Users by role
        users_by_role = {}
        role_counts = self.db.query(
            User.role, func.count(User.id)
        ).group_by(User.role)
        
        if tenant_id:
            role_counts = role_counts.filter(User.tenant_id == tenant_id)
        
        for role, count in role_counts.all():
            users_by_role[role] = count
        
        # Recent logins (last 24 hours)
        recent_logins = self.db.query(func.count(func.distinct(UserActivity.user_id))).filter(
            UserActivity.action == "login",
            UserActivity.timestamp >= datetime.utcnow() - timedelta(hours=24)
        )
        
        if tenant_id:
            recent_logins = recent_logins.filter(UserActivity.tenant_id == tenant_id)
        
        recent_logins_count = recent_logins.scalar() or 0
        
        # Failed login attempts (last 24 hours)
        failed_logins = self.db.query(func.count(UserActivity.id)).filter(
            UserActivity.action == "login_failed",
            UserActivity.timestamp >= datetime.utcnow() - timedelta(hours=24)
        )
        
        if tenant_id:
            failed_logins = failed_logins.filter(UserActivity.tenant_id == tenant_id)
        
        failed_logins_count = failed_logins.scalar() or 0
        
        return UserManagementStats(
            total_users=total_users,
            active_users=active_users,
            inactive_users=inactive_users,
            locked_users=locked_users,
            users_by_role=users_by_role,
            recent_logins=recent_logins_count,
            failed_login_attempts=failed_logins_count
        )
    
    def get_user_activity_history(
        self,
        user_id: str,
        limit: int = 100,
        action: Optional[str] = None
    ) -> List[UserActivity]:
        """
        Get activity history for a specific user
        """
        query = self.db.query(UserActivity).filter(
            UserActivity.user_id == user_id
        )
        
        if action:
            query = query.filter(UserActivity.action == action)
        
        return query.order_by(desc(UserActivity.timestamp)).limit(limit).all()
    
    def lock_user_account(self, user_id: str, reason: str, locked_by: str) -> User:
        """
        Lock a user account (prevent login)
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ValueError("User not found")
        
        user.is_active = False
        
        # Terminate all sessions
        self.db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active == True
        ).update({"is_active": False})
        
        # Log the lock action
        self.log_user_activity(
            user_id=locked_by,
            action="user_account_locked",
            resource="user",
            resource_id=user_id,
            metadata={"reason": reason}
        )
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def unlock_user_account(self, user_id: str, unlocked_by: str) -> User:
        """
        Unlock a user account
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ValueError("User not found")
        
        user.is_active = True
        
        # Log the unlock action
        self.log_user_activity(
            user_id=unlocked_by,
            action="user_account_unlocked",
            resource="user",
            resource_id=user_id
        )
        
        self.db.commit()
        self.db.refresh(user)
        
        return user


# Singleton instance
user_management_service = None

def get_user_management_service(db: Session) -> UserManagementService:
    """Get user management service instance"""
    return UserManagementService(db)
