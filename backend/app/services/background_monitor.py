"""
Background monitoring service for alerts and subscriptions

This service runs in a separate thread and checks alerts and sends subscription emails
"""

import threading
import time
import logging
from datetime import datetime
from app.core.database import SessionLocal
from app.services.alert_service import AlertService
from app.services.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)

class BackgroundMonitor:
    """Background service for monitoring alerts and subscriptions"""
    
    def __init__(self, check_interval: int = 300):  # 5 minutes default
        self.check_interval = check_interval
        self.running = False
        self.thread = None
    
    def start(self):
        """Start the background monitoring thread"""
        if self.running:
            logger.warning("Background monitor is already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info(f"✅ Background monitor started (checking every {self.check_interval}s)")
    
    def stop(self):
        """Stop the background monitoring thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=10)
        logger.info("🛑 Background monitor stopped")
    
    def _run(self):
        """Main monitoring loop"""
        while self.running:
            try:
                self._check_alerts()
                self._send_subscriptions()
            except Exception as e:
                logger.error(f"Error in background monitor: {str(e)}")
            
            # Sleep for the check interval
            time.sleep(self.check_interval)
    
    def _check_alerts(self):
        """Check and evaluate due alerts"""
        db = SessionLocal()
        try:
            results = AlertService.check_all_alerts(db)
            if results['checked'] > 0:
                logger.info(
                    f"🔔 Alert check: {results['checked']} checked, "
                    f"{results['triggered']} triggered, {results['errors']} errors"
                )
        except Exception as e:
            logger.error(f"Error checking alerts: {str(e)}")
        finally:
            db.close()
    
    def _send_subscriptions(self):
        """Send due subscription emails"""
        db = SessionLocal()
        try:
            sent_count = SubscriptionService.send_subscription_emails(db)
            if sent_count > 0:
                logger.info(f"📧 Sent {sent_count} subscription emails")
        except Exception as e:
            logger.error(f"Error sending subscriptions: {str(e)}")
        finally:
            db.close()

# Global instance
background_monitor = BackgroundMonitor(check_interval=300)  # Check every 5 minutes
