from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User, UserRole
from ..schemas.api_key import (
    APIKeyCreate,
    APIKeyUpdate,
    APIKeyResponse,
    APIKeyCreatedResponse,
    APIKeyRotateResponse,
    APIKeyScopesResponse,
    APIKeyScopeInfo,
    APIKeyUsageStats,
    AVAILABLE_SCOPES
)
from ..services.api_key_service import APIKeyService

router = APIRouter()


# Scope descriptions for documentation
SCOPE_DESCRIPTIONS = {
    "read:datasources": {"description": "Read data source configurations", "category": "Data Sources"},
    "write:datasources": {"description": "Create, update, and delete data sources", "category": "Data Sources"},
    "read:queries": {"description": "Read saved queries", "category": "Queries"},
    "write:queries": {"description": "Create, update, and delete queries", "category": "Queries"},
    "execute:queries": {"description": "Execute queries and view results", "category": "Queries"},
    "read:dashboards": {"description": "Read dashboards", "category": "Dashboards"},
    "write:dashboards": {"description": "Create, update, and delete dashboards", "category": "Dashboards"},
    "read:users": {"description": "Read user information", "category": "Users"},
    "write:users": {"description": "Create, update, and delete users", "category": "Users"},
    "read:analytics": {"description": "Read analytics data", "category": "Analytics"},
    "execute:analytics": {"description": "Execute analytics operations", "category": "Analytics"},
    "read:alerts": {"description": "Read alert configurations", "category": "Alerts"},
    "write:alerts": {"description": "Create, update, and delete alerts", "category": "Alerts"},
    "read:exports": {"description": "Read export history", "category": "Exports"},
    "execute:exports": {"description": "Execute data exports", "category": "Exports"},
    "admin:*": {"description": "Full administrative access to all resources", "category": "Admin"},
}


@router.get("/scopes", response_model=APIKeyScopesResponse)
async def get_available_scopes():
    """
    Get list of all available API scopes
    """
    scopes = [
        APIKeyScopeInfo(
            scope=scope,
            description=SCOPE_DESCRIPTIONS.get(scope, {}).get("description", ""),
            category=SCOPE_DESCRIPTIONS.get(scope, {}).get("category", "Other")
        )
        for scope in AVAILABLE_SCOPES
    ]
    
    return APIKeyScopesResponse(scopes=scopes)


@router.post("/", response_model=APIKeyCreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    api_key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new API key
    
    **Important:** The full API key is only shown once upon creation.
    Store it securely as it cannot be retrieved later.
    """
    # Create API key
    api_key, plain_key = APIKeyService.create_api_key(
        db=db,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        api_key_data=api_key_data
    )
    
    # Return response with full key
    response = APIKeyCreatedResponse(
        id=api_key.id,
        name=api_key.name,
        description=api_key.description,
        key_prefix=api_key.key_prefix,
        scopes=api_key.scopes,
        rate_limit_per_minute=api_key.rate_limit_per_minute,
        rate_limit_per_hour=api_key.rate_limit_per_hour,
        rate_limit_per_day=api_key.rate_limit_per_day,
        is_active=api_key.is_active,
        expires_at=api_key.expires_at,
        last_used_at=api_key.last_used_at,
        last_used_ip=api_key.last_used_ip,
        request_count=api_key.request_count,
        created_at=api_key.created_at,
        updated_at=api_key.updated_at,
        api_key=plain_key
    )
    
    return response


@router.get("/", response_model=List[APIKeyResponse])
async def list_api_keys(
    include_inactive: bool = False,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all API keys for the current user
    """
    api_keys = APIKeyService.get_api_keys(
        db=db,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        skip=skip,
        limit=limit,
        include_inactive=include_inactive
    )
    
    return api_keys


@router.get("/{api_key_id}", response_model=APIKeyResponse)
async def get_api_key(
    api_key_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific API key
    """
    api_key = APIKeyService.get_api_key_by_id(
        db=db,
        api_key_id=api_key_id,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id
    )
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    return api_key


@router.put("/{api_key_id}", response_model=APIKeyResponse)
async def update_api_key(
    api_key_id: str,
    update_data: APIKeyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an API key
    
    You can update name, description, scopes, rate limits, and active status.
    The actual key value cannot be changed - use rotate endpoint instead.
    """
    api_key = APIKeyService.update_api_key(
        db=db,
        api_key_id=api_key_id,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        update_data=update_data
    )
    
    return api_key


@router.delete("/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    api_key_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete (revoke) an API key
    
    This will immediately revoke the API key and prevent any further use.
    """
    APIKeyService.delete_api_key(
        db=db,
        api_key_id=api_key_id,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id
    )
    
    return None


@router.post("/{api_key_id}/rotate", response_model=APIKeyRotateResponse)
async def rotate_api_key(
    api_key_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Rotate an API key
    
    Generates a new key value while keeping the same configuration.
    The old key will be immediately invalidated.
    
    **Important:** The new API key is only shown once. Store it securely.
    """
    api_key, new_key = APIKeyService.rotate_api_key(
        db=db,
        api_key_id=api_key_id,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id
    )
    
    return APIKeyRotateResponse(
        id=api_key.id,
        api_key=new_key
    )


@router.get("/{api_key_id}/usage", response_model=APIKeyUsageStats)
async def get_api_key_usage(
    api_key_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get usage statistics for an API key
    
    Returns request counts, average response time, error rate, and most used endpoints.
    """
    stats = APIKeyService.get_api_key_usage_stats(
        db=db,
        api_key_id=api_key_id,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id
    )
    
    return stats


@router.post("/test", status_code=status.HTTP_200_OK)
async def test_api_key_authentication(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Test API key authentication
    
    Use this endpoint to verify your API key is working correctly.
    Include your API key in the Authorization header: `Bearer nexbii_your_key_here`
    """
    # Check if authenticated via API key or JWT
    auth_method = "JWT Token"
    api_key_info = None
    
    if hasattr(current_user, 'api_key') and current_user.api_key:
        auth_method = "API Key"
        api_key_info = {
            "key_prefix": current_user.api_key.key_prefix,
            "scopes": current_user.api_key.scopes,
            "rate_limits": {
                "per_minute": current_user.api_key.rate_limit_per_minute,
                "per_hour": current_user.api_key.rate_limit_per_hour,
                "per_day": current_user.api_key.rate_limit_per_day
            }
        }
    
    return {
        "success": True,
        "message": "Authentication successful",
        "auth_method": auth_method,
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "role": current_user.role
        },
        "api_key": api_key_info
    }
