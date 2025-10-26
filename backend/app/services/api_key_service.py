import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from ..models.api_key import APIKey, APIKeyUsageLog
from ..schemas.api_key import APIKeyCreate, APIKeyUpdate, APIKeyUsageStats
from ..core.security import get_password_hash, verify_password
from fastapi import HTTPException, status

class APIKeyService:
    """Service for managing API keys"""
    
    @staticmethod
    def generate_api_key() -> tuple[str, str]:
        """
        Generate a secure API key
        Returns: (full_key, key_prefix)
        """
        # Generate 32-byte random key
        random_part = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        
        # Add prefix for easy identification
        full_key = f"nexbii_{random_part}"
        key_prefix = full_key[:15]  # First 15 chars for display
        
        return full_key, key_prefix
    
    @staticmethod
    def create_api_key(
        db: Session,
        user_id: str,
        tenant_id: str,
        api_key_data: APIKeyCreate
    ) -> tuple[APIKey, str]:
        """
        Create a new API key
        Returns: (api_key_object, plain_text_key)
        """
        # Generate key
        full_key, key_prefix = APIKeyService.generate_api_key()
        key_hash = get_password_hash(full_key)
        
        # Create API key object
        api_key = APIKey(
            user_id=user_id,
            tenant_id=tenant_id,
            name=api_key_data.name,
            description=api_key_data.description,
            key_prefix=key_prefix,
            key_hash=key_hash,
            scopes=api_key_data.scopes,
            rate_limit_per_minute=api_key_data.rate_limit_per_minute,
            rate_limit_per_hour=api_key_data.rate_limit_per_hour,
            rate_limit_per_day=api_key_data.rate_limit_per_day,
            expires_at=api_key_data.expires_at,
            is_active=True,
            request_count=0
        )
        
        db.add(api_key)
        db.commit()
        db.refresh(api_key)
        
        return api_key, full_key
    
    @staticmethod
    def get_api_keys(
        db: Session,
        user_id: str,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        include_inactive: bool = False
    ) -> List[APIKey]:
        """Get all API keys for a user"""
        query = db.query(APIKey).filter(
            APIKey.user_id == user_id,
            APIKey.tenant_id == tenant_id
        )
        
        if not include_inactive:
            query = query.filter(APIKey.is_active == True)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_api_key_by_id(
        db: Session,
        api_key_id: str,
        user_id: str,
        tenant_id: str
    ) -> Optional[APIKey]:
        """Get a specific API key by ID"""
        return db.query(APIKey).filter(
            APIKey.id == api_key_id,
            APIKey.user_id == user_id,
            APIKey.tenant_id == tenant_id
        ).first()
    
    @staticmethod
    def verify_api_key(db: Session, key_string: str) -> Optional[APIKey]:
        """
        Verify an API key and return the API key object
        Returns None if key is invalid or expired
        """
        # Extract prefix to narrow down search
        if not key_string.startswith("nexbii_"):
            return None
        
        key_prefix = key_string[:15]
        
        # Find API key by prefix
        api_keys = db.query(APIKey).filter(
            APIKey.key_prefix == key_prefix,
            APIKey.is_active == True
        ).all()
        
        # Verify hash
        for api_key in api_keys:
            if verify_password(key_string, api_key.key_hash):
                # Check if expired
                if api_key.is_expired():
                    return None
                
                # Update last used
                api_key.last_used_at = datetime.utcnow()
                api_key.request_count += 1
                db.commit()
                
                return api_key
        
        return None
    
    @staticmethod
    def update_api_key(
        db: Session,
        api_key_id: str,
        user_id: str,
        tenant_id: str,
        update_data: APIKeyUpdate
    ) -> APIKey:
        """Update an API key"""
        api_key = APIKeyService.get_api_key_by_id(db, api_key_id, user_id, tenant_id)
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(api_key, field, value)
        
        db.commit()
        db.refresh(api_key)
        return api_key
    
    @staticmethod
    def delete_api_key(
        db: Session,
        api_key_id: str,
        user_id: str,
        tenant_id: str
    ) -> bool:
        """Delete (revoke) an API key"""
        api_key = APIKeyService.get_api_key_by_id(db, api_key_id, user_id, tenant_id)
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        
        # Soft delete by deactivating
        api_key.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def rotate_api_key(
        db: Session,
        api_key_id: str,
        user_id: str,
        tenant_id: str
    ) -> tuple[APIKey, str]:
        """
        Rotate an API key (generate new key, keep same settings)
        Returns: (updated_api_key, new_plain_text_key)
        """
        api_key = APIKeyService.get_api_key_by_id(db, api_key_id, user_id, tenant_id)
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        
        # Generate new key
        full_key, key_prefix = APIKeyService.generate_api_key()
        key_hash = get_password_hash(full_key)
        
        # Update API key
        api_key.key_prefix = key_prefix
        api_key.key_hash = key_hash
        api_key.request_count = 0
        api_key.last_used_at = None
        api_key.last_used_ip = None
        
        db.commit()
        db.refresh(api_key)
        
        return api_key, full_key
    
    @staticmethod
    def log_api_key_usage(
        db: Session,
        api_key_id: str,
        endpoint: str,
        method: str,
        status_code: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        response_time_ms: Optional[int] = None
    ):
        """Log API key usage for analytics"""
        log_entry = APIKeyUsageLog(
            api_key_id=api_key_id,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            ip_address=ip_address,
            user_agent=user_agent,
            response_time_ms=response_time_ms
        )
        
        db.add(log_entry)
        
        # Update API key's last used info
        api_key = db.query(APIKey).filter(APIKey.id == api_key_id).first()
        if api_key:
            api_key.last_used_at = datetime.utcnow()
            api_key.last_used_ip = ip_address
        
        db.commit()
    
    @staticmethod
    def get_api_key_usage_stats(
        db: Session,
        api_key_id: str,
        user_id: str,
        tenant_id: str
    ) -> APIKeyUsageStats:
        """Get usage statistics for an API key"""
        # Verify ownership
        api_key = APIKeyService.get_api_key_by_id(db, api_key_id, user_id, tenant_id)
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        
        now = datetime.utcnow()
        
        # Total requests
        total_requests = api_key.request_count
        
        # Requests in last 24 hours
        requests_24h = db.query(func.count(APIKeyUsageLog.id)).filter(
            APIKeyUsageLog.api_key_id == api_key_id,
            APIKeyUsageLog.created_at >= now - timedelta(hours=24)
        ).scalar() or 0
        
        # Requests in last 7 days
        requests_7d = db.query(func.count(APIKeyUsageLog.id)).filter(
            APIKeyUsageLog.api_key_id == api_key_id,
            APIKeyUsageLog.created_at >= now - timedelta(days=7)
        ).scalar() or 0
        
        # Requests in last 30 days
        requests_30d = db.query(func.count(APIKeyUsageLog.id)).filter(
            APIKeyUsageLog.api_key_id == api_key_id,
            APIKeyUsageLog.created_at >= now - timedelta(days=30)
        ).scalar() or 0
        
        # Average response time
        avg_response_time = db.query(func.avg(APIKeyUsageLog.response_time_ms)).filter(
            APIKeyUsageLog.api_key_id == api_key_id,
            APIKeyUsageLog.response_time_ms.isnot(None),
            APIKeyUsageLog.created_at >= now - timedelta(days=7)
        ).scalar()
        
        # Error rate (4xx and 5xx status codes)
        error_count = db.query(func.count(APIKeyUsageLog.id)).filter(
            APIKeyUsageLog.api_key_id == api_key_id,
            APIKeyUsageLog.status_code >= 400,
            APIKeyUsageLog.created_at >= now - timedelta(days=7)
        ).scalar() or 0
        
        error_rate = (error_count / requests_7d * 100) if requests_7d > 0 else 0
        
        # Most used endpoints
        most_used = db.query(
            APIKeyUsageLog.endpoint,
            APIKeyUsageLog.method,
            func.count(APIKeyUsageLog.id).label('count')
        ).filter(
            APIKeyUsageLog.api_key_id == api_key_id,
            APIKeyUsageLog.created_at >= now - timedelta(days=7)
        ).group_by(
            APIKeyUsageLog.endpoint,
            APIKeyUsageLog.method
        ).order_by(
            func.count(APIKeyUsageLog.id).desc()
        ).limit(10).all()
        
        most_used_endpoints = [
            {
                "endpoint": endpoint,
                "method": method,
                "count": count
            }
            for endpoint, method, count in most_used
        ]
        
        return APIKeyUsageStats(
            api_key_id=api_key_id,
            total_requests=total_requests,
            requests_last_24h=requests_24h,
            requests_last_7d=requests_7d,
            requests_last_30d=requests_30d,
            avg_response_time_ms=avg_response_time,
            error_rate=error_rate,
            most_used_endpoints=most_used_endpoints
        )
