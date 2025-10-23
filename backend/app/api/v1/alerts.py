from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ...core.database import get_db
from ...core.security import get_current_user
from ...models.user import User, UserRole
from ...models.alert import AlertStatus
from ...schemas.collaboration import (
    AlertCreate,
    AlertUpdate,
    AlertResponse,
    AlertHistoryResponse
)
from ...services.alert_service import AlertService

router = APIRouter()

@router.post("/", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert: AlertCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new alert for query monitoring
    """
    try:
        result = AlertService.create_alert(
            db=db,
            user_id=current_user.id,
            **alert.dict()
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create alert: {str(e)}"
        )

@router.get("/", response_model=List[AlertResponse])
async def get_alerts(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all alerts for current user
    """
    alert_status = None
    if status:
        try:
            alert_status = AlertStatus[status.upper()]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}"
            )
    
    alerts = AlertService.get_user_alerts(
        db=db,
        user_id=current_user.id,
        status=alert_status
    )
    return alerts

@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific alert
    """
    alert = AlertService.get_alert(db, alert_id, current_user.id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    return alert

@router.put("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: str,
    update_data: AlertUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an alert
    """
    result = AlertService.update_alert(
        db=db,
        alert_id=alert_id,
        user_id=current_user.id,
        **update_data.dict(exclude_unset=True)
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    return result

@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an alert
    """
    success = AlertService.delete_alert(db, alert_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    return None

@router.post("/{alert_id}/evaluate", status_code=status.HTTP_200_OK)
async def evaluate_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually evaluate an alert
    """
    alert = AlertService.get_alert(db, alert_id, current_user.id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    triggered = AlertService.evaluate_alert(db, alert)
    return {
        "alert_id": alert_id,
        "evaluated": True,
        "triggered": triggered
    }

@router.post("/{alert_id}/snooze", response_model=AlertResponse)
async def snooze_alert(
    alert_id: str,
    hours: int = Query(24, ge=1, le=168),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Snooze an alert for specified hours
    """
    result = AlertService.snooze_alert(
        db=db,
        alert_id=alert_id,
        user_id=current_user.id,
        hours=hours
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    return result

@router.get("/{alert_id}/history", response_model=List[AlertHistoryResponse])
async def get_alert_history(
    alert_id: str,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get alert history
    """
    # Verify alert belongs to user
    alert = AlertService.get_alert(db, alert_id, current_user.id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    history = AlertService.get_alert_history(db, alert_id, limit)
    return history

@router.post("/check-all", status_code=status.HTTP_200_OK)
async def check_all_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually check all due alerts (Admin only)
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can trigger alert checks"
        )
    
    results = AlertService.check_all_alerts(db)
    return {
        "message": "Alert check completed",
        **results
    }
