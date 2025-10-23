from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from ..models.activity import Activity, ActivityType

class ActivityService:
    """Service for managing activity feed"""
    
    @staticmethod
    def create_activity(
        db: Session,
        user_id: str,
        activity_type: ActivityType,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        entity_name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> Activity:
        """Create a new activity entry"""
        activity = Activity(
            user_id=user_id,
            activity_type=activity_type,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=entity_name,
            description=description,
            metadata=metadata
        )
        
        db.add(activity)
        db.commit()
        db.refresh(activity)
        return activity
    
    @staticmethod
    def get_user_activities(
        db: Session,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Activity]:
        """Get activities for a specific user"""
        return db.query(Activity).filter(
            Activity.user_id == user_id
        ).order_by(
            Activity.created_at.desc()
        ).limit(limit).offset(offset).all()
    
    @staticmethod
    def get_all_activities(
        db: Session,
        limit: int = 100,
        offset: int = 0,
        activity_types: Optional[List[ActivityType]] = None,
        days: Optional[int] = None
    ) -> List[Activity]:
        """Get all activities with optional filters"""
        query = db.query(Activity)
        
        if activity_types:
            query = query.filter(Activity.activity_type.in_(activity_types))
        
        if days:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(Activity.created_at >= cutoff_date)
        
        return query.order_by(
            Activity.created_at.desc()
        ).limit(limit).offset(offset).all()
    
    @staticmethod
    def get_entity_activities(
        db: Session,
        entity_type: str,
        entity_id: str,
        limit: int = 50
    ) -> List[Activity]:
        """Get all activities for a specific entity"""
        return db.query(Activity).filter(
            Activity.entity_type == entity_type,
            Activity.entity_id == entity_id
        ).order_by(
            Activity.created_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def delete_old_activities(db: Session, days: int = 90) -> int:
        """Delete activities older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        deleted = db.query(Activity).filter(
            Activity.created_at < cutoff_date
        ).delete()
        db.commit()
        return deleted