from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from ...core.security import get_current_user
from ...models.user import User
from ...schemas.collaboration import (
    EmailSubscriptionCreate,
    EmailSubscriptionUpdate,
    EmailSubscriptionResponse
)
from ...services.subscription_service import SubscriptionService

router = APIRouter()

@router.post("/", response_model=EmailSubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription: EmailSubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new email subscription for a dashboard
    """
    try:
        result = SubscriptionService.create_subscription(
            db=db,
            user_id=current_user.id,
            dashboard_id=subscription.dashboard_id,
            frequency=subscription.frequency
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create subscription: {str(e)}"
        )

@router.get("/", response_model=List[EmailSubscriptionResponse])
async def get_subscriptions(
    dashboard_id: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all subscriptions for current user
    """
    subscriptions = SubscriptionService.get_user_subscriptions(
        db=db,
        user_id=current_user.id,
        dashboard_id=dashboard_id
    )
    return subscriptions

@router.put("/{subscription_id}", response_model=EmailSubscriptionResponse)
async def update_subscription(
    subscription_id: str,
    update_data: EmailSubscriptionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a subscription
    """
    result = SubscriptionService.update_subscription(
        db=db,
        subscription_id=subscription_id,
        user_id=current_user.id,
        **update_data.dict(exclude_unset=True)
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    return result

@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscription(
    subscription_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a subscription
    """
    success = SubscriptionService.delete_subscription(
        db=db,
        subscription_id=subscription_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    return None

@router.post("/send-due", status_code=status.HTTP_200_OK)
async def send_due_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually trigger sending of due subscription emails (Admin only)
    """
    from ...models.user import UserRole
    
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can trigger subscription emails"
        )
    
    sent_count = SubscriptionService.send_subscription_emails(db)
    return {"message": f"Sent {sent_count} subscription emails"}