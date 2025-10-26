"""
OAuth 2.0 Service for SSO
Supports Google, Microsoft, GitHub and custom providers
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from app.models.security import OAuthProvider
from app.models.user import User, UserRole
import uuid
import httpx


class OAuthService:
    """Service for OAuth 2.0 authentication"""
    
    # Predefined providers
    PROVIDERS = {
        "google": {
            "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
            "token_url": "https://oauth2.googleapis.com/token",
            "user_info_url": "https://www.googleapis.com/oauth2/v2/userinfo",
            "scopes": ["openid", "email", "profile"]
        },
        "microsoft": {
            "authorize_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
            "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
            "user_info_url": "https://graph.microsoft.com/v1.0/me",
            "scopes": ["openid", "email", "profile"]
        },
        "github": {
            "authorize_url": "https://github.com/login/oauth/authorize",
            "token_url": "https://github.com/login/oauth/access_token",
            "user_info_url": "https://api.github.com/user",
            "scopes": ["user:email"]
        }
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_provider(self, provider_id: str) -> Optional[OAuthProvider]:
        """Get OAuth provider by ID"""
        return self.db.query(OAuthProvider).filter(
            OAuthProvider.id == provider_id,
            OAuthProvider.is_enabled == True
        ).first()
    
    def get_provider_by_name(self, provider_name: str, tenant_id: str) -> Optional[OAuthProvider]:
        """Get OAuth provider by name and tenant"""
        return self.db.query(OAuthProvider).filter(
            OAuthProvider.provider_name == provider_name,
            OAuthProvider.tenant_id == tenant_id,
            OAuthProvider.is_enabled == True
        ).first()
    
    def create_provider(self, tenant_id: str, provider_data: Dict[str, Any]) -> OAuthProvider:
        """Create OAuth provider configuration"""
        provider_name = provider_data.get("provider_name")
        
        # Use predefined config if available
        if provider_name in self.PROVIDERS:
            predefined = self.PROVIDERS[provider_name]
            provider_data["authorize_url"] = provider_data.get(
                "authorize_url", predefined["authorize_url"]
            )
            provider_data["token_url"] = provider_data.get(
                "token_url", predefined["token_url"]
            )
            provider_data["user_info_url"] = provider_data.get(
                "user_info_url", predefined["user_info_url"]
            )
            provider_data["scopes"] = provider_data.get(
                "scopes", predefined["scopes"]
            )
        
        provider = OAuthProvider(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            **provider_data
        )
        
        self.db.add(provider)
        self.db.commit()
        self.db.refresh(provider)
        
        return provider
    
    def get_authorization_url(
        self, provider: OAuthProvider, redirect_uri: str, state: str
    ) -> str:
        """Get OAuth authorization URL"""
        params = {
            "client_id": provider.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(provider.scopes),
            "state": state
        }
        
        # Build URL with query parameters
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{provider.authorize_url}?{query_string}"
    
    async def exchange_code_for_token(
        self, provider: OAuthProvider, code: str, redirect_uri: str
    ) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        data = {
            "client_id": provider.client_id,
            "client_secret": provider.client_secret,
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                provider.token_url,
                data=data,
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            return response.json()
    
    async def get_user_info(
        self, provider: OAuthProvider, access_token: str
    ) -> Dict[str, Any]:
        """Get user information from OAuth provider"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                provider.user_info_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json"
                }
            )
            response.raise_for_status()
            return response.json()
    
    def map_user_data(
        self, provider: OAuthProvider, oauth_user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Map OAuth user data to our user model"""
        mapping = provider.user_field_mapping or {}
        
        # Default mappings by provider
        if provider.provider_name == "google":
            return {
                "email": oauth_user_data.get("email"),
                "full_name": oauth_user_data.get("name"),
                "avatar_url": oauth_user_data.get("picture")
            }
        elif provider.provider_name == "microsoft":
            return {
                "email": oauth_user_data.get("mail") or oauth_user_data.get("userPrincipalName"),
                "full_name": oauth_user_data.get("displayName"),
                "avatar_url": None
            }
        elif provider.provider_name == "github":
            return {
                "email": oauth_user_data.get("email"),
                "full_name": oauth_user_data.get("name"),
                "avatar_url": oauth_user_data.get("avatar_url")
            }
        
        # Custom mapping
        return {
            "email": oauth_user_data.get(mapping.get("email", "email")),
            "full_name": oauth_user_data.get(mapping.get("name", "name")),
            "avatar_url": oauth_user_data.get(mapping.get("avatar", "avatar_url"))
        }
    
    def find_or_create_user(
        self, provider: OAuthProvider, user_data: Dict[str, Any]
    ) -> Optional[User]:
        """Find existing user or create new one from OAuth data"""
        email = user_data.get("email")
        
        if not email:
            return None
        
        # Find existing user
        user = self.db.query(User).filter(
            User.email == email,
            User.tenant_id == provider.tenant_id
        ).first()
        
        if user:
            return user
        
        # Create new user if allowed
        if not provider.allow_sign_up:
            return None
        
        from app.core.security import get_password_hash
        import secrets
        
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            full_name=user_data.get("full_name", email),
            hashed_password=get_password_hash(secrets.token_urlsafe(32)),  # Random password
            role=UserRole.VIEWER,  # Default role
            is_active=True,
            tenant_id=provider.tenant_id
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
