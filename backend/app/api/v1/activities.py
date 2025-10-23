from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ...core.database import get_db
from ...core.security import get_current_user
from ...models.user import User, UserRole
from ...models.activity import ActivityType
from ...schemas.collaboration import ActivityResponse
from ...services.activity_service import ActivityService

router = APIRouter()

@router.get("/me", response_model=List[ActivityResponse])
async def get_my_activities(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get activities for the current user
    """
    activities = ActivityService.get_user_activities(
        db=db,
        user_id=current_user.id,
        limit=limit,
        offset=offset
    )
    return activities

@router.get("/all", response_model=List[ActivityResponse])
async def get_all_activities(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    days: Optional[int] = Query(None, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all activities (Admin/Editor only)
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.EDITOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and editors can view all activities"
        )
    
    activities = ActivityService.get_all_activities(
        db=db,
        limit=limit,
        offset=offset,
        days=days
    )
    return activities

@router.get("/entity/{entity_type}/{entity_id}", response_model=List[ActivityResponse])
async def get_entity_activities(
    entity_type: str,
    entity_id: str,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get activities for a specific entity (dashboard, query, etc.)
    """
    activities = ActivityService.get_entity_activities(
        db=db,
        entity_type=entity_type,
        entity_id=entity_id,
        limit=limit
    )
    return activities

@router.delete("/cleanup", status_code=status.HTTP_200_OK)
async def cleanup_old_activities(
    days: int = Query(90, ge=30, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete activities older than specified days (Admin only)
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can cleanup activities"
        )
    
    deleted_count = ActivityService.delete_old_activities(db, days)
    return {
        "message": f"Deleted {deleted_count} activities older than {days} days"
    }