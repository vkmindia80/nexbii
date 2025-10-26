from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
import re

# ========== Tenant Schemas ==========

class TenantBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Organization name")
    contact_email: EmailStr
    contact_name: Optional[str] = None

class TenantCreate(TenantBase):
    slug: Optional[str] = Field(None, description="URL-friendly identifier (auto-generated if not provided)")
    plan: Optional[str] = Field("free", description="Subscription plan")
    
    @validator('slug')
    def validate_slug(cls, v):
        if v:
            if not re.match(r'^[a-z0-9-]+$', v):
                raise ValueError('Slug must contain only lowercase letters, numbers, and hyphens')
            if len(v) < 3 or len(v) > 50:
                raise ValueError('Slug must be between 3 and 50 characters')
        return v

class TenantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    contact_email: Optional[EmailStr] = None
    contact_name: Optional[str] = None
    plan: Optional[str] = None
    is_active: Optional[bool] = None
    max_users: Optional[int] = None
    max_datasources: Optional[int] = None
    max_dashboards: Optional[int] = None
    max_queries: Optional[int] = None
    storage_limit_mb: Optional[int] = None
    features: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None

class TenantBranding(BaseModel):
    logo_url: Optional[str] = None
    logo_dark_url: Optional[str] = None  # For dark mode
    primary_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    secondary_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    accent_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    font_family: Optional[str] = None
    custom_css: Optional[str] = None
    favicon_url: Optional[str] = None
    
class TenantBrandingUpdate(BaseModel):
    branding: TenantBranding

class Tenant(TenantBase):
    id: str
    slug: str
    plan: str
    is_active: bool
    max_users: int
    max_datasources: int
    max_dashboards: int
    max_queries: int
    storage_limit_mb: int
    storage_used_mb: int
    features: Dict[str, Any]
    branding: Dict[str, Any]
    custom_domain: Optional[str]
    settings: Dict[str, Any]
    extra_metadata: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]
    trial_ends_at: Optional[datetime]
    suspended_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class TenantList(BaseModel):
    """List of tenants with pagination"""
    tenants: List[Tenant]
    total: int
    page: int
    page_size: int

# ========== Tenant Domain Schemas ==========

class TenantDomainBase(BaseModel):
    domain: str = Field(..., description="Custom domain (e.g., analytics.company.com)")
    
    @validator('domain')
    def validate_domain(cls, v):
        # Basic domain validation
        if not re.match(r'^[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,}$', v.lower()):
            raise ValueError('Invalid domain format')
        return v.lower()

class TenantDomainCreate(TenantDomainBase):
    is_primary: Optional[bool] = False

class TenantDomainUpdate(BaseModel):
    is_primary: Optional[bool] = None
    ssl_enabled: Optional[bool] = None

class TenantDomain(TenantDomainBase):
    id: str
    tenant_id: str
    is_verified: bool
    is_primary: bool
    ssl_enabled: bool
    verification_token: Optional[str]
    verification_method: str
    verified_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

# ========== Tenant Invitation Schemas ==========

class TenantInvitationCreate(BaseModel):
    email: EmailStr
    role: str = Field("viewer", description="Role for the invited user")
    
    @validator('role')
    def validate_role(cls, v):
        allowed_roles = ['admin', 'editor', 'viewer']
        if v not in allowed_roles:
            raise ValueError(f'Role must be one of: {", ".join(allowed_roles)}')
        return v

class TenantInvitation(BaseModel):
    id: str
    tenant_id: str
    email: EmailStr
    role: str
    invited_by: str
    token: str
    expires_at: datetime
    accepted_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class TenantInvitationAccept(BaseModel):
    token: str
    full_name: str
    password: str = Field(..., min_length=8)

# ========== Tenant Usage Schemas ==========

class TenantUsageStats(BaseModel):
    """Current usage statistics for a tenant"""
    tenant_id: str
    current_users: int
    current_datasources: int
    current_dashboards: int
    current_queries: int
    storage_used_mb: int
    queries_this_month: int
    dashboards_viewed_this_month: int
    api_calls_this_month: int
    
class TenantUsagePeriod(BaseModel):
    """Historical usage for a specific period"""
    period_start: datetime
    period_end: datetime
    queries_executed: int
    dashboards_viewed: int
    api_calls: int
    storage_used_mb: int
    users_active: int
    ai_queries: int
    analytics_runs: int
    exports_generated: int
    billable_amount: int
    
    class Config:
        from_attributes = True

# ========== Tenant Provisioning ==========

class TenantProvision(BaseModel):
    """Automated tenant provisioning request"""
    organization_name: str = Field(..., min_length=2, max_length=100)
    admin_email: EmailStr
    admin_name: str
    admin_password: str = Field(..., min_length=8)
    plan: Optional[str] = Field("free", description="Subscription plan")
    custom_slug: Optional[str] = None

class TenantProvisionResponse(BaseModel):
    """Response after tenant provisioning"""
    tenant: Tenant
    admin_user_id: str
    login_url: str
    message: str

# ========== Tenant Limits Check ==========

class TenantLimitsCheck(BaseModel):
    """Check if tenant is within limits"""
    within_user_limit: bool
    within_datasource_limit: bool
    within_dashboard_limit: bool
    within_query_limit: bool
    within_storage_limit: bool
    limits_exceeded: List[str] = []
    
class TenantFeatureAccess(BaseModel):
    """Check feature access for tenant"""
    feature: str
    has_access: bool
    reason: Optional[str] = None
