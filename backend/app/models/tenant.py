from sqlalchemy import Column, String, JSON, Boolean, DateTime, Integer, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from ..core.database import Base

class Tenant(Base):
    """
    Multi-tenancy support for SaaS deployment.
    Each tenant represents an organization/company using the platform.
    """
    __tablename__ = "tenants"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, index=True)  # Organization name
    slug = Column(String, unique=True, nullable=False, index=True)  # URL-friendly identifier
    
    # Contact & Billing
    contact_email = Column(String, nullable=False)
    contact_name = Column(String)
    
    # Subscription & Limits
    plan = Column(String, default="free")  # free, starter, professional, enterprise
    is_active = Column(Boolean, default=True)
    max_users = Column(Integer, default=5)
    max_datasources = Column(Integer, default=3)
    max_dashboards = Column(Integer, default=10)
    max_queries = Column(Integer, default=100)
    
    # Storage limits (in MB)
    storage_limit_mb = Column(Integer, default=1000)
    storage_used_mb = Column(Integer, default=0)
    
    # Feature flags
    features = Column(JSON, default=dict)  # {"ai_enabled": true, "advanced_analytics": true}
    
    # White-labeling
    branding = Column(JSON, default=dict)  # Logo URL, colors, fonts
    custom_domain = Column(String, nullable=True)  # custom.example.com
    
    # Settings
    settings = Column(JSON, default=dict)  # Tenant-specific configuration
    extra_metadata = Column(JSON, default=dict)  # Additional metadata (renamed from metadata)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)
    suspended_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships (users, datasources, etc. will have tenant_id foreign key)
    
    def __repr__(self):
        return f"<Tenant {self.name} ({self.slug})>"


class TenantDomain(Base):
    """
    Custom domains for tenant white-labeling.
    Allows tenants to use their own domain (e.g., analytics.company.com)
    """
    __tablename__ = "tenant_domains"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=False, index=True)
    domain = Column(String, unique=True, nullable=False, index=True)
    is_verified = Column(Boolean, default=False)
    is_primary = Column(Boolean, default=False)
    
    # SSL/TLS
    ssl_enabled = Column(Boolean, default=False)
    ssl_certificate = Column(Text, nullable=True)  # PEM format
    ssl_private_key = Column(Text, nullable=True)  # Encrypted
    
    # DNS verification
    verification_token = Column(String)
    verification_method = Column(String, default="cname")  # cname, txt, http
    verified_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<TenantDomain {self.domain}>"


class TenantInvitation(Base):
    """
    Invitations for users to join a tenant.
    """
    __tablename__ = "tenant_invitations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=False, index=True)
    email = Column(String, nullable=False, index=True)
    role = Column(String, default="viewer")  # admin, editor, viewer
    invited_by = Column(String)  # User ID
    
    token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<TenantInvitation {self.email}>"


class TenantUsage(Base):
    """
    Track tenant resource usage for billing and limits enforcement.
    """
    __tablename__ = "tenant_usage"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=False, index=True)
    
    # Usage metrics
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    queries_executed = Column(Integer, default=0)
    dashboards_viewed = Column(Integer, default=0)
    api_calls = Column(Integer, default=0)
    storage_used_mb = Column(Integer, default=0)
    users_active = Column(Integer, default=0)
    
    # AI/Advanced features usage
    ai_queries = Column(Integer, default=0)
    analytics_runs = Column(Integer, default=0)
    exports_generated = Column(Integer, default=0)
    
    # Billing
    billable_amount = Column(Integer, default=0)  # In cents
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<TenantUsage {self.tenant_id} {self.period_start}>"
