from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.dashboard import Dashboard
from app.models.share import SharedDashboard

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()


class CreateShareRequest(BaseModel):
    dashboard_id: str
    password: Optional[str] = None
    expires_in_days: Optional[int] = None
    allow_interactions: bool = True


class ShareResponse(BaseModel):
    share_token: str
    share_url: str
    expires_at: Optional[datetime] = None
    password_protected: bool
    allow_interactions: bool


class AccessShareRequest(BaseModel):
    password: Optional[str] = None


@router.post("/create", response_model=ShareResponse)
async def create_share_link(
    request: CreateShareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a shareable link for a dashboard"""
    # Verify dashboard exists
    dashboard = db.query(Dashboard).filter(Dashboard.id == request.dashboard_id).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    # Check if user has permission (dashboard owner or admin)
    if dashboard.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to share this dashboard")
    
    # Calculate expiration
    expires_at = None
    if request.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=request.expires_in_days)
    
    # Hash password if provided
    hashed_password = None
    if request.password:
        hashed_password = pwd_context.hash(request.password)
    
    # Create share record
    share = SharedDashboard(
        dashboard_id=request.dashboard_id,
        share_token=SharedDashboard.generate_token(),
        password=hashed_password,
        expires_at=expires_at,
        allow_interactions=request.allow_interactions,
        created_by=current_user.id,
        is_active=True
    )
    
    db.add(share)
    db.commit()
    db.refresh(share)
    
    # Generate share URL (frontend will handle this route)
    share_url = f"/public/dashboard/{share.share_token}"
    
    return ShareResponse(
        share_token=share.share_token,
        share_url=share_url,
        expires_at=expires_at,
        password_protected=bool(request.password),
        allow_interactions=request.allow_interactions
    )


@router.get("/dashboard/{share_token}")
async def get_shared_dashboard(
    share_token: str,
    db: Session = Depends(get_db)
):
    """Get shared dashboard (public access, no auth required)"""
    share = db.query(SharedDashboard).filter(
        SharedDashboard.share_token == share_token,
        SharedDashboard.is_active == True
    ).first()
    
    if not share:
        raise HTTPException(status_code=404, detail="Shared dashboard not found or expired")
    
    # Check expiration
    if share.expires_at and share.expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="This shared link has expired")
    
    # Return basic info (password check will be separate)
    return {
        "dashboard_id": share.dashboard_id,
        "requires_password": bool(share.password),
        "allow_interactions": share.allow_interactions,
        "expires_at": share.expires_at
    }


@router.post("/dashboard/{share_token}/access")
async def access_shared_dashboard(
    share_token: str,
    request: AccessShareRequest,
    db: Session = Depends(get_db)
):
    """Access shared dashboard with optional password"""
    share = db.query(SharedDashboard).filter(
        SharedDashboard.share_token == share_token,
        SharedDashboard.is_active == True
    ).first()
    
    if not share:
        raise HTTPException(status_code=404, detail="Shared dashboard not found")
    
    # Check expiration
    if share.expires_at and share.expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="This shared link has expired")
    
    # Verify password if required
    if share.password:
        if not request.password:
            raise HTTPException(status_code=401, detail="Password required")
        if not pwd_context.verify(request.password, share.password):
            raise HTTPException(status_code=401, detail="Invalid password")
    
    # Get full dashboard
    dashboard = db.query(Dashboard).filter(Dashboard.id == share.dashboard_id).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    return {
        "dashboard": {
            "id": dashboard.id,
            "name": dashboard.name,
            "description": dashboard.description,
            "layout": dashboard.layout,
            "widgets": dashboard.widgets,
            "filters": dashboard.filters
        },
        "allow_interactions": share.allow_interactions
    }


@router.get("/my-shares")
async def get_my_shares(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all shares created by current user"""
    shares = db.query(SharedDashboard).filter(
        SharedDashboard.created_by == current_user.id,
        SharedDashboard.is_active == True
    ).all()
    
    result = []
    for share in shares:
        dashboard = db.query(Dashboard).filter(Dashboard.id == share.dashboard_id).first()
        result.append({
            "id": share.id,
            "dashboard_id": share.dashboard_id,
            "dashboard_name": dashboard.name if dashboard else "Unknown",
            "share_token": share.share_token,
            "share_url": f"/public/dashboard/{share.share_token}",
            "password_protected": bool(share.password),
            "expires_at": share.expires_at,
            "allow_interactions": share.allow_interactions,
            "created_at": share.created_at
        })
    
    return result


@router.delete("/share/{share_id}")
async def delete_share(
    share_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deactivate a share link"""
    share = db.query(SharedDashboard).filter(SharedDashboard.id == share_id).first()
    if not share:
        raise HTTPException(status_code=404, detail="Share not found")
    
    # Check permission
    if share.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    share.is_active = False
    db.commit()
    
    return {"message": "Share link deactivated successfully"}
