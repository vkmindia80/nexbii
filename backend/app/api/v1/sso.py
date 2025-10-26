"""
SSO API Endpoints
Handles OAuth, SAML, and LDAP authentication
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user, create_access_token
from app.models.user import User
from app.models.security import OAuthProvider, SAMLConfig, LDAPConfig
from app.schemas.security import (
    OAuthProviderCreate,
    OAuthProviderUpdate,
    OAuthProviderResponse,
    SAMLConfigCreate,
    SAMLConfigUpdate,
    SAMLConfigResponse,
    LDAPConfigCreate,
    LDAPConfigUpdate,
    LDAPConfigResponse
)
from app.services.oauth_service import OAuthService
from app.services.saml_service import SAMLService
from app.services.ldap_service import LDAPService
from app.services.audit_service import AuditService
import uuid

router = APIRouter()


# ===== OAuth Providers =====

@router.get("/providers", response_model=List[OAuthProviderResponse])
def list_oauth_providers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all OAuth providers"""
    providers = db.query(OAuthProvider).filter(
        OAuthProvider.tenant_id == current_user.tenant_id
    ).all()
    
    return providers


@router.post("/providers", response_model=OAuthProviderResponse, status_code=status.HTTP_201_CREATED)
def create_oauth_provider(
    provider_data: OAuthProviderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create OAuth provider configuration"""
    oauth_service = OAuthService(db)
    provider = oauth_service.create_provider(
        tenant_id=current_user.tenant_id,
        provider_data=provider_data.dict()
    )
    
    return provider


@router.get("/providers/{provider_id}", response_model=OAuthProviderResponse)
def get_oauth_provider(
    provider_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get OAuth provider details"""
    provider = db.query(OAuthProvider).filter(
        OAuthProvider.id == provider_id,
        OAuthProvider.tenant_id == current_user.tenant_id
    ).first()
    
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OAuth provider not found"
        )
    
    return provider


@router.put("/providers/{provider_id}", response_model=OAuthProviderResponse)
def update_oauth_provider(
    provider_id: str,
    provider_data: OAuthProviderUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update OAuth provider configuration"""
    provider = db.query(OAuthProvider).filter(
        OAuthProvider.id == provider_id,
        OAuthProvider.tenant_id == current_user.tenant_id
    ).first()
    
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OAuth provider not found"
        )
    
    for field, value in provider_data.dict(exclude_unset=True).items():
        setattr(provider, field, value)
    
    db.commit()
    db.refresh(provider)
    
    return provider


@router.delete("/providers/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_oauth_provider(
    provider_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete OAuth provider"""
    provider = db.query(OAuthProvider).filter(
        OAuthProvider.id == provider_id,
        OAuthProvider.tenant_id == current_user.tenant_id
    ).first()
    
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OAuth provider not found"
        )
    
    db.delete(provider)
    db.commit()


@router.get("/oauth/{provider_name}/authorize")
async def oauth_authorize(
    provider_name: str,
    tenant_id: str,
    db: Session = Depends(get_db)
):
    """Start OAuth authorization flow"""
    oauth_service = OAuthService(db)
    provider = oauth_service.get_provider_by_name(provider_name, tenant_id)
    
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OAuth provider '{provider_name}' not found or not enabled"
        )
    
    # Generate state for CSRF protection
    import secrets
    state = secrets.token_urlsafe(32)
    
    # Store state in session (in production, use Redis or database)
    # For demo, we'll just pass it through
    
    redirect_uri = f"http://localhost:8001/api/sso/oauth/{provider_name}/callback"
    
    auth_url = oauth_service.get_authorization_url(
        provider=provider,
        redirect_uri=redirect_uri,
        state=state
    )
    
    return RedirectResponse(url=auth_url)


