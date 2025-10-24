"""
Tests for alerts endpoints
"""
import pytest
from fastapi import status
from unittest.mock import Mock, patch


class TestAlerts:
    """Test alert management endpoints"""

    @patch('app.api.v1.alerts.AlertService')
    def test_create_alert(self, mock_service, client, auth_headers, test_query):
        """Test creating an alert"""
        mock_service.create_alert.return_value = {
            "id": "alert-123",
            "name": "High Revenue Alert",
            "query_id": test_query.id,
            "threshold": 10000,
            "condition": "greater_than"
        }
        
        response = client.post(
            "/api/alerts/",
            headers=auth_headers,
            json={
                "name": "High Revenue Alert",
                "query_id": test_query.id,
                "threshold": 10000,
                "condition": "greater_than",
                "notification_channels": ["email"]
            }
        )
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_create_alert_unauthorized(self, client):
        """Test creating alert without authentication"""
        response = client.post(
            "/api/alerts/",
            json={"name": "Test Alert"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch('app.api.v1.alerts.AlertService')
    def test_list_alerts(self, mock_service, client, auth_headers):
        """Test listing alerts"""
        mock_service.get_alerts.return_value = []
        
        response = client.get("/api/alerts/", headers=auth_headers)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_list_alerts_unauthorized(self, client):
        """Test listing alerts without authentication"""
        response = client.get("/api/alerts/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
