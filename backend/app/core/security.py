from datetime import datetime, timedelta
from typing import Optional, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(lambda: None)
):
    """Get current user from JWT token"""
    from .database import SessionLocal
    from ..models.user import User
    
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    # Get user from database
    db_session = SessionLocal()
    try:
        user = db_session.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        return user
    finally:
        db_session.close()


async def get_current_user_or_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Get current user from either JWT token or API key
    Supports both authentication methods
    """
    from .database import SessionLocal
    from ..models.user import User
    from ..services.api_key_service import APIKeyService
    
    token = credentials.credentials
    db_session = SessionLocal()
    
    try:
        # Try API key first (starts with "nexbii_")
        if token.startswith("nexbii_"):
            api_key = APIKeyService.verify_api_key(db_session, token)
            if api_key is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired API key",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Get user associated with API key
            user = db_session.query(User).filter(User.id == api_key.user_id).first()
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found for API key",
                )
            
            # Attach API key to user for scope checking
            user.api_key = api_key
            return user
        
        # Otherwise, try JWT token
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        
        user = db_session.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        
        # No API key attached for JWT auth
        user.api_key = None
        return user
        
    finally:
        db_session.close()


def require_scope(required_scope: str):
    """
    Dependency to check if user has required scope (for API key authentication)
    For JWT authentication, this always passes (full access)
    """
    async def scope_checker(user = Depends(get_current_user_or_api_key)):
        # If authenticated via JWT (no API key), grant full access
        if not hasattr(user, 'api_key') or user.api_key is None:
            return user
        
        # Check if API key has required scope
        if not user.api_key.has_scope(required_scope):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"API key does not have required scope: {required_scope}"
            )
        
        return user
    
    return scope_checker


def require_role(allowed_roles: list):
    """
    Dependency to check if user has one of the allowed roles
    Usage: current_user: User = Depends(require_role(["admin"]))
    """
    async def role_checker(user = Depends(get_current_user)):
        from ..models.user import UserRole
        
        # Convert string roles to enum if needed
        if isinstance(user.role, str):
            user_role = user.role.lower()
        else:
            user_role = user.role.value.lower() if hasattr(user.role, 'value') else str(user.role).lower()
        
        # Check if user has one of the allowed roles
        allowed_roles_lower = [role.lower() for role in allowed_roles]
        
        if user_role not in allowed_roles_lower:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient privileges. Required role: {', '.join(allowed_roles)}"
            )
        
        return user
    
    return role_checker
