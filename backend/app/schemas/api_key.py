from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

# Available API scopes
AVAILABLE_SCOPES = [
    "read:datasources",
    "write:datasources",
    "read:queries",
    "write:queries",
    "execute:queries",
    "read:dashboards",
    "write:dashboards",
    "read:users",
    "write:users",
    "read:analytics",
    "execute:analytics",
    "read:alerts",
    "write:alerts",
    "read:exports",
    "execute:exports",
    "admin:*",  # Full admin access
]

class APIKeyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    scopes: List[str] = Field(default_factory=list)
    rate_limit_per_minute: int = Field(default=60, ge=1, le=10000)
    rate_limit_per_hour: int = Field(default=1000, ge=1, le=100000)
    rate_limit_per_day: int = Field(default=10000, ge=1, le=1000000)
    expires_at: Optional[datetime] = None
    
    @validator('scopes')
    def validate_scopes(cls, v):
        """Validate that all scopes are valid"""
        if not v:
            raise ValueError("At least one scope is required")
        
        invalid_scopes = [scope for scope in v if scope not in AVAILABLE_SCOPES]
        if invalid_scopes:
            raise ValueError(f"Invalid scopes: {', '.join(invalid_scopes)}")
        
        return v


class APIKeyCreate(APIKeyBase):
    """Schema for creating a new API key"""
    pass


class APIKeyUpdate(BaseModel):
    """Schema for updating an existing API key"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    scopes: Optional[List[str]] = None
    rate_limit_per_minute: Optional[int] = Field(None, ge=1, le=10000)
    rate_limit_per_hour: Optional[int] = Field(None, ge=1, le=100000)
    rate_limit_per_day: Optional[int] = Field(None, ge=1, le=1000000)
    is_active: Optional[bool] = None
    
    @validator('scopes')
    def validate_scopes(cls, v):
        """Validate that all scopes are valid"""
        if v is not None:
            if not v:
                raise ValueError("At least one scope is required")
            
            invalid_scopes = [scope for scope in v if scope not in AVAILABLE_SCOPES]
            if invalid_scopes:
                raise ValueError(f"Invalid scopes: {', '.join(invalid_scopes)}")
        
        return v


class APIKeyResponse(BaseModel):
    """Schema for API key response (without the actual key)"""
    id: str
    name: str
    description: Optional[str]
    key_prefix: str  # First 8 chars for display
    scopes: List[str]
    rate_limit_per_minute: int
    rate_limit_per_hour: int
    rate_limit_per_day: int
    is_active: bool
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    last_used_ip: Optional[str]
    request_count: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class APIKeyCreatedResponse(APIKeyResponse):
    """Response when API key is first created (includes the actual key)"""
    api_key: str  # Full API key - only shown once!
    
    class Config:
        from_attributes = True


class APIKeyRotateResponse(BaseModel):
    """Response when rotating an API key"""
    id: str
    api_key: str  # New API key
    message: str = "API key rotated successfully. Please update your applications with the new key."


class APIKeyScopeInfo(BaseModel):
    """Information about available scopes"""
    scope: str
    description: str
    category: str


class APIKeyScopesResponse(BaseModel):
    """Response with all available scopes"""
    scopes: List[APIKeyScopeInfo]


class APIKeyUsageStats(BaseModel):
    """Usage statistics for an API key"""
    api_key_id: str
    total_requests: int
    requests_last_24h: int
    requests_last_7d: int
    requests_last_30d: int
    avg_response_time_ms: Optional[float]
    error_rate: Optional[float]
    most_used_endpoints: List[dict]
    
    class Config:
        from_attributes = True
