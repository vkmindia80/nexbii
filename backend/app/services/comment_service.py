from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import re
from ..models.comment import Comment
from ..models.user import User
from ..models.dashboard import Dashboard
from ..models.query import Query
from ..models.activity import Activity, ActivityType
from .email_service import EmailService

logger = logging.getLogger(__name__)

class CommentService:
    """Service for managing comments and mentions"""
    
    @staticmethod
    def create_comment(
        db: Session,
        user_id: str,
        content: str,
        dashboard_id: Optional[str] = None,
        query_id: Optional[str] = None,
        parent_id: Optional[str] = None
    ) -> Comment:
        """Create a new comment with mention detection"""
        
        # Extract mentions from content (e.g., @user123)
        mentions = CommentService._extract_mentions(content)
        
        comment = Comment(
            user_id=user_id,
            content=content,
            dashboard_id=dashboard_id,
            query_id=query_id,
            parent_id=parent_id,
            mentions=mentions
        )
        
        db.add(comment)
        db.commit()
        db.refresh(comment)
        
        # Create activity
        CommentService._create_comment_activity(db, comment, user_id)
        
        # Send mention notifications
        if mentions:
            CommentService._send_mention_notifications(db, comment, mentions, user_id)
        
        logger.info(f"Created comment {comment.id} by user {user_id}")
        return comment
    
    @staticmethod
    def get_comments(
        db: Session,
        dashboard_id: Optional[str] = None,
        query_id: Optional[str] = None,
        parent_id: Optional[str] = None
    ) -> List[Comment]:
        """Get comments for a dashboard or query"""
        query_obj = db.query(Comment)
        
        if dashboard_id:
            query_obj = query_obj.filter(Comment.dashboard_id == dashboard_id)
        if query_id:
            query_obj = query_obj.filter(Comment.query_id == query_id)
        if parent_id is not None:
            query_obj = query_obj.filter(Comment.parent_id == parent_id)
        
        return query_obj.order_by(Comment.created_at.desc()).all()
    
    @staticmethod
    def update_comment(
        db: Session,
        comment_id: str,
        user_id: str,
        content: str
    ) -> Optional[Comment]:
        """Update a comment (only by owner)"""
        comment = db.query(Comment).filter(
            Comment.id == comment_id,
            Comment.user_id == user_id
        ).first()
        
        if not comment:
            return None
        
        # Update mentions
        mentions = CommentService._extract_mentions(content)
        comment.content = content
        comment.mentions = mentions
        
        db.commit()
        db.refresh(comment)
        return comment
    
    @staticmethod
    def delete_comment(
        db: Session,
        comment_id: str,
        user_id: str
    ) -> bool:
        """Delete a comment (only by owner)"""
        comment = db.query(Comment).filter(
            Comment.id == comment_id,
            Comment.user_id == user_id
        ).first()
        
        if comment:
            db.delete(comment)
            db.commit()
            return True
        return False
    
    @staticmethod
    def _extract_mentions(content: str) -> List[str]:
        """Extract user mentions from comment content"""
        # Match @username or @user_id patterns
        pattern = r'@([a-zA-Z0-9_-]+)'
        matches = re.findall(pattern, content)
        return list(set(matches))  # Remove duplicates
    
    @staticmethod
    def _create_comment_activity(
        db: Session,
        comment: Comment,
        user_id: str
    ):
        """Create activity for new comment"""
        entity_type = "dashboard" if comment.dashboard_id else "query"
        entity_id = comment.dashboard_id or comment.query_id
        
        activity = Activity(
            user_id=user_id,
            activity_type=ActivityType.COMMENT_ADDED,
            entity_type=entity_type,
            entity_id=entity_id,
            description=f"Added a comment: {comment.content[:50]}...",
            activity_metadata={
                "comment_id": comment.id,
                "mentions": comment.mentions
            }
        )
        db.add(activity)
        db.commit()
    
    @staticmethod
    def _send_mention_notifications(
        db: Session,
        comment: Comment,
        mentions: List[str],
        commenter_id: str
    ):
        """Send email notifications to mentioned users"""
        commenter = db.query(User).filter(User.id == commenter_id).first()
        if not commenter:
            return
        
        # Get entity info
        entity_type = "dashboard" if comment.dashboard_id else "query"
        entity_id = comment.dashboard_id or comment.query_id
        
        if entity_type == "dashboard":
            entity = db.query(Dashboard).filter(Dashboard.id == entity_id).first()
        else:
            entity = db.query(Query).filter(Query.id == entity_id).first()
        
        entity_name = entity.name if entity else "Unknown"
        entity_url = f"https://yourapp.com/{entity_type}s/{entity_id}"
        
        # Find mentioned users
        for mention in mentions:
            # Try to find user by email (assuming mention is email username)
            user = db.query(User).filter(User.email.like(f"{mention}%")).first()
            
            if user and user.id != commenter_id:
                EmailService.send_mention_notification(
                    to_email=user.email,
                    mentioned_by=commenter.full_name or commenter.email,
                    comment_text=comment.content,
                    entity_type=entity_type,
                    entity_name=entity_name,
                    entity_url=entity_url
                )
                
                # Create activity for mention
                activity = Activity(
                    user_id=user.id,
                    activity_type=ActivityType.USER_MENTIONED,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    description=f"You were mentioned by {commenter.full_name or commenter.email}",
                    metadata={
                        "comment_id": comment.id,
                        "mentioned_by": commenter_id
                    }
                )
                db.add(activity)
        
        db.commit()