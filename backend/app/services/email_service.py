"""
Email service with mock support and easy SMTP configuration

To configure real SMTP, update the settings in this file and set MOCK_EMAIL=False
"""

import os
import logging
from typing import List, Optional
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

logger = logging.getLogger(__name__)

# Email Configuration - UPDATE THESE FOR REAL EMAILS
MOCK_EMAIL = os.getenv("MOCK_EMAIL", "true").lower() == "true"
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "your-email@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your-app-password")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@nexbii.com")
FROM_NAME = os.getenv("FROM_NAME", "NexBII Analytics")

class EmailService:
    """Email service with mock mode for development"""
    
    @staticmethod
    def send_email(
        to_emails: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send email to recipients
        
        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            html_content: HTML email body
            text_content: Plain text email body (optional)
        
        Returns:
            bool: True if successful, False otherwise
        """
        if MOCK_EMAIL:
            # Mock mode - just log the email
            logger.info(f"📧 [MOCK EMAIL] To: {', '.join(to_emails)}")
            logger.info(f"📧 [MOCK EMAIL] Subject: {subject}")
            logger.info(f"📧 [MOCK EMAIL] Content: {text_content or html_content[:100]}...")
            return True
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{FROM_NAME} <{FROM_EMAIL}>"
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            
            # Add text and HTML parts
            if text_content:
                part1 = MIMEText(text_content, 'plain')
                msg.attach(part1)
            
            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"✅ Email sent successfully to {', '.join(to_emails)}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email: {str(e)}")
            return False
    
    @staticmethod
    def send_subscription_email(
        to_email: str,
        dashboard_name: str,
        dashboard_url: str,
        dashboard_data: dict,
        frequency: str
    ) -> bool:
        """Send scheduled dashboard subscription email"""
        
        subject = f"Your {frequency.title()} Dashboard Report: {dashboard_name}"
        
        html_content = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                             color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; }}
                    .dashboard-link {{ display: inline-block; background: #667eea; color: white; 
                                     padding: 12px 24px; text-decoration: none; border-radius: 6px; 
                                     margin: 20px 0; }}
                    .footer {{ background: #f4f4f4; padding: 15px; text-align: center; 
                             font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>📊 {dashboard_name}</h1>
                    <p>{frequency.title()} Report - {datetime.now().strftime('%B %d, %Y')}</p>
                </div>
                <div class="content">
                    <p>Hello!</p>
                    <p>Here's your {frequency} dashboard report for <strong>{dashboard_name}</strong>.</p>
                    <p>Click the button below to view your interactive dashboard:</p>
                    <center>
                        <a href="{dashboard_url}" class="dashboard-link">View Dashboard</a>
                    </center>
                    <p>This email was sent as part of your {frequency} subscription. 
                       You can manage your subscriptions in your dashboard settings.</p>
                </div>
                <div class="footer">
                    <p>© 2024 NexBII Analytics Platform | Business Intelligence Made Simple</p>
                </div>
            </body>
        </html>
        """
        
        text_content = f"""
        {dashboard_name}
        {frequency.title()} Report - {datetime.now().strftime('%B %d, %Y')}
        
        Hello!
        
        Here's your {frequency} dashboard report for {dashboard_name}.
        
        View your dashboard at: {dashboard_url}
        
        This email was sent as part of your {frequency} subscription.
        """
        
        return EmailService.send_email([to_email], subject, html_content, text_content)
    
    @staticmethod
    def send_alert_notification(
        to_emails: List[str],
        alert_name: str,
        condition_description: str,
        actual_value: float,
        threshold_value: float,
        query_name: str
    ) -> bool:
        """Send alert notification email"""
        
        subject = f"🔔 Alert Triggered: {alert_name}"
        
        html_content = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .header {{ background: #ef4444; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; }}
                    .alert-box {{ background: #fef2f2; border-left: 4px solid #ef4444; 
                                 padding: 15px; margin: 20px 0; }}
                    .metric {{ font-size: 24px; font-weight: bold; color: #ef4444; }}
                    .footer {{ background: #f4f4f4; padding: 15px; text-align: center; 
                             font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🔔 Alert Triggered</h1>
                    <p>{alert_name}</p>
                </div>
                <div class="content">
                    <p>An alert condition has been met for your query <strong>{query_name}</strong>.</p>
                    
                    <div class="alert-box">
                        <p><strong>Condition:</strong> {condition_description}</p>
                        <p><strong>Actual Value:</strong> <span class="metric">{actual_value}</span></p>
                        <p><strong>Threshold:</strong> {threshold_value}</p>
                    </div>
                    
                    <p>Triggered at: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                    
                    <p>Please review your data and take appropriate action if needed.</p>
                </div>
                <div class="footer">
                    <p>© 2024 NexBII Analytics Platform | Intelligent Alerts & Monitoring</p>
                </div>
            </body>
        </html>
        """
        
        text_content = f"""
        🔔 ALERT TRIGGERED: {alert_name}
        
        An alert condition has been met for your query: {query_name}
        
        Condition: {condition_description}
        Actual Value: {actual_value}
        Threshold: {threshold_value}
        
        Triggered at: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
        
        Please review your data and take appropriate action if needed.
        """
        
        return EmailService.send_email(to_emails, subject, html_content, text_content)
    
    @staticmethod
    def send_mention_notification(
        to_email: str,
        mentioned_by: str,
        comment_text: str,
        entity_type: str,
        entity_name: str,
        entity_url: str
    ) -> bool:
        """Send notification when user is mentioned in a comment"""
        
        subject = f"💬 {mentioned_by} mentioned you in a comment"
        
        html_content = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .header {{ background: #3b82f6; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; }}
                    .comment-box {{ background: #eff6ff; border-left: 4px solid #3b82f6; 
                                   padding: 15px; margin: 20px 0; font-style: italic; }}
                    .view-link {{ display: inline-block; background: #3b82f6; color: white; 
                                 padding: 12px 24px; text-decoration: none; border-radius: 6px; 
                                 margin: 20px 0; }}
                    .footer {{ background: #f4f4f4; padding: 15px; text-align: center; 
                             font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>💬 You were mentioned!</h1>
                </div>
                <div class="content">
                    <p><strong>{mentioned_by}</strong> mentioned you in a comment on 
                       {entity_type} <strong>{entity_name}</strong>:</p>
                    
                    <div class="comment-box">
                        "{comment_text}"
                    </div>
                    
                    <center>
                        <a href="{entity_url}" class="view-link">View & Reply</a>
                    </center>
                </div>
                <div class="footer">
                    <p>© 2024 NexBII Analytics Platform | Collaboration Made Easy</p>
                </div>
            </body>
        </html>
        """
        
        text_content = f"""
        💬 YOU WERE MENTIONED!
        
        {mentioned_by} mentioned you in a comment on {entity_type} "{entity_name}":
        
        "{comment_text}"
        
        View and reply at: {entity_url}
        """
        
        return EmailService.send_email([to_email], subject, html_content, text_content)