@router.get("/oauth/{provider_name}/callback")
async def oauth_callback(
    provider_name: str,
    code: str,
    state: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle OAuth callback"""
    # Get tenant_id from state or session
    # For demo, using default demo tenant
    tenant_id = "demo_tenant_id"
    
    oauth_service = OAuthService(db)
    provider = oauth_service.get_provider_by_name(provider_name, tenant_id)
    
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OAuth provider not found"
        )
    
    try:
        # Exchange code for token
        redirect_uri = f"http://localhost:8001/api/sso/oauth/{provider_name}/callback"
        token_data = await oauth_service.exchange_code_for_token(
            provider=provider,
            code=code,
            redirect_uri=redirect_uri
        )
        
        # Get user info
        access_token = token_data.get("access_token")
        user_info = await oauth_service.get_user_info(provider, access_token)
        
        # Map user data
        user_data = oauth_service.map_user_data(provider, user_info)
        
        # Find or create user
        user = oauth_service.find_or_create_user(provider, user_data)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User sign-up not allowed"
            )
        
        # Create JWT token
        access_token = create_access_token(data={"sub": user.email})
        
        # Log successful login
        audit_service = AuditService(db)
        audit_service.log_login_attempt(
            email=user.email,
            success=True,
            tenant_id=user.tenant_id,
            user_id=user.id
        )
        
        # Redirect to frontend with token
        return RedirectResponse(
            url=f"http://localhost:3000/auth/callback?token={access_token}"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authentication failed: {str(e)}"
        )


# ===== SAML Configuration =====

@router.post("/saml/config", response_model=SAMLConfigResponse, status_code=status.HTTP_201_CREATED)
def create_saml_config(
    config_data: SAMLConfigCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create SAML configuration"""
    saml_service = SAMLService(db)
    config = saml_service.create_config(
        tenant_id=current_user.tenant_id,
        config_data=config_data.dict()
    )
    
    return config


@router.get("/saml/config", response_model=SAMLConfigResponse)
def get_saml_config(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get SAML configuration"""
    saml_service = SAMLService(db)
    config = saml_service.get_config_by_tenant(current_user.tenant_id)
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SAML configuration not found"
        )
    
    return config


@router.get("/saml/metadata")
def get_saml_metadata(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get SAML Service Provider metadata"""
    saml_service = SAMLService(db)
    config = saml_service.get_config_by_tenant(current_user.tenant_id)
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SAML configuration not found"
        )
    
    metadata = saml_service.get_sp_metadata(config)
    
    return {"metadata": metadata}


@router.post("/saml/acs")
async def saml_assertion_consumer(
    saml_response: str,
    db: Session = Depends(get_db)
):
    """SAML Assertion Consumer Service (ACS)"""
    # This endpoint receives SAML assertions from IdP
    # For demo, returning mock response
    
    tenant_id = "demo_tenant_id"
    
    saml_service = SAMLService(db)
    config = saml_service.get_config_by_tenant(tenant_id)
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SAML configuration not found"
        )
    
    try:
        # Parse SAML response
        saml_data = saml_service.parse_saml_response(saml_response, config)
        
        # Map user data
        user_data = saml_service.map_user_data(config, saml_data)
        
        # Find or create user
        user = saml_service.find_or_create_user(config, user_data)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User sign-up not allowed"
            )
        
        # Create JWT token
        access_token = create_access_token(data={"sub": user.email})
        
        return {"access_token": access_token, "token_type": "bearer"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SAML authentication failed: {str(e)}"
        )


# ===== LDAP Configuration =====

@router.post("/ldap/config", response_model=LDAPConfigResponse, status_code=status.HTTP_201_CREATED)
def create_ldap_config(
    config_data: LDAPConfigCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create LDAP configuration"""
    ldap_service = LDAPService(db)
    config = ldap_service.create_config(
        tenant_id=current_user.tenant_id,
        config_data=config_data.dict()
    )
    
    return config


@router.get("/ldap/config", response_model=LDAPConfigResponse)
def get_ldap_config(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get LDAP configuration"""
    ldap_service = LDAPService(db)
    config = ldap_service.get_config_by_tenant(current_user.tenant_id)
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LDAP configuration not found"
        )
    
    return config


@router.post("/ldap/test")
def test_ldap_connection(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test LDAP connection"""
    ldap_service = LDAPService(db)
    config = ldap_service.get_config_by_tenant(current_user.tenant_id)
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LDAP configuration not found"
        )
    
    result = ldap_service.test_connection(config)
    
    return result


@router.post("/ldap/sync")
def sync_ldap_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync users from LDAP"""
    ldap_service = LDAPService(db)
    config = ldap_service.get_config_by_tenant(current_user.tenant_id)
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LDAP configuration not found"
        )
    
    result = ldap_service.sync_users(config)
    
    return result
