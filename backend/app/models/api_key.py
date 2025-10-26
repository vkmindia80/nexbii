from sqlalchemy import Column, String, Boolean, DateTime, Integer, JSON, Index
from sqlalchemy.sql import func
import uuid
from ..core.database import Base

class APIKey(Base):
    """API Key model for programmatic access to the platform"""
    __tablename__ = "api_keys"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Ownership
    tenant_id = Column(String, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=False)
    
    # Key details
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    key_prefix = Column(String(8), nullable=False, index=True)  # First 8 chars for display (e.g., "nexbii_1")
    key_hash = Column(String, nullable=False, unique=True, index=True)  # Bcrypt hash of full key
    
    # Permissions
    scopes = Column(JSON, nullable=False, default=list)  # List of scope strings
    # Available scopes:
    # - read:datasources, write:datasources
    # - read:queries, write:queries, execute:queries
    # - read:dashboards, write:dashboards
    # - read:users, write:users
    # - read:analytics, execute:analytics
    # - admin:* (full access)
    
    # Rate limiting
    rate_limit_per_minute = Column(Integer, default=60)  # Requests per minute
    rate_limit_per_hour = Column(Integer, default=1000)  # Requests per hour
    rate_limit_per_day = Column(Integer, default=10000)  # Requests per day
    
    # Status
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)  # Optional expiration
    
    # Usage tracking
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    last_used_ip = Column(String, nullable=True)
    request_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_api_key_tenant_user', 'tenant_id', 'user_id'),
        Index('idx_api_key_active', 'is_active', 'expires_at'),
    )
    
    def is_expired(self):
        """Check if API key is expired"""
        if self.expires_at is None:
            return False
        from datetime import datetime
        return datetime.utcnow() > self.expires_at
    
    def has_scope(self, required_scope: str) -> bool:
        """Check if API key has a specific scope"""
        if not self.scopes:
            return False
        
        # Admin scope grants all permissions
        if "admin:*" in self.scopes:
            return True
        
        # Check exact scope match
        if required_scope in self.scopes:
            return True
        
        # Check wildcard scopes (e.g., "write:*" grants all write permissions)
        scope_parts = required_scope.split(':')
        if len(scope_parts) == 2:
            wildcard_scope = f"{scope_parts[0]}:*"
            if wildcard_scope in self.scopes:
                return True
        
        return False


class APIKeyUsageLog(Base):
    """Log API key usage for analytics and debugging"""
    __tablename__ = "api_key_usage_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    api_key_id = Column(String, index=True, nullable=False)
    
    # Request details
    endpoint = Column(String, nullable=False)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, nullable=False)
    
    # Client info
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    # Performance
    response_time_ms = Column(Integer, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_api_key_usage_key_time', 'api_key_id', 'created_at'),
    )
