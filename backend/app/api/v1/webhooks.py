from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ...core.database import get_db
from ...core.security import get_current_user
from ...models.user import User
from ...schemas.webhook import (
    WebhookCreate,
    WebhookUpdate,
    WebhookResponse,
    WebhookDeliveryResponse,
    WebhookTestRequest,
    WebhookTestResponse,
    WebhookEventsResponse,
    WebhookEventInfo,
    WebhookStatsResponse,
    AVAILABLE_EVENTS
)
from ...services.webhook_service import WebhookService

router = APIRouter()

# Event descriptions for documentation
EVENT_DESCRIPTIONS = {
    "datasource.created": {"description": "Data source was created", "category": "Data Sources"},
    "datasource.updated": {"description": "Data source was updated", "category": "Data Sources"},
    "datasource.deleted": {"description": "Data source was deleted", "category": "Data Sources"},
    "query.created": {"description": "Query was created", "category": "Queries"},
    "query.updated": {"description": "Query was updated", "category": "Queries"},
    "query.deleted": {"description": "Query was deleted", "category": "Queries"},
    "query.executed": {"description": "Query was executed", "category": "Queries"},
    "dashboard.created": {"description": "Dashboard was created", "category": "Dashboards"},
    "dashboard.updated": {"description": "Dashboard was updated", "category": "Dashboards"},
    "dashboard.deleted": {"description": "Dashboard was deleted", "category": "Dashboards"},
    "dashboard.viewed": {"description": "Dashboard was viewed", "category": "Dashboards"},
    "alert.triggered": {"description": "Alert was triggered", "category": "Alerts"},
    "alert.resolved": {"description": "Alert was resolved", "category": "Alerts"},
    "export.completed": {"description": "Export operation completed", "category": "Exports"},
    "user.created": {"description": "User account was created", "category": "Users"},
    "user.updated": {"description": "User account was updated", "category": "Users"},
    "user.deleted": {"description": "User account was deleted", "category": "Users"},
}


@router.get("/events", response_model=WebhookEventsResponse)
async def get_available_events():
    """
    Get list of all available webhook events
    """
    events = [
        WebhookEventInfo(
            event=event,
            description=EVENT_DESCRIPTIONS.get(event, {}).get("description", ""),
            category=EVENT_DESCRIPTIONS.get(event, {}).get("category", "Other")
        )
        for event in AVAILABLE_EVENTS
    ]
    
    return WebhookEventsResponse(events=events)


@router.post("/", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    webhook_data: WebhookCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new webhook
    
    Webhooks allow you to receive real-time notifications when events occur in your account.
    Each webhook delivery includes an HMAC-SHA256 signature for verification.
    """
    webhook = WebhookService.create_webhook(
        db=db,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        webhook_data=webhook_data
    )
    
    return webhook


@router.get("/", response_model=List[WebhookResponse])
async def list_webhooks(
    include_inactive: bool = False,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all webhooks for the current tenant
    """
    webhooks = WebhookService.get_webhooks(
        db=db,
        tenant_id=current_user.tenant_id,
        skip=skip,
        limit=limit,
        include_inactive=include_inactive
    )
    
    return webhooks


@router.get("/{webhook_id}", response_model=WebhookResponse)
async def get_webhook(
    webhook_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific webhook
    """
    webhook = WebhookService.get_webhook_by_id(
        db=db,
        webhook_id=webhook_id,
        tenant_id=current_user.tenant_id
    )
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    return webhook


@router.put("/{webhook_id}", response_model=WebhookResponse)
async def update_webhook(
    webhook_id: str,
    update_data: WebhookUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a webhook
    
    You can update the name, URL, events, and other settings.
    The secret cannot be changed directly for security reasons.
    """
    webhook = WebhookService.update_webhook(
        db=db,
        webhook_id=webhook_id,
        tenant_id=current_user.tenant_id,
        update_data=update_data
    )
    
    return webhook


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    webhook_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a webhook
    
    This will permanently delete the webhook and stop all future deliveries.
    """
    WebhookService.delete_webhook(
        db=db,
        webhook_id=webhook_id,
        tenant_id=current_user.tenant_id
    )
    
    return None


@router.post("/{webhook_id}/test", response_model=WebhookTestResponse)
async def test_webhook(
    webhook_id: str,
    test_request: WebhookTestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Test a webhook by sending a test payload
    
    This will send a real HTTP request to your webhook URL with a test payload.
    Use this to verify your webhook endpoint is working correctly.
    """
    result = WebhookService.test_webhook(
        db=db,
        webhook_id=webhook_id,
        tenant_id=current_user.tenant_id,
        event_type=test_request.event_type,
        test_data=test_request.test_data
    )
    
    return WebhookTestResponse(**result)


@router.get("/{webhook_id}/deliveries", response_model=List[WebhookDeliveryResponse])
async def get_webhook_deliveries(
    webhook_id: str,
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get delivery logs for a webhook
    
    Shows the history of webhook deliveries including status, response codes, and retry information.
    """
    deliveries = WebhookService.get_webhook_deliveries(
        db=db,
        webhook_id=webhook_id,
        tenant_id=current_user.tenant_id,
        skip=skip,
        limit=limit,
        status_filter=status_filter
    )
    
    return deliveries


@router.get("/{webhook_id}/stats", response_model=WebhookStatsResponse)
async def get_webhook_stats(
    webhook_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get statistics for a webhook
    
    Returns delivery counts, success rate, average response time, and recent activity.
    """
    stats = WebhookService.get_webhook_stats(
        db=db,
        webhook_id=webhook_id,
        tenant_id=current_user.tenant_id
    )
    
    return stats
