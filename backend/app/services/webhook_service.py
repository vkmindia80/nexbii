import secrets
import hmac
import hashlib
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from ..models.webhook import Webhook, WebhookDelivery
from ..schemas.webhook import WebhookCreate, WebhookUpdate, WebhookStatsResponse, WebhookDeliveryResponse
from fastapi import HTTPException, status
import threading
import queue

class WebhookService:
    """Service for managing webhooks"""
    
    # Delivery queue for async processing
    delivery_queue = queue.Queue()
    delivery_thread = None
    
    @staticmethod
    def generate_secret() -> str:
        """Generate a secure webhook secret"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def create_webhook(
        db: Session,
        user_id: str,
        tenant_id: str,
        webhook_data: WebhookCreate
    ) -> Webhook:
        """Create a new webhook"""
        # Generate secret if not provided
        secret = webhook_data.secret or WebhookService.generate_secret()
        
        webhook = Webhook(
            user_id=user_id,
            tenant_id=tenant_id,
            name=webhook_data.name,
            description=webhook_data.description,
            url=webhook_data.url,
            secret=secret,
            events=webhook_data.events,
            max_retries=webhook_data.max_retries,
            retry_backoff_seconds=webhook_data.retry_backoff_seconds,
            is_active=True
        )
        
        db.add(webhook)
        db.commit()
        db.refresh(webhook)
        
        return webhook
    
    @staticmethod
    def get_webhooks(
        db: Session,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        include_inactive: bool = False
    ) -> List[Webhook]:
        """Get all webhooks for a tenant"""
        query = db.query(Webhook).filter(Webhook.tenant_id == tenant_id)
        
        if not include_inactive:
            query = query.filter(Webhook.is_active == True)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_webhook_by_id(
        db: Session,
        webhook_id: str,
        tenant_id: str
    ) -> Optional[Webhook]:
        """Get a specific webhook by ID"""
        return db.query(Webhook).filter(
            Webhook.id == webhook_id,
            Webhook.tenant_id == tenant_id
        ).first()
    
    @staticmethod
    def update_webhook(
        db: Session,
        webhook_id: str,
        tenant_id: str,
        update_data: WebhookUpdate
    ) -> Webhook:
        """Update a webhook"""
        webhook = WebhookService.get_webhook_by_id(db, webhook_id, tenant_id)
        if not webhook:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Webhook not found"
            )
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(webhook, field, value)
        
        db.commit()
        db.refresh(webhook)
        return webhook
    
    @staticmethod
    def delete_webhook(
        db: Session,
        webhook_id: str,
        tenant_id: str
    ) -> bool:
        """Delete a webhook"""
        webhook = WebhookService.get_webhook_by_id(db, webhook_id, tenant_id)
        if not webhook:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Webhook not found"
            )
        
        # Hard delete
        db.delete(webhook)
        db.commit()
        return True
    
    @staticmethod
    def generate_signature(payload: str, secret: str) -> str:
        """Generate HMAC-SHA256 signature for webhook payload"""
        signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"
    
    @staticmethod
    def trigger_event(
        db: Session,
        event_type: str,
        event_data: dict,
        tenant_id: str
    ):
        """
        Trigger webhooks for a specific event
        This queues webhook deliveries for async processing
        """
        # Find all active webhooks subscribed to this event
        webhooks = db.query(Webhook).filter(
            Webhook.tenant_id == tenant_id,
            Webhook.is_active == True
        ).all()
        
        for webhook in webhooks:
            if event_type in webhook.events:
                # Create delivery record
                delivery = WebhookDelivery(
                    webhook_id=webhook.id,
                    event_type=event_type,
                    event_data=event_data,
                    status="pending",
                    attempt_count=0,
                    max_attempts=webhook.max_retries + 1  # Initial attempt + retries
                )
                
                db.add(delivery)
                
                # Update webhook stats
                webhook.total_deliveries += 1
                webhook.last_triggered_at = datetime.utcnow()
        
        db.commit()
    
    @staticmethod
    def deliver_webhook(
        db: Session,
        delivery_id: str,
        webhook_id: str
    ) -> bool:
        """
        Deliver a webhook (synchronous)
        Returns True if successful, False otherwise
        """
        delivery = db.query(WebhookDelivery).filter(WebhookDelivery.id == delivery_id).first()
        webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
        
        if not delivery or not webhook:
            return False
        
        # Increment attempt count
        delivery.attempt_count += 1
        delivery.status = "retrying" if delivery.attempt_count > 1 else "pending"
        
        # Prepare payload
        payload_data = {
            "event": delivery.event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "webhook_id": webhook.id,
            "data": delivery.event_data
        }
        
        payload_json = json.dumps(payload_data)
        signature = WebhookService.generate_signature(payload_json, webhook.secret)
        
        # Set headers
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
            "X-Webhook-Event": delivery.event_type,
            "X-Webhook-Delivery": delivery.id,
            "User-Agent": "NexBII-Webhooks/1.0"
        }
        
        # Attempt delivery
        try:
            start_time = time.time()
            response = requests.post(
                webhook.url,
                data=payload_json,
                headers=headers,
                timeout=30
            )
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Update delivery record
            delivery.response_status_code = response.status_code
            delivery.response_body = response.text[:1000]  # Store first 1000 chars
            delivery.response_time_ms = response_time_ms
            
            # Check if successful (2xx status code)
            if 200 <= response.status_code < 300:
                delivery.status = "success"
                delivery.delivered_at = datetime.utcnow()
                
                # Update webhook stats
                webhook.successful_deliveries += 1
                webhook.last_success_at = datetime.utcnow()
                
                db.commit()
                return True
            else:
                delivery.error_message = f"HTTP {response.status_code}: {response.text[:500]}"
                
                # Schedule retry if attempts remaining
                if delivery.attempt_count < delivery.max_attempts:
                    # Exponential backoff
                    backoff_seconds = webhook.retry_backoff_seconds * (2 ** (delivery.attempt_count - 1))
                    delivery.next_retry_at = datetime.utcnow() + timedelta(seconds=backoff_seconds)
                    delivery.status = "retrying"
                else:
                    delivery.status = "failed"
                    webhook.failed_deliveries += 1
                    webhook.last_failure_at = datetime.utcnow()
                
                db.commit()
                return False
                
        except Exception as e:
            # Handle delivery errors
            delivery.error_message = str(e)[:1000]
            
            # Schedule retry if attempts remaining
            if delivery.attempt_count < delivery.max_attempts:
                backoff_seconds = webhook.retry_backoff_seconds * (2 ** (delivery.attempt_count - 1))
                delivery.next_retry_at = datetime.utcnow() + timedelta(seconds=backoff_seconds)
                delivery.status = "retrying"
            else:
                delivery.status = "failed"
                webhook.failed_deliveries += 1
                webhook.last_failure_at = datetime.utcnow()
            
            db.commit()
            return False
    
    @staticmethod
    def test_webhook(
        db: Session,
        webhook_id: str,
        tenant_id: str,
        event_type: str = "test.webhook",
        test_data: dict = None
    ) -> dict:
        """Test a webhook by sending a test payload"""
        webhook = WebhookService.get_webhook_by_id(db, webhook_id, tenant_id)
        if not webhook:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Webhook not found"
            )
        
        # Prepare test payload
        test_data = test_data or {"message": "This is a test webhook"}
        payload_data = {
            "event": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "webhook_id": webhook.id,
            "data": test_data
        }
        
        payload_json = json.dumps(payload_data)
        signature = WebhookService.generate_signature(payload_json, webhook.secret)
        
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
            "X-Webhook-Event": event_type,
            "User-Agent": "NexBII-Webhooks/1.0"
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                webhook.url,
                data=payload_json,
                headers=headers,
                timeout=30
            )
            response_time_ms = int((time.time() - start_time) * 1000)
            
            return {
                "success": 200 <= response.status_code < 300,
                "status_code": response.status_code,
                "response_time_ms": response_time_ms,
                "response_body": response.text[:1000],
                "error_message": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "status_code": None,
                "response_time_ms": None,
                "response_body": None,
                "error_message": str(e)
            }
    
    @staticmethod
    def get_webhook_deliveries(
        db: Session,
        webhook_id: str,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[str] = None
    ) -> List[WebhookDelivery]:
        """Get delivery logs for a webhook"""
        # Verify webhook ownership
        webhook = WebhookService.get_webhook_by_id(db, webhook_id, tenant_id)
        if not webhook:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Webhook not found"
            )
        
        query = db.query(WebhookDelivery).filter(
            WebhookDelivery.webhook_id == webhook_id
        )
        
        if status_filter:
            query = query.filter(WebhookDelivery.status == status_filter)
        
        return query.order_by(WebhookDelivery.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_webhook_stats(
        db: Session,
        webhook_id: str,
        tenant_id: str
    ) -> WebhookStatsResponse:
        """Get statistics for a webhook"""
        webhook = WebhookService.get_webhook_by_id(db, webhook_id, tenant_id)
        if not webhook:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Webhook not found"
            )
        
        now = datetime.utcnow()
        
        # Get delivery counts
        deliveries_24h = db.query(func.count(WebhookDelivery.id)).filter(
            WebhookDelivery.webhook_id == webhook_id,
            WebhookDelivery.created_at >= now - timedelta(hours=24)
        ).scalar() or 0
        
        deliveries_7d = db.query(func.count(WebhookDelivery.id)).filter(
            WebhookDelivery.webhook_id == webhook_id,
            WebhookDelivery.created_at >= now - timedelta(days=7)
        ).scalar() or 0
        
        deliveries_30d = db.query(func.count(WebhookDelivery.id)).filter(
            WebhookDelivery.webhook_id == webhook_id,
            WebhookDelivery.created_at >= now - timedelta(days=30)
        ).scalar() or 0
        
        # Average response time (successful deliveries only)
        avg_response_time = db.query(func.avg(WebhookDelivery.response_time_ms)).filter(
            WebhookDelivery.webhook_id == webhook_id,
            WebhookDelivery.status == "success",
            WebhookDelivery.response_time_ms.isnot(None)
        ).scalar()
        
        # Success rate
        success_rate = 0.0
        if webhook.total_deliveries > 0:
            success_rate = (webhook.successful_deliveries / webhook.total_deliveries) * 100
        
        # Recent deliveries
        recent_deliveries = db.query(WebhookDelivery).filter(
            WebhookDelivery.webhook_id == webhook_id
        ).order_by(WebhookDelivery.created_at.desc()).limit(10).all()
        
        return WebhookStatsResponse(
            webhook_id=webhook.id,
            webhook_name=webhook.name,
            total_deliveries=webhook.total_deliveries,
            successful_deliveries=webhook.successful_deliveries,
            failed_deliveries=webhook.failed_deliveries,
            success_rate=round(success_rate, 2),
            avg_response_time_ms=avg_response_time,
            deliveries_last_24h=deliveries_24h,
            deliveries_last_7d=deliveries_7d,
            deliveries_last_30d=deliveries_30d,
            recent_deliveries=[
                WebhookDeliveryResponse(
                    id=d.id,
                    webhook_id=d.webhook_id,
                    event_type=d.event_type,
                    status=d.status,
                    attempt_count=d.attempt_count,
                    max_attempts=d.max_attempts,
                    response_status_code=d.response_status_code,
                    response_time_ms=d.response_time_ms,
                    error_message=d.error_message,
                    next_retry_at=d.next_retry_at,
                    created_at=d.created_at,
                    delivered_at=d.delivered_at
                )
                for d in recent_deliveries
            ]
        )
