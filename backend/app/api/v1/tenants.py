"""
Tenant Management API
Handles tenant CRUD operations, provisioning, and administration.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import secrets
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user, get_password_hash
from app.models.user import User, UserRole
from app.models.tenant import Tenant, TenantDomain, TenantInvitation, TenantUsage
from app.schemas.tenant import (
    TenantCreate, TenantUpdate, Tenant as TenantSchema, TenantList,
    TenantProvision, TenantProvisionResponse,
    TenantDomainCreate, TenantDomain as TenantDomainSchema,
    TenantInvitationCreate, TenantInvitation as TenantInvitationSchema,
    TenantInvitationAccept, TenantUsageStats, TenantBrandingUpdate,
    TenantLimitsCheck, TenantFeatureAccess
)
from app.core.tenant_context import (
    get_current_tenant_id, require_tenant_context,
    enforce_tenant_limits, check_tenant_feature
)

router = APIRouter()

# ========== Helper Functions ==========

def generate_slug(name: str, db: Session) -> str:
    """Generate a unique slug from tenant name"""
    import re
    base_slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    base_slug = base_slug[:50]  # Max 50 chars
    
    slug = base_slug
    counter = 1
    while db.query(Tenant).filter(Tenant.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    return slug


def check_admin_access(current_user: User, tenant_id: str):
    """Verify user is admin of the tenant"""
    if current_user.role != UserRole.ADMIN or current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only tenant administrators can perform this action"
        )


# ========== Public Endpoints ==========

@router.post("/provision", response_model=TenantProvisionResponse, tags=["Public"])
async def provision_tenant(
    provision: TenantProvision,
    db: Session = Depends(get_db)
):
    """
    🚀 Automated tenant provisioning (public endpoint for signups).
    Creates tenant + admin user in one request.
    """
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == provision.admin_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Generate or validate slug
    slug = provision.custom_slug or generate_slug(provision.organization_name, db)
    
    # Check slug availability
    if db.query(Tenant).filter(Tenant.slug == slug).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Slug '{slug}' is already taken"
        )
    
    # Create tenant
    tenant = Tenant(
        id=str(uuid.uuid4()),
        name=provision.organization_name,
        slug=slug,
        contact_email=provision.admin_email,
        contact_name=provision.admin_name,
        plan=provision.plan,
        is_active=True,
        features={
            "ai_enabled": provision.plan in ["professional", "enterprise"],
            "advanced_analytics": provision.plan in ["professional", "enterprise"],
            "white_labeling": provision.plan == "enterprise",
            "api_access": True
        },
        trial_ends_at=datetime.utcnow() + timedelta(days=30) if provision.plan == "free" else None
    )
    db.add(tenant)
    db.flush()
    
    # Create admin user
    admin_user = User(
        id=str(uuid.uuid4()),
        email=provision.admin_email,
        hashed_password=get_password_hash(provision.admin_password),
        full_name=provision.admin_name,
        role=UserRole.ADMIN,
        is_active=True,
        tenant_id=tenant.id
    )
    db.add(admin_user)
    
    db.commit()
    db.refresh(tenant)
    
    # Generate login URL
    login_url = f"https://{slug}.nexbii.com/login" if slug != "demo" else "http://localhost:3000/login"
    
    return {
        "tenant": tenant,
        "admin_user_id": admin_user.id,
        "login_url": login_url,
        "message": f"Tenant '{tenant.name}' created successfully! Admin user can now log in."
    }


# ========== Tenant CRUD ==========

@router.get("/", response_model=TenantList)
async def list_tenants(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    📋 List all tenants (platform admin only).
    """
    # Only platform super admin can list all tenants
    if current_user.role != UserRole.ADMIN or current_user.tenant_id is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires platform administrator access"
        )
    
    tenants = db.query(Tenant).offset(skip).limit(limit).all()
    total = db.query(Tenant).count()
    
    return {
        "tenants": tenants,
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit
    }


