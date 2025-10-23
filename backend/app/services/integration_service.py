"""Integration service for managing email and Slack configurations with encryption"""

import os
import logging
from typing import Optional, Tuple
from cryptography.fernet import Fernet
import base64
from sqlalchemy.orm import Session
from ..models.integration import Integration
from ..schemas.integration import EmailConfigCreate, SlackConfigCreate

logger = logging.getLogger(__name__)

# Encryption key - In production, store this securely (e.g., AWS Secrets Manager, environment variable)
ENCRYPTION_KEY = os.getenv("INTEGRATION_ENCRYPTION_KEY", "")

if not ENCRYPTION_KEY:
    # Use a static default key for development (DO NOT use in production)
    # This is a valid Fernet key generated with Fernet.generate_key()
    ENCRYPTION_KEY = "dJIqJ2H98c8bzKs4fD7e4j_W0sCmyHalWpsTWmXEJXM="
    logger.warning("⚠️  Using default encryption key. Set INTEGRATION_ENCRYPTION_KEY in production!")

cipher_suite = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)

class IntegrationService:
    """Service for managing encrypted integration configurations"""
    
    @staticmethod
    def encrypt_value(value: str) -> str:
        """Encrypt a string value"""
        if not value:
            return ""
        try:
            encrypted = cipher_suite.encrypt(value.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            return ""
    
    @staticmethod
    def decrypt_value(encrypted_value: str) -> str:
        """Decrypt a string value"""
        if not encrypted_value:
            return ""
        try:
            decrypted = cipher_suite.decrypt(encrypted_value.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return ""
    
    @staticmethod
    def get_or_create_integration(db: Session, user_id: str) -> Integration:
        """Get existing integration config or create new one"""
        integration = db.query(Integration).first()
        
        if not integration:
            integration = Integration(
                created_by=user_id,
                mock_email=True,
                mock_slack=True
            )
            db.add(integration)
            db.commit()
            db.refresh(integration)
            logger.info("Created new integration configuration")
        
        return integration
    
    @staticmethod
    def save_email_config(
        db: Session,
        user_id: str,
        email_config: EmailConfigCreate
    ) -> Integration:
        """Save email configuration with encryption"""
        integration = IntegrationService.get_or_create_integration(db, user_id)
        
        # Update email fields with encryption for sensitive data
        integration.smtp_host = email_config.smtp_host
        integration.smtp_port = str(email_config.smtp_port) if email_config.smtp_port else None
        integration.smtp_user = IntegrationService.encrypt_value(email_config.smtp_user) if email_config.smtp_user else None
        integration.smtp_password = IntegrationService.encrypt_value(email_config.smtp_password) if email_config.smtp_password else None
        integration.from_email = email_config.from_email
        integration.from_name = email_config.from_name
        integration.mock_email = email_config.mock_email
        integration.created_by = user_id
        
        db.commit()
        db.refresh(integration)
        
        logger.info(f"Email configuration saved by user {user_id}")
        return integration
    
    @staticmethod
    def save_slack_config(
        db: Session,
        user_id: str,
        slack_config: SlackConfigCreate
    ) -> Integration:
        """Save Slack configuration with encryption"""
        integration = IntegrationService.get_or_create_integration(db, user_id)
        
        # Update Slack fields with encryption
        integration.slack_webhook_url = IntegrationService.encrypt_value(slack_config.slack_webhook_url) if slack_config.slack_webhook_url else None
        integration.mock_slack = slack_config.mock_slack
        integration.created_by = user_id
        
        db.commit()
        db.refresh(integration)
        
        logger.info(f"Slack configuration saved by user {user_id}")
        return integration
    
    @staticmethod
    def get_email_config(db: Session) -> Tuple[Optional[dict], bool]:
        """Get decrypted email configuration"""
        integration = db.query(Integration).first()
        
        if not integration:
            return None, True
        
        return {
            'smtp_host': integration.smtp_host,
            'smtp_port': int(integration.smtp_port) if integration.smtp_port else 587,
            'smtp_user': IntegrationService.decrypt_value(integration.smtp_user) if integration.smtp_user else None,
            'smtp_password': IntegrationService.decrypt_value(integration.smtp_password) if integration.smtp_password else None,
            'from_email': integration.from_email,
            'from_name': integration.from_name,
        }, integration.mock_email
    
    @staticmethod
    def get_slack_config(db: Session) -> Tuple[Optional[str], bool]:
        """Get decrypted Slack webhook URL"""
        integration = db.query(Integration).first()
        
        if not integration or not integration.slack_webhook_url:
            return None, True
        
        webhook_url = IntegrationService.decrypt_value(integration.slack_webhook_url)
        return webhook_url, integration.mock_slack
