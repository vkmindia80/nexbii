"""
Tenant Context Middleware
Automatically manages tenant context for all requests and ensures data isolation.
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
import contextvars

# Context variable to store current tenant ID
current_tenant_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'current_tenant_id', default=None
)

class TenantContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract and set tenant context from:
    1. Custom domain (e.g., tenant1.nexbii.com)
    2. Subdomain (e.g., tenant1.example.com)
    3. Header (X-Tenant-ID)
    4. User's tenant association
    """
    
    async def dispatch(self, request: Request, call_next):
        tenant_id = None
        
        # Skip tenant context for certain paths
        skip_paths = [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/health",
            "/api/auth/login",
            "/api/auth/register",
            "/api/tenants/provision",  # Public provisioning endpoint
            "/socket.io",
        ]
        
        if any(request.url.path.startswith(path) for path in skip_paths):
            return await call_next(request)
        
        # Method 1: Check custom domain mapping
        host = request.headers.get("host", "").split(":")[0]
        if host and not host.startswith("localhost") and not host.startswith("127.0.0.1"):
            tenant_id = await self.get_tenant_by_domain(host)
        
        # Method 2: Check X-Tenant-ID header (for API access)
        if not tenant_id:
            tenant_id = request.headers.get("X-Tenant-ID")
        
        # Method 3: Extract from subdomain
        if not tenant_id and "." in host:
            subdomain = host.split(".")[0]
            if subdomain not in ["www", "api", "admin"]:
                tenant_id = await self.get_tenant_by_slug(subdomain)
        
        # Method 4: Get from authenticated user's tenant
        if not tenant_id and hasattr(request.state, "user"):
            tenant_id = getattr(request.state.user, "tenant_id", None)
        
        # Set tenant context
        if tenant_id:
            current_tenant_id.set(tenant_id)
            request.state.tenant_id = tenant_id
        
        response = await call_next(request)
        return response
    
    async def get_tenant_by_domain(self, domain: str) -> Optional[str]:
        """Look up tenant by custom domain"""
        from app.core.database import SessionLocal
        from app.models.tenant import TenantDomain
        
        db = SessionLocal()
        try:
            tenant_domain = db.query(TenantDomain).filter(
                TenantDomain.domain == domain,
                TenantDomain.is_verified == True
            ).first()
            return tenant_domain.tenant_id if tenant_domain else None
        finally:
            db.close()
    
    async def get_tenant_by_slug(self, slug: str) -> Optional[str]:
        """Look up tenant by slug"""
        from app.core.database import SessionLocal
        from app.models.tenant import Tenant
        
        db = SessionLocal()
        try:
            tenant = db.query(Tenant).filter(
                Tenant.slug == slug,
                Tenant.is_active == True
            ).first()
            return tenant.id if tenant else None
        finally:
            db.close()


def get_current_tenant_id() -> Optional[str]:
    """Get current tenant ID from context"""
    return current_tenant_id.get()


def require_tenant_context():
    """Dependency to ensure tenant context is set"""
    tenant_id = get_current_tenant_id()
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant context is required for this operation"
        )
    return tenant_id


class TenantQueryFilter:
    """
    Mixin to automatically filter queries by tenant.
    Add this to database queries to ensure tenant isolation.
    """
    
    @staticmethod
    def filter_by_tenant(query, model):
        """Apply tenant filter to SQLAlchemy query"""
        tenant_id = get_current_tenant_id()
        if tenant_id and hasattr(model, 'tenant_id'):
            return query.filter(model.tenant_id == tenant_id)
        return query
    
    @staticmethod
    def check_tenant_access(obj) -> bool:
        """Check if current tenant has access to object"""
        tenant_id = get_current_tenant_id()
        if not tenant_id:
            return True  # No tenant context, allow access
        if not hasattr(obj, 'tenant_id'):
            return True  # Object not tenant-scoped
        return obj.tenant_id == tenant_id
    
    @staticmethod
    def set_tenant_on_create(obj):
        """Automatically set tenant_id when creating objects"""
        tenant_id = get_current_tenant_id()
        if tenant_id and hasattr(obj, 'tenant_id'):
            obj.tenant_id = tenant_id


def enforce_tenant_limits(tenant_id: str, resource_type: str) -> None:
    """
    Check if tenant is within limits for creating new resources.
    Raises HTTPException if limit exceeded.
    """
    from app.core.database import SessionLocal
    from app.models.tenant import Tenant
    
    db = SessionLocal()
    try:
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        if not tenant.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tenant account is suspended"
            )
        
        # Check resource-specific limits
        from app.models.user import User
        from app.models.datasource import DataSource
        from app.models.dashboard import Dashboard
        from app.models.query import Query
        
        if resource_type == "user":
            count = db.query(User).filter(User.tenant_id == tenant_id).count()
            if count >= tenant.max_users:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"User limit reached ({tenant.max_users}). Please upgrade your plan."
                )
        
        elif resource_type == "datasource":
            count = db.query(DataSource).filter(DataSource.tenant_id == tenant_id).count()
            if count >= tenant.max_datasources:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Data source limit reached ({tenant.max_datasources}). Please upgrade your plan."
                )
        
        elif resource_type == "dashboard":
            count = db.query(Dashboard).filter(Dashboard.tenant_id == tenant_id).count()
            if count >= tenant.max_dashboards:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Dashboard limit reached ({tenant.max_dashboards}). Please upgrade your plan."
                )
        
        elif resource_type == "query":
            count = db.query(Query).filter(Query.tenant_id == tenant_id).count()
            if count >= tenant.max_queries:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Query limit reached ({tenant.max_queries}). Please upgrade your plan."
                )
    
    finally:
        db.close()


def check_tenant_feature(tenant_id: str, feature: str) -> bool:
    """Check if tenant has access to a specific feature"""
    from app.core.database import SessionLocal
    from app.models.tenant import Tenant
    
    db = SessionLocal()
    try:
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            return False
        
        return tenant.features.get(feature, False)
    finally:
        db.close()
