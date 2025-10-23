"""Integration management endpoints - Admin only"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict
from ...core.database import get_db
from ...core.security import get_current_user
from ...models.user import User, UserRole
from ...schemas.integration import (
    EmailConfigCreate,
    EmailConfigResponse,
    SlackConfigCreate,
    SlackConfigResponse,
    TestEmailRequest,
    TestSlackRequest
)
from ...services.integration_service import IntegrationService
from ...services.email_service import EmailService
from ...services.slack_service import SlackService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

def require_admin(current_user: User = Depends(get_current_user)):
    """Require admin role for integration management"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can manage integrations"
        )
    return current_user

@router.get("/email", response_model=EmailConfigResponse)
async def get_email_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get email configuration (admin only)"""
    integration = IntegrationService.get_or_create_integration(db, current_user.id)
    
    # Decrypt sensitive fields for display (but not password)
    smtp_user = IntegrationService.decrypt_value(integration.smtp_user) if integration.smtp_user else None
    
    return EmailConfigResponse(
        smtp_host=integration.smtp_host,
        smtp_port=int(integration.smtp_port) if integration.smtp_port else None,
        smtp_user=smtp_user,
        from_email=integration.from_email,
        from_name=integration.from_name,
        mock_email=integration.mock_email
    )

@router.post("/email", response_model=EmailConfigResponse)
async def save_email_config(
    email_config: EmailConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Save email configuration (admin only)"""
    try:
        integration = IntegrationService.save_email_config(db, current_user.id, email_config)
        
        # Return response without password
        smtp_user = IntegrationService.decrypt_value(integration.smtp_user) if integration.smtp_user else None
        
        return EmailConfigResponse(
            smtp_host=integration.smtp_host,
            smtp_port=int(integration.smtp_port) if integration.smtp_port else None,
            smtp_user=smtp_user,
            from_email=integration.from_email,
            from_name=integration.from_name,
            mock_email=integration.mock_email
        )
    except Exception as e:
        logger.error(f"Error saving email config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save email configuration"
        )

@router.post("/email/test")
async def test_email_config(
    test_request: TestEmailRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Test email configuration by sending a test email"""
    try:
        # Get email config from database
        email_config, mock_mode = IntegrationService.get_email_config(db)
        
        if not email_config or not email_config.get('smtp_host'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email configuration is incomplete. Please configure SMTP settings first."
            )
        
        # Temporarily override environment variables for this test
        import os
        original_values = {}
        try:
            # Save original values
            for key in ['SMTP_HOST', 'SMTP_PORT', 'SMTP_USER', 'SMTP_PASSWORD', 'FROM_EMAIL', 'FROM_NAME', 'MOCK_EMAIL']:
                original_values[key] = os.getenv(key)
            
            # Set config values
            os.environ['SMTP_HOST'] = email_config['smtp_host']
            os.environ['SMTP_PORT'] = str(email_config['smtp_port'])
            os.environ['SMTP_USER'] = email_config['smtp_user'] or ''
            os.environ['SMTP_PASSWORD'] = email_config['smtp_password'] or ''
            os.environ['FROM_EMAIL'] = email_config['from_email'] or 'noreply@nexbii.com'
            os.environ['FROM_NAME'] = email_config['from_name'] or 'NexBII Analytics'
            os.environ['MOCK_EMAIL'] = 'true' if mock_mode else 'false'
            
            # Send test email
            subject = "🧪 NexBII Email Configuration Test"
            html_content = f"""
            <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                 color: white; padding: 20px; text-align: center; border-radius: 8px; }}
                        .content {{ padding: 20px; }}
                        .success {{ background: #d4edda; color: #155724; padding: 15px; 
                                   border-radius: 6px; margin: 15px 0; }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>✅ Email Test Successful!</h1>
                    </div>
                    <div class="content">
                        <div class="success">
                            <strong>Congratulations!</strong> Your email configuration is working correctly.
                        </div>
                        <p>This is a test email from NexBII Analytics Platform.</p>
                        <p>Your SMTP settings have been configured successfully and you can now receive:</p>
                        <ul>
                            <li>📊 Dashboard subscriptions</li>
                            <li>🔔 Alert notifications</li>
                            <li>💬 Comment mentions</li>
                            <li>📈 Scheduled reports</li>
                        </ul>
                        <p><strong>Mode:</strong> {'Mock Mode (emails logged only)' if mock_mode else 'Production Mode (real emails)'}</p>
                    </div>
                </body>
            </html>
            """
            
            text_content = f"NexBII Email Test - Your email configuration is working! Mode: {'Mock' if mock_mode else 'Production'}"
            
            success = EmailService.send_email(
                to_emails=[test_request.test_email],
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
            if success:
                return {
                    "success": True,
                    "message": f"Test email sent successfully to {test_request.test_email}" + (" (Mock mode - check logs)" if mock_mode else ""),
                    "mock_mode": mock_mode
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to send test email. Check your SMTP settings."
                )
        finally:
            # Restore original values
            for key, value in original_values.items():
                if value is not None:
                    os.environ[key] = value
                elif key in os.environ:
                    del os.environ[key]
                    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Email test failed: {str(e)}"
        )

@router.get("/slack", response_model=SlackConfigResponse)
async def get_slack_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get Slack configuration (admin only)"""
    integration = IntegrationService.get_or_create_integration(db, current_user.id)
    
    # Decrypt webhook URL for display
    webhook_url = IntegrationService.decrypt_value(integration.slack_webhook_url) if integration.slack_webhook_url else None
    
    return SlackConfigResponse(
        slack_webhook_url=webhook_url,
        mock_slack=integration.mock_slack
    )

@router.post("/slack", response_model=SlackConfigResponse)
async def save_slack_config(
    slack_config: SlackConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Save Slack configuration (admin only)"""
    try:
        integration = IntegrationService.save_slack_config(db, current_user.id, slack_config)
        
        # Decrypt for response
        webhook_url = IntegrationService.decrypt_value(integration.slack_webhook_url) if integration.slack_webhook_url else None
        
        return SlackConfigResponse(
            slack_webhook_url=webhook_url,
            mock_slack=integration.mock_slack
        )
    except Exception as e:
        logger.error(f"Error saving Slack config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save Slack configuration"
        )

@router.post("/slack/test")
async def test_slack_config(
    test_request: TestSlackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Test Slack webhook by sending a test message"""
    try:
        # Get Slack config from database
        webhook_url, mock_mode = IntegrationService.get_slack_config(db)
        
        if not webhook_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Slack webhook URL is not configured. Please configure it first."
            )
        
        # Temporarily override environment variable
        import os
        original_mock = os.getenv('MOCK_SLACK')
        try:
            os.environ['MOCK_SLACK'] = 'true' if mock_mode else 'false'
            
            # Send test message
            success = SlackService.send_test_message(webhook_url)
            
            if success:
                return {
                    "success": True,
                    "message": "Test message sent successfully to Slack" + (" (Mock mode - check logs)" if mock_mode else ""),
                    "mock_mode": mock_mode
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to send test message. Check your webhook URL."
                )
        finally:
            # Restore original value
            if original_mock is not None:
                os.environ['MOCK_SLACK'] = original_mock
            elif 'MOCK_SLACK' in os.environ:
                del os.environ['MOCK_SLACK']
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing Slack: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Slack test failed: {str(e)}"
        )
