"""
Slack notification service for alerts and notifications

Sends formatted messages to Slack channels via webhooks
"""

import os
import logging
import requests
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Slack Configuration
MOCK_SLACK = os.getenv("MOCK_SLACK", "true").lower() == "true"

class SlackService:
    """Slack notification service with webhook support"""
    
    @staticmethod
    def send_webhook_message(
        webhook_url: str,
        message: Dict[str, Any]
    ) -> bool:
        """
        Send a message to Slack via webhook
        
        Args:
            webhook_url: Slack webhook URL
            message: Slack message payload (blocks and/or text)
        
        Returns:
            bool: True if successful, False otherwise
        """
        if MOCK_SLACK:
            # Mock mode - just log the message
            logger.info(f"💬 [MOCK SLACK] Webhook: {webhook_url[:30]}...")
            logger.info(f"💬 [MOCK SLACK] Message: {message.get('text', 'No text')}")
            return True
        
        try:
            response = requests.post(
                webhook_url,
                json=message,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Slack message sent successfully")
                return True
            else:
                logger.error(f"❌ Slack webhook failed: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error(f"❌ Slack webhook timeout")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to send Slack message: {str(e)}")
            return False
    
    @staticmethod
    def send_alert_notification(
        webhook_url: str,
        alert_name: str,
        condition_description: str,
        actual_value: float,
        threshold_value: float,
        query_name: str,
        alert_url: Optional[str] = None
    ) -> bool:
        """
        Send alert notification to Slack with rich formatting
        
        Args:
            webhook_url: Slack webhook URL
            alert_name: Name of the alert
            condition_description: Human-readable condition
            actual_value: Actual metric value
            threshold_value: Threshold that was exceeded
            query_name: Name of the query
            alert_url: Optional URL to view the alert
        
        Returns:
            bool: True if successful
        """
        
        # Build rich Slack message with blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🔔 Alert Triggered: {alert_name}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Query:*\n{query_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Triggered At:*\n{datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
                    }
                ]
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Condition:*\n{condition_description}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Threshold:*\n`{threshold_value}`"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Actual Value:*\n:warning: `{actual_value}`"
                }
            }
        ]
        
        # Add button if URL provided
        if alert_url:
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View Alert",
                            "emoji": True
                        },
                        "url": alert_url,
                        "style": "primary"
                    }
                ]
            })
        
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "📊 _NexBII Analytics Platform - Intelligent Alerts & Monitoring_"
                }
            ]
        })
        
        message = {
            "text": f"Alert Triggered: {alert_name}",  # Fallback text
            "blocks": blocks
        }
        
        return SlackService.send_webhook_message(webhook_url, message)
    
    @staticmethod
    def send_subscription_notification(
        webhook_url: str,
        dashboard_name: str,
        dashboard_url: str,
        frequency: str,
        recipient: str
    ) -> bool:
        """
        Send subscription notification to Slack
        
        Args:
            webhook_url: Slack webhook URL
            dashboard_name: Name of the dashboard
            dashboard_url: URL to view dashboard
            frequency: Subscription frequency
            recipient: Email of recipient
        
        Returns:
            bool: True if successful
        """
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📊 Dashboard Report: {dashboard_name}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Your {frequency} dashboard report is ready!"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Recipient:*\n{recipient}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Frequency:*\n{frequency.title()}"
                    }
                ]
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View Dashboard",
                            "emoji": True
                        },
                        "url": dashboard_url,
                        "style": "primary"
                    }
                ]
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"📅 _{datetime.now().strftime('%B %d, %Y')}_ | 📊 _NexBII Analytics Platform_"
                    }
                ]
            }
        ]
        
        message = {
            "text": f"Dashboard Report: {dashboard_name}",
            "blocks": blocks
        }
        
        return SlackService.send_webhook_message(webhook_url, message)
    
    @staticmethod
    def send_test_message(webhook_url: str) -> bool:
        """
        Send a test message to verify webhook configuration
        
        Args:
            webhook_url: Slack webhook URL to test
        
        Returns:
            bool: True if successful
        """
        message = {
            "text": "✅ Slack webhook test successful!",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "✅ *Slack Webhook Test Successful!*\n\nYour NexBII alert notifications are properly configured."
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"🕐 Test sent at {datetime.now().strftime('%I:%M %p on %B %d, %Y')}"
                        }
                    ]
                }
            ]
        }
        
        return SlackService.send_webhook_message(webhook_url, message)
    
    @staticmethod
    def validate_webhook_url(webhook_url: str) -> bool:
        """
        Validate if a webhook URL looks like a valid Slack webhook
        
        Args:
            webhook_url: Webhook URL to validate
        
        Returns:
            bool: True if URL format is valid
        """
        if not webhook_url:
            return False
        
        # Basic validation - Slack webhooks typically start with hooks.slack.com
        return (
            webhook_url.startswith('https://hooks.slack.com/') or
            webhook_url.startswith('http://') or
            webhook_url.startswith('https://')
        )