@router.get("/current", response_model=TenantSchema)
async def get_current_tenant(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🏢 Get current user's tenant information.
    """
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not associated with any tenant"
        )
    
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    return tenant


@router.get("/{tenant_id}", response_model=TenantSchema)
async def get_tenant(
    tenant_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    📖 Get tenant by ID.
    """
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Check access
    if current_user.tenant_id != tenant_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return tenant


@router.put("/{tenant_id}", response_model=TenantSchema)
async def update_tenant(
    tenant_id: str,
    tenant_update: TenantUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ✏️ Update tenant settings (admin only).
    """
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    check_admin_access(current_user, tenant_id)
    
    # Update fields
    update_data = tenant_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tenant, field, value)
    
    tenant.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(tenant)
    
    return tenant


@router.put("/{tenant_id}/branding", response_model=TenantSchema)
async def update_tenant_branding(
    tenant_id: str,
    branding_update: TenantBrandingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🎨 Update tenant branding (white-labeling).
    """
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    check_admin_access(current_user, tenant_id)
    
    # Check white-labeling feature access
    if not check_tenant_feature(tenant_id, "white_labeling"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="White-labeling feature not available in your plan"
        )
    
    tenant.branding = branding_update.branding.dict(exclude_none=True)
    tenant.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(tenant)
    
    return tenant


@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant(
    tenant_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🗑️ Delete tenant (soft delete by deactivating).
    """
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    check_admin_access(current_user, tenant_id)
    
    # Soft delete
    tenant.is_active = False
    tenant.suspended_at = datetime.utcnow()
    db.commit()
    
    return None


# ========== Tenant Limits & Usage ==========

@router.get("/{tenant_id}/limits", response_model=TenantLimitsCheck)
async def check_tenant_limits(
    tenant_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    📊 Check tenant resource limits.
    """
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    
    check_admin_access(current_user, tenant_id)
    
    # Count current resources
    from app.models.datasource import DataSource
    from app.models.dashboard import Dashboard
    from app.models.query import Query
    
    user_count = db.query(User).filter(User.tenant_id == tenant_id).count()
    datasource_count = db.query(DataSource).filter(DataSource.tenant_id == tenant_id).count()
    dashboard_count = db.query(Dashboard).filter(Dashboard.tenant_id == tenant_id).count()
    query_count = db.query(Query).filter(Query.tenant_id == tenant_id).count()
    
    limits_exceeded = []
    if user_count >= tenant.max_users:
        limits_exceeded.append(f"Users ({user_count}/{tenant.max_users})")
    if datasource_count >= tenant.max_datasources:
        limits_exceeded.append(f"Data Sources ({datasource_count}/{tenant.max_datasources})")
    if dashboard_count >= tenant.max_dashboards:
        limits_exceeded.append(f"Dashboards ({dashboard_count}/{tenant.max_dashboards})")
    if query_count >= tenant.max_queries:
        limits_exceeded.append(f"Queries ({query_count}/{tenant.max_queries})")
    if tenant.storage_used_mb >= tenant.storage_limit_mb:
        limits_exceeded.append(f"Storage ({tenant.storage_used_mb}/{tenant.storage_limit_mb} MB)")
    
    return {
        "within_user_limit": user_count < tenant.max_users,
        "within_datasource_limit": datasource_count < tenant.max_datasources,
        "within_dashboard_limit": dashboard_count < tenant.max_dashboards,
        "within_query_limit": query_count < tenant.max_queries,
        "within_storage_limit": tenant.storage_used_mb < tenant.storage_limit_mb,
        "limits_exceeded": limits_exceeded
    }


@router.get("/{tenant_id}/usage", response_model=TenantUsageStats)
async def get_tenant_usage(
    tenant_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    📈 Get tenant usage statistics.
    """
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    
    check_admin_access(current_user, tenant_id)
    
    # Count resources
    from app.models.datasource import DataSource
    from app.models.dashboard import Dashboard
    from app.models.query import Query
    
    # Get current month usage
    from sqlalchemy import func, extract
    now = datetime.utcnow()
    
    usage_record = db.query(TenantUsage).filter(
        TenantUsage.tenant_id == tenant_id,
        extract('month', TenantUsage.period_start) == now.month,
        extract('year', TenantUsage.period_start) == now.year
    ).first()
    
    return {
        "tenant_id": tenant_id,
        "current_users": db.query(User).filter(User.tenant_id == tenant_id, User.is_active == True).count(),
        "current_datasources": db.query(DataSource).filter(DataSource.tenant_id == tenant_id).count(),
        "current_dashboards": db.query(Dashboard).filter(Dashboard.tenant_id == tenant_id).count(),
        "current_queries": db.query(Query).filter(Query.tenant_id == tenant_id).count(),
        "storage_used_mb": tenant.storage_used_mb,
        "queries_this_month": usage_record.queries_executed if usage_record else 0,
        "dashboards_viewed_this_month": usage_record.dashboards_viewed if usage_record else 0,
        "api_calls_this_month": usage_record.api_calls if usage_record else 0
    }


@router.get("/{tenant_id}/features/{feature}", response_model=TenantFeatureAccess)
async def check_feature_access(
    tenant_id: str,
    feature: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🔍 Check if tenant has access to a specific feature.
    """
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    
    has_access = tenant.features.get(feature, False)
    reason = None
    
    if not has_access:
        reason = f"Feature '{feature}' not included in '{tenant.plan}' plan"
    
    return {
        "feature": feature,
        "has_access": has_access,
        "reason": reason
    }


# ========== Custom Domains ==========

@router.post("/{tenant_id}/domains", response_model=TenantDomainSchema)
async def add_custom_domain(
    tenant_id: str,
    domain_create: TenantDomainCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🌐 Add custom domain for tenant.
    """
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    
    check_admin_access(current_user, tenant_id)
    
    # Check if domain already exists
    existing = db.query(TenantDomain).filter(TenantDomain.domain == domain_create.domain).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Domain already registered"
        )
    
    # Create domain
    domain = TenantDomain(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        domain=domain_create.domain,
        is_primary=domain_create.is_primary,
        verification_token=secrets.token_urlsafe(32),
        verification_method="cname"
    )
    db.add(domain)
    db.commit()
    db.refresh(domain)
    
    return domain


@router.get("/{tenant_id}/domains", response_model=List[TenantDomainSchema])
async def list_custom_domains(
    tenant_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    📋 List custom domains for tenant.
    """
    check_admin_access(current_user, tenant_id)
    
    domains = db.query(TenantDomain).filter(TenantDomain.tenant_id == tenant_id).all()
    return domains


# ========== Tenant Invitations ==========

@router.post("/{tenant_id}/invitations", response_model=TenantInvitationSchema)
async def invite_user_to_tenant(
    tenant_id: str,
    invitation: TenantInvitationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ✉️ Invite user to join tenant.
    """
    check_admin_access(current_user, tenant_id)
    
    # Check user limit
    enforce_tenant_limits(tenant_id, "user")
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == invitation.email).first()
    if existing_user and existing_user.tenant_id == tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists in this tenant"
        )
    
    # Create invitation
    invite = TenantInvitation(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        email=invitation.email,
        role=invitation.role,
        invited_by=current_user.id,
        token=secrets.token_urlsafe(32),
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)
    
    # Send invitation email with branding
    from app.services.email_template_service import EmailTemplateService
    from app.services.email_service import EmailService
    
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    invitation_url = f"https://{tenant.slug}.nexbii.com/accept-invitation?token={invite.token}"
    
    email_data = EmailTemplateService.generate_invitation_email(
        invitee_email=invitation.email,
        inviter_name=current_user.full_name,
        organization_name=tenant.name,
        invitation_url=invitation_url,
        role=invitation.role,
        tenant_branding={**tenant.branding, "company_name": tenant.name}
    )
    
    EmailService.send_email(
        to_emails=[invitation.email],
        subject=email_data["subject"],
        html_content=email_data["html"],
        text_content=email_data["text"]
    )
    
    return invite


# ========== DNS Verification & SSL Management ==========

from pydantic import BaseModel

class DomainVerificationRequest(BaseModel):
    """Request to verify domain ownership"""
    pass

class DomainVerificationInstructions(BaseModel):
    """DNS verification instructions"""
    method: str
    title: str
    instructions: str
    record_type: Optional[str] = None
    host: Optional[str] = None
    value: Optional[str] = None

class SSLCertificateUpload(BaseModel):
    """Manual SSL certificate upload"""
    certificate_pem: str
    private_key_pem: str
    chain_pem: Optional[str] = None

class LetsEncryptRequest(BaseModel):
    """Request Let's Encrypt certificate"""
    email: str
    staging: bool = False


@router.get("/{tenant_id}/domains/{domain_id}/verification-instructions", response_model=DomainVerificationInstructions)
async def get_domain_verification_instructions(
    tenant_id: str,
    domain_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    📋 Get DNS verification instructions for custom domain.
    """
    check_admin_access(current_user, tenant_id)
    
    domain = db.query(TenantDomain).filter(
        TenantDomain.id == domain_id,
        TenantDomain.tenant_id == tenant_id
    ).first()
    
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found"
        )
    
    from app.services.dns_verification_service import DNSVerificationService
    
    instructions = DNSVerificationService.get_verification_instructions(
        domain.domain,
        domain.verification_method,
        domain.verification_token
    )
    
    return instructions


@router.post("/{tenant_id}/domains/{domain_id}/verify")
async def verify_custom_domain(
    tenant_id: str,
    domain_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ✅ Verify custom domain ownership via DNS.
    """
    check_admin_access(current_user, tenant_id)
    
    domain = db.query(TenantDomain).filter(
        TenantDomain.id == domain_id,
        TenantDomain.tenant_id == tenant_id
    ).first()
    
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found"
        )
    
    if domain.is_verified:
        return {
            "success": True,
            "message": "Domain is already verified",
            "verified_at": domain.verified_at.isoformat()
        }
    
    from app.services.dns_verification_service import DNSVerificationService
    
    result = DNSVerificationService.verify_domain(
        domain.domain,
        domain.verification_method,
        domain.verification_token
    )
    
    if result["verified"]:
        domain.is_verified = True
        domain.verified_at = datetime.utcnow()
        db.commit()
        
        return {
            "success": True,
            "message": f"Domain {domain.domain} verified successfully!",
            "verified_at": domain.verified_at.isoformat()
        }
    else:
        return {
            "success": False,
            "message": f"Verification failed: {result['error']}",
            "actual_value": result.get("actual_value"),
            "error": result["error"]
        }


@router.post("/{tenant_id}/domains/{domain_id}/ssl/upload")
async def upload_ssl_certificate(
    tenant_id: str,
    domain_id: str,
    cert_data: SSLCertificateUpload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🔒 Upload SSL certificate manually.
    """
    check_admin_access(current_user, tenant_id)
    
    domain = db.query(TenantDomain).filter(
        TenantDomain.id == domain_id,
        TenantDomain.tenant_id == tenant_id
    ).first()
    
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found"
        )
    
    if not domain.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Domain must be verified before uploading SSL certificate"
        )
    
    from app.services.ssl_certificate_service import SSLCertificateService
    
    ssl_service = SSLCertificateService()
    
    # Validate certificate
    validation = ssl_service.validate_certificate(
        cert_data.certificate_pem,
        cert_data.private_key_pem,
        domain.domain
    )
    
    if not validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid certificate: {validation['error']}"
        )
    
    # Store certificate
    try:
        paths = ssl_service.store_certificate(
            tenant_id,
            domain.domain,
            cert_data.certificate_pem,
            cert_data.private_key_pem,
            cert_data.chain_pem
        )
        
        # Update domain record
        domain.ssl_enabled = True
        domain.ssl_certificate = cert_data.certificate_pem
        domain.ssl_private_key = cert_data.private_key_pem  # In production, encrypt this!
        db.commit()
        
        return {
            "success": True,
            "message": "SSL certificate uploaded successfully",
            "certificate_info": {
                "subject": validation["subject"],
                "issuer": validation["issuer"],
                "not_before": validation["not_before"],
                "not_after": validation["not_after"],
                "days_until_expiry": validation["days_until_expiry"]
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store certificate: {str(e)}"
        )


@router.post("/{tenant_id}/domains/{domain_id}/ssl/letsencrypt")
async def request_letsencrypt_certificate(
    tenant_id: str,
    domain_id: str,
    request_data: LetsEncryptRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🔐 Request Let's Encrypt SSL certificate automatically.
    """
    check_admin_access(current_user, tenant_id)
    
    domain = db.query(TenantDomain).filter(
        TenantDomain.id == domain_id,
        TenantDomain.tenant_id == tenant_id
    ).first()
    
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found"
        )
    
    if not domain.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Domain must be verified before requesting SSL certificate"
        )
    
    from app.services.ssl_certificate_service import SSLCertificateService
    
    result = SSLCertificateService.request_letsencrypt_certificate(
        domain.domain,
        request_data.email,
        request_data.staging
    )
    
    if result["success"]:
        domain.ssl_enabled = True
        db.commit()
        
        return {
            "success": True,
            "message": result["message"],
            "certificate_path": result["certificate_path"],
            "private_key_path": result["private_key_path"]
        }
    else:
        return {
            "success": False,
            "error": result["error"],
            "message": "Failed to obtain Let's Encrypt certificate. Make sure domain points to this server and port 80 is accessible."
        }


@router.get("/{tenant_id}/domains/{domain_id}/ssl/info")
async def get_ssl_certificate_info(
    tenant_id: str,
    domain_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ℹ️ Get SSL certificate information.
    """
    check_admin_access(current_user, tenant_id)
    
    domain = db.query(TenantDomain).filter(
        TenantDomain.id == domain_id,
        TenantDomain.tenant_id == tenant_id
    ).first()
    
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found"
        )
    
    if not domain.ssl_enabled:
        return {
            "ssl_enabled": False,
            "message": "SSL certificate not configured for this domain"
        }
    
    from app.services.ssl_certificate_service import SSLCertificateService
    
    if domain.ssl_certificate:
        # Certificate stored in database
        validation = SSLCertificateService.validate_certificate(
            domain.ssl_certificate,
            domain.ssl_private_key,
            domain.domain
        )
        
        return {
            "ssl_enabled": True,
            "source": "manual_upload",
            "certificate_info": validation if validation["valid"] else None,
            "error": validation.get("error")
        }
    else:
        # Let's Encrypt certificate
        cert_path = f"/etc/letsencrypt/live/{domain.domain}/fullchain.pem"
        cert_info = SSLCertificateService.get_certificate_info(cert_path)
        
        if cert_info:
            return {
                "ssl_enabled": True,
                "source": "letsencrypt",
                "certificate_info": cert_info
            }
        else:
            return {
                "ssl_enabled": True,
                "source": "unknown",
                "message": "Certificate exists but info could not be retrieved"
            }


@router.post("/{tenant_id}/domains/{domain_id}/ssl/renew")
async def renew_ssl_certificate(
    tenant_id: str,
    domain_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🔄 Renew Let's Encrypt SSL certificate.
    """
    check_admin_access(current_user, tenant_id)
    
    domain = db.query(TenantDomain).filter(
        TenantDomain.id == domain_id,
        TenantDomain.tenant_id == tenant_id
    ).first()
    
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found"
        )
    
    from app.services.ssl_certificate_service import SSLCertificateService
    
    result = SSLCertificateService.renew_letsencrypt_certificate(domain.domain)
    
    return result
