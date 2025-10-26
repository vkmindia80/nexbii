"""
GDPR Compliance Service
Implements GDPR tools: data export, right to be forgotten, consent management
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.security import ConsentRecord
from datetime import datetime
import uuid
import json


class GDPRService:
    """Service for GDPR compliance"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def export_user_data(self, user: User) -> Dict[str, Any]:
        """
        Export all user data for GDPR compliance
        
        Returns comprehensive data package including:
        - User profile
        - Data sources
        - Queries
        - Dashboards
        - Activity logs
        - Consent records
        """
        data = {
            "user_profile": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "is_active": user.is_active
            },
            "data_sources": [],
            "queries": [],
            "dashboards": [],
            "activity_logs": [],
            "consent_records": [],
            "exported_at": datetime.utcnow().isoformat()
        }
        
        # Get user's data sources
        from app.models.datasource import DataSource
        datasources = self.db.query(DataSource).filter(
            DataSource.created_by == user.id
        ).all()
        
        for ds in datasources:
            data["data_sources"].append({
                "id": ds.id,
                "name": ds.name,
                "type": ds.type,
                "created_at": ds.created_at.isoformat() if ds.created_at else None
            })
        
        # Get user's queries
        from app.models.query import Query
        queries = self.db.query(Query).filter(
            Query.created_by == user.id
        ).all()
        
        for q in queries:
            data["queries"].append({
                "id": q.id,
                "name": q.name,
                "sql": q.sql,
                "created_at": q.created_at.isoformat() if q.created_at else None
            })
        
        # Get user's dashboards
        from app.models.dashboard import Dashboard
        dashboards = self.db.query(Dashboard).filter(
            Dashboard.created_by == user.id
        ).all()
        
        for d in dashboards:
            data["dashboards"].append({
                "id": d.id,
                "name": d.name,
                "description": d.description,
                "created_at": d.created_at.isoformat() if d.created_at else None
            })
        
        # Get user's audit logs
        from app.models.security import AuditLog
        logs = self.db.query(AuditLog).filter(
            AuditLog.user_id == user.id
        ).order_by(AuditLog.created_at.desc()).limit(1000).all()
        
        for log in logs:
            data["activity_logs"].append({
                "event_type": log.event_type,
                "action": log.action,
                "status": log.status,
                "created_at": log.created_at.isoformat() if log.created_at else None
            })
        
        # Get consent records
        consents = self.db.query(ConsentRecord).filter(
            ConsentRecord.user_id == user.id
        ).all()
        
        for consent in consents:
            data["consent_records"].append({
                "consent_type": consent.consent_type,
                "version": consent.version,
                "is_granted": consent.is_granted,
                "granted_at": consent.granted_at.isoformat() if consent.granted_at else None,
                "revoked_at": consent.revoked_at.isoformat() if consent.revoked_at else None
            })
        
        return data
    
    def delete_user_data(self, user: User) -> Dict[str, Any]:
        """
        Delete all user data (Right to be Forgotten)
        
        This is irreversible!
        
        Returns:
            Summary of deleted data
        """
        summary = {
            "user_id": user.id,
            "email": user.email,
            "deleted_at": datetime.utcnow().isoformat(),
            "items_deleted": {}
        }
        
        # Delete data sources
        from app.models.datasource import DataSource
        ds_count = self.db.query(DataSource).filter(
            DataSource.created_by == user.id
        ).delete()
        summary["items_deleted"]["data_sources"] = ds_count
        
        # Delete queries
        from app.models.query import Query
        q_count = self.db.query(Query).filter(
            Query.created_by == user.id
        ).delete()
        summary["items_deleted"]["queries"] = q_count
        
        # Delete dashboards
        from app.models.dashboard import Dashboard
        d_count = self.db.query(Dashboard).filter(
            Dashboard.created_by == user.id
        ).delete()
        summary["items_deleted"]["dashboards"] = d_count
        
        # Anonymize audit logs (don't delete for compliance)
        from app.models.security import AuditLog
        logs = self.db.query(AuditLog).filter(
            AuditLog.user_id == user.id
        ).all()
        
        for log in logs:
            log.username = "[DELETED USER]"
            log.user_id = None
        
        summary["items_deleted"]["audit_logs_anonymized"] = len(logs)
        
        # Delete consent records
        consent_count = self.db.query(ConsentRecord).filter(
            ConsentRecord.user_id == user.id
        ).delete()
        summary["items_deleted"]["consent_records"] = consent_count
        
        # Delete MFA config
        from app.models.security import MFAConfig
        mfa_count = self.db.query(MFAConfig).filter(
            MFAConfig.user_id == user.id
        ).delete()
        summary["items_deleted"]["mfa_configs"] = mfa_count
        
        # Finally, delete the user
        self.db.delete(user)
        self.db.commit()
        
        return summary
    
    def record_consent(
        self,
        user: User,
        consent_type: str,
        version: str,
        is_granted: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> ConsentRecord:
        """
        Record user consent
        
        Args:
            user: User giving consent
            consent_type: Type (terms_of_service, privacy_policy, marketing)
            version: Version of the policy
            is_granted: Whether consent is granted
            ip_address: IP address
            user_agent: User agent
        """
        consent = ConsentRecord(
            id=str(uuid.uuid4()),
            user_id=user.id,
            tenant_id=user.tenant_id,
            consent_type=consent_type,
            version=version,
            is_granted=is_granted,
            granted_at=datetime.utcnow() if is_granted else None,
            revoked_at=datetime.utcnow() if not is_granted else None,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.db.add(consent)
        self.db.commit()
        self.db.refresh(consent)
        
        return consent
    
    def get_consents(self, user: User) -> List[ConsentRecord]:
        """Get all consent records for user"""
        return self.db.query(ConsentRecord).filter(
            ConsentRecord.user_id == user.id
        ).order_by(ConsentRecord.created_at.desc()).all()
    
    def revoke_consent(
        self, user: User, consent_type: str
    ) -> Optional[ConsentRecord]:
        """Revoke a specific consent"""
        consent = self.db.query(ConsentRecord).filter(
            ConsentRecord.user_id == user.id,
            ConsentRecord.consent_type == consent_type,
            ConsentRecord.is_granted == True
        ).first()
        
        if consent:
            consent.is_granted = False
            consent.revoked_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(consent)
        
        return consent
