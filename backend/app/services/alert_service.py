from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging
from ..models.alert import Alert, AlertHistory, AlertConditionType, AlertFrequency, AlertStatus
from ..models.query import Query
from ..models.user import User
from ..models.activity import Activity, ActivityType
from .query_service import QueryService
from .email_service import EmailService

logger = logging.getLogger(__name__)

class AlertService:
    """Service for managing alerts and notifications"""
    
    @staticmethod
    def create_alert(
        db: Session,
        user_id: str,
        name: str,
        query_id: str,
        condition_type: AlertConditionType,
        metric_column: str,
        threshold_value: Optional[float] = None,
        threshold_value_2: Optional[float] = None,
        frequency: AlertFrequency = AlertFrequency.ONCE,
        notify_emails: List[str] = [],
        **kwargs
    ) -> Alert:
        """Create a new alert"""
        
        alert = Alert(
            user_id=user_id,
            name=name,
            query_id=query_id,
            condition_type=condition_type,
            metric_column=metric_column,
            threshold_value=threshold_value,
            threshold_value_2=threshold_value_2,
            frequency=frequency,
            notify_emails=notify_emails,
            next_check_at=AlertService._calculate_next_check(frequency),
            **kwargs
        )
        
        db.add(alert)
        db.commit()
        db.refresh(alert)
        
        # Create activity
        activity = Activity(
            user_id=user_id,
            activity_type=ActivityType.ALERT_TRIGGERED,
            entity_type="alert",
            entity_id=alert.id,
            entity_name=name,
            description=f"Created alert: {name}"
        )
        db.add(activity)
        db.commit()
        
        logger.info(f"Created alert {alert.id} for user {user_id}")
        return alert
    
    @staticmethod
    def get_user_alerts(
        db: Session,
        user_id: str,
        status: Optional[AlertStatus] = None
    ) -> List[Alert]:
        """Get all alerts for a user"""
        query = db.query(Alert).filter(Alert.user_id == user_id)
        
        if status:
            query = query.filter(Alert.status == status)
        
        return query.order_by(Alert.created_at.desc()).all()
    
    @staticmethod
    def get_alert(db: Session, alert_id: str, user_id: str) -> Optional[Alert]:
        """Get a specific alert"""
        return db.query(Alert).filter(
            Alert.id == alert_id,
            Alert.user_id == user_id
        ).first()
    
    @staticmethod
    def update_alert(
        db: Session,
        alert_id: str,
        user_id: str,
        **kwargs
    ) -> Optional[Alert]:
        """Update an alert"""
        alert = AlertService.get_alert(db, alert_id, user_id)
        if not alert:
            return None
        
        for key, value in kwargs.items():
            if hasattr(alert, key) and value is not None:
                setattr(alert, key, value)
        
        if 'frequency' in kwargs:
            alert.next_check_at = AlertService._calculate_next_check(kwargs['frequency'])
        
        db.commit()
        db.refresh(alert)
        return alert
    
    @staticmethod
    def delete_alert(db: Session, alert_id: str, user_id: str) -> bool:
        """Delete an alert"""
        alert = AlertService.get_alert(db, alert_id, user_id)
        if alert:
            db.delete(alert)
            db.commit()
            return True
        return False
    
    @staticmethod
    def check_alert_condition(
        db: Session,
        alert: Alert,
        query_result: List[dict]
    ) -> tuple[bool, Optional[float]]:
        """
        Check if alert condition is met
        
        Returns:
            tuple: (condition_met: bool, actual_value: Optional[float])
        """
        if not query_result:
            return False, None
        
        # Get the first row's metric value
        first_row = query_result[0]
        if alert.metric_column not in first_row:
            logger.warning(f"Metric column {alert.metric_column} not found in query result")
            return False, None
        
        actual_value = float(first_row[alert.metric_column])
        condition_met = False
        
        if alert.condition_type == AlertConditionType.GREATER_THAN:
            condition_met = actual_value > alert.threshold_value
        elif alert.condition_type == AlertConditionType.LESS_THAN:
            condition_met = actual_value < alert.threshold_value
        elif alert.condition_type == AlertConditionType.EQUALS:
            condition_met = actual_value == alert.threshold_value
        elif alert.condition_type == AlertConditionType.NOT_EQUALS:
            condition_met = actual_value != alert.threshold_value
        elif alert.condition_type == AlertConditionType.BETWEEN:
            condition_met = alert.threshold_value <= actual_value <= alert.threshold_value_2
        
        return condition_met, actual_value
    
    @staticmethod
    def evaluate_alert(db: Session, alert: Alert) -> bool:
        """
        Evaluate an alert and send notification if triggered
        
        Returns:
            bool: True if alert was triggered and notification sent
        """
        try:
            # Get query
            query = db.query(Query).filter(Query.id == alert.query_id).first()
            if not query:
                logger.error(f"Query {alert.query_id} not found for alert {alert.id}")
                return False
            
            # Execute query
            query_result = QueryService.execute_query_sql(
                db=db,
                datasource_id=query.datasource_id,
                sql_query=query.sql_query
            )
            
            if not query_result or 'data' not in query_result:
                return False
            
            # Check condition
            condition_met, actual_value = AlertService.check_alert_condition(
                db, alert, query_result['data']
            )
            
            # Create history record
            history = AlertHistory(
                alert_id=alert.id,
                condition_met=condition_met,
                actual_value=actual_value,
                threshold_value=alert.threshold_value,
                query_result=query_result['data'][:5] if query_result['data'] else []  # Store first 5 rows
            )
            
            # Send notification if condition is met
            if condition_met:
                notification_sent = AlertService._send_alert_notification(
                    db, alert, actual_value
                )
                history.notification_sent = notification_sent
                
                # Update alert status
                alert.last_triggered_at = datetime.utcnow()
                alert.status = AlertStatus.TRIGGERED
                
                # Create activity
                activity = Activity(
                    user_id=alert.user_id,
                    activity_type=ActivityType.ALERT_TRIGGERED,
                    entity_type="alert",
                    entity_id=alert.id,
                    entity_name=alert.name,
                    description=f"Alert triggered: {alert.name} (value: {actual_value})"
                )
                db.add(activity)
            
            # Update alert
            alert.last_checked_at = datetime.utcnow()
            alert.next_check_at = AlertService._calculate_next_check(alert.frequency)
            
            db.add(history)
            db.commit()
            
            return condition_met
            
        except Exception as e:
            logger.error(f"Error evaluating alert {alert.id}: {str(e)}")
            
            # Create error history
            history = AlertHistory(
                alert_id=alert.id,
                condition_met=False,
                notification_sent=False,
                notification_error=str(e)
            )
            db.add(history)
            db.commit()
            
            return False
    
    @staticmethod
    def get_due_alerts(db: Session) -> List[Alert]:
        """Get alerts that are due for checking"""
        now = datetime.utcnow()
        return db.query(Alert).filter(
            Alert.is_active == True,
            Alert.status != AlertStatus.SNOOZED,
            Alert.next_check_at <= now
        ).all()
    
    @staticmethod
    def check_all_alerts(db: Session) -> dict:
        """Check all due alerts"""
        due_alerts = AlertService.get_due_alerts(db)
        
        results = {
            'checked': 0,
            'triggered': 0,
            'errors': 0
        }
        
        for alert in due_alerts:
            try:
                results['checked'] += 1
                triggered = AlertService.evaluate_alert(db, alert)
                if triggered:
                    results['triggered'] += 1
            except Exception as e:
                logger.error(f"Error checking alert {alert.id}: {str(e)}")
                results['errors'] += 1
        
        logger.info(f"Checked {results['checked']} alerts, {results['triggered']} triggered")
        return results
    
    @staticmethod
    def get_alert_history(
        db: Session,
        alert_id: str,
        limit: int = 50
    ) -> List[AlertHistory]:
        """Get alert history"""
        return db.query(AlertHistory).filter(
            AlertHistory.alert_id == alert_id
        ).order_by(
            AlertHistory.triggered_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def snooze_alert(
        db: Session,
        alert_id: str,
        user_id: str,
        hours: int = 24
    ) -> Optional[Alert]:
        """Snooze an alert for specified hours"""
        alert = AlertService.get_alert(db, alert_id, user_id)
        if not alert:
            return None
        
        alert.status = AlertStatus.SNOOZED
        alert.snooze_until = datetime.utcnow() + timedelta(hours=hours)
        
        db.commit()
        db.refresh(alert)
        return alert
    
    @staticmethod
    def _send_alert_notification(
        db: Session,
        alert: Alert,
        actual_value: float
    ) -> bool:
        """Send alert notification via email"""
        if not alert.notify_emails:
            return False
        
        # Get query name
        query = db.query(Query).filter(Query.id == alert.query_id).first()
        query_name = query.name if query else "Unknown Query"
        
        # Build condition description
        condition_desc = AlertService._format_condition_description(
            alert.condition_type,
            alert.threshold_value,
            alert.threshold_value_2
        )
        
        # Send email
        return EmailService.send_alert_notification(
            to_emails=alert.notify_emails,
            alert_name=alert.name,
            condition_description=condition_desc,
            actual_value=actual_value,
            threshold_value=alert.threshold_value,
            query_name=query_name
        )
    
    @staticmethod
    def _format_condition_description(
        condition_type: AlertConditionType,
        threshold: float,
        threshold_2: Optional[float] = None
    ) -> str:
        """Format alert condition for display"""
        if condition_type == AlertConditionType.GREATER_THAN:
            return f"Value greater than {threshold}"
        elif condition_type == AlertConditionType.LESS_THAN:
            return f"Value less than {threshold}"
        elif condition_type == AlertConditionType.EQUALS:
            return f"Value equals {threshold}"
        elif condition_type == AlertConditionType.NOT_EQUALS:
            return f"Value not equals {threshold}"
        elif condition_type == AlertConditionType.BETWEEN:
            return f"Value between {threshold} and {threshold_2}"
        return "Unknown condition"
    
    @staticmethod
    def _calculate_next_check(frequency: AlertFrequency) -> datetime:
        """Calculate next check time based on frequency"""
        now = datetime.utcnow()
        
        if frequency == AlertFrequency.HOURLY:
            return now + timedelta(hours=1)
        elif frequency == AlertFrequency.DAILY:
            return now + timedelta(days=1)
        elif frequency == AlertFrequency.WEEKLY:
            return now + timedelta(weeks=1)
        else:  # ONCE
            return now + timedelta(minutes=5)  # Check again in 5 minutes
