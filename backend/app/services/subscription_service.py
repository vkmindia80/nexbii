from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import logging
from ..models.subscription import EmailSubscription, SubscriptionFrequency
from ..models.user import User
from ..models.dashboard import Dashboard
from .email_service import EmailService

logger = logging.getLogger(__name__)

class SubscriptionService:
    """Service for managing email subscriptions"""
    
    @staticmethod
    def create_subscription(
        db: Session,
        user_id: str,
        dashboard_id: str,
        frequency: SubscriptionFrequency
    ) -> EmailSubscription:
        """Create a new email subscription"""
        
        # Check if subscription already exists
        existing = db.query(EmailSubscription).filter(
            EmailSubscription.user_id == user_id,
            EmailSubscription.dashboard_id == dashboard_id
        ).first()
        
        if existing:
            # Update existing subscription
            existing.frequency = frequency
            existing.is_active = True
            existing.next_send_date = SubscriptionService._calculate_next_send_date(frequency)
            db.commit()
            db.refresh(existing)
            return existing
        
        # Create new subscription
        subscription = EmailSubscription(
            user_id=user_id,
            dashboard_id=dashboard_id,
            frequency=frequency,
            next_send_date=SubscriptionService._calculate_next_send_date(frequency)
        )
        
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        
        logger.info(f"Created subscription for user {user_id} to dashboard {dashboard_id}")
        return subscription
    
    @staticmethod
    def get_user_subscriptions(
        db: Session,
        user_id: str,
        dashboard_id: Optional[str] = None
    ) -> List[EmailSubscription]:
        """Get all subscriptions for a user"""
        query = db.query(EmailSubscription).filter(
            EmailSubscription.user_id == user_id
        )
        
        if dashboard_id:
            query = query.filter(EmailSubscription.dashboard_id == dashboard_id)
        
        return query.all()
    
    @staticmethod
    def delete_subscription(db: Session, subscription_id: str, user_id: str) -> bool:
        """Delete a subscription"""
        subscription = db.query(EmailSubscription).filter(
            EmailSubscription.id == subscription_id,
            EmailSubscription.user_id == user_id
        ).first()
        
        if subscription:
            db.delete(subscription)
            db.commit()
            return True
        return False
    
    @staticmethod
    def update_subscription(
        db: Session,
        subscription_id: str,
        user_id: str,
        **kwargs
    ) -> Optional[EmailSubscription]:
        """Update subscription settings"""
        subscription = db.query(EmailSubscription).filter(
            EmailSubscription.id == subscription_id,
            EmailSubscription.user_id == user_id
        ).first()
        
        if not subscription:
            return None
        
        for key, value in kwargs.items():
            if hasattr(subscription, key) and value is not None:
                setattr(subscription, key, value)
        
        if 'frequency' in kwargs:
            subscription.next_send_date = SubscriptionService._calculate_next_send_date(
                kwargs['frequency']
            )
        
        db.commit()
        db.refresh(subscription)
        return subscription
    
    @staticmethod
    def get_due_subscriptions(db: Session) -> List[EmailSubscription]:
        """Get subscriptions that are due to be sent"""
        now = datetime.utcnow()
        return db.query(EmailSubscription).filter(
            EmailSubscription.is_active == True,
            EmailSubscription.next_send_date <= now
        ).all()
    
    @staticmethod
    def send_subscription_emails(db: Session) -> int:
        """Process and send due subscription emails"""
        due_subscriptions = SubscriptionService.get_due_subscriptions(db)
        sent_count = 0
        
        for subscription in due_subscriptions:
            try:
                # Get user and dashboard
                user = db.query(User).filter(User.id == subscription.user_id).first()
                dashboard = db.query(Dashboard).filter(
                    Dashboard.id == subscription.dashboard_id
                ).first()
                
                if not user or not dashboard:
                    continue
                
                # Send email
                success = EmailService.send_subscription_email(
                    to_email=user.email,
                    dashboard_name=dashboard.name,
                    dashboard_url=f"https://yourapp.com/dashboards/{dashboard.id}",
                    dashboard_data={},  # You can add actual dashboard data here
                    frequency=subscription.frequency.value
                )
                
                if success:
                    # Update subscription
                    subscription.last_sent_date = datetime.utcnow()
                    subscription.next_send_date = SubscriptionService._calculate_next_send_date(
                        subscription.frequency
                    )
                    db.commit()
                    sent_count += 1
                    
            except Exception as e:
                logger.error(f"Failed to send subscription email: {str(e)}")
                continue
        
        logger.info(f"Sent {sent_count} subscription emails")
        return sent_count
    
    @staticmethod
    def _calculate_next_send_date(frequency: SubscriptionFrequency) -> datetime:
        """Calculate next send date based on frequency"""
        now = datetime.utcnow()
        
        if frequency == SubscriptionFrequency.DAILY:
            return now + timedelta(days=1)
        elif frequency == SubscriptionFrequency.WEEKLY:
            return now + timedelta(weeks=1)
        elif frequency == SubscriptionFrequency.MONTHLY:
            return now + timedelta(days=30)
        
        return now + timedelta(days=1)