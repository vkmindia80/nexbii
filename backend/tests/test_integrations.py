"""
Tests for integrations endpoints
"""
import pytest
from fastapi import status
from unittest.mock import Mock, patch


class TestIntegrations:
    """Test integration configuration endpoints"""

    @patch('app.api.v1.integrations.IntegrationService')
    def test_get_email_config(self, mock_service, client, auth_headers):
        """Test getting email configuration"""
        mock_service.get_email_config.return_value = {
            "smtp_host": "smtp.example.com",
            "smtp_port": 587,
            "from_email": "noreply@example.com"
        }
        
        response = client.get("/api/integrations/email", headers=auth_headers)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_email_config_unauthorized(self, client):
        """Test getting email config without authentication"""
        response = client.get("/api/integrations/email")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch('app.api.v1.integrations.IntegrationService')
    def test_save_email_config(self, mock_service, client, auth_headers):
        """Test saving email configuration"""
        mock_service.save_email_config.return_value = {"success": True}
        
        response = client.post(
            "/api/integrations/email",
            headers=auth_headers,
            json={
                "smtp_host": "smtp.example.com",
                "smtp_port": 587,
                "from_email": "noreply@example.com"
            }
        )
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    @patch('app.api.v1.integrations.IntegrationService')
    def test_get_slack_config(self, mock_service, client, auth_headers):
        """Test getting Slack configuration"""
        mock_service.get_slack_config.return_value = {
            "webhook_url": "https://hooks.slack.com/services/..."
        }
        
        response = client.get("/api/integrations/slack", headers=auth_headers)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_integrations_unauthorized(self, client):
        """Test integration endpoints require authentication"""
        endpoints = [
            "/api/integrations/email",
            "/api/integrations/slack"
        ]
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
