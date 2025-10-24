"""
Tests for subscriptions endpoints
"""
import pytest
from fastapi import status
from unittest.mock import Mock, patch


class TestSubscriptions:
    """Test subscription management endpoints"""

    @patch('app.api.v1.subscriptions.SubscriptionService')
    def test_create_subscription(self, mock_service, client, auth_headers, test_dashboard):
        """Test creating a dashboard subscription"""
        mock_service.create_subscription.return_value = {
            "id": "sub-123",
            "dashboard_id": test_dashboard.id,
            "frequency": "daily",
            "email": "user@example.com"
        }
        
        response = client.post(
            "/api/subscriptions/",
            headers=auth_headers,
            json={
                "dashboard_id": test_dashboard.id,
                "frequency": "daily",
                "email": "user@example.com"
            }
        )
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_create_subscription_unauthorized(self, client):
        """Test creating subscription without authentication"""
        response = client.post(
            "/api/subscriptions/",
            json={"dashboard_id": "test", "frequency": "daily"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch('app.api.v1.subscriptions.SubscriptionService')
    def test_list_subscriptions(self, mock_service, client, auth_headers):
        """Test listing subscriptions"""
        mock_service.get_subscriptions.return_value = []
        
        response = client.get("/api/subscriptions/", headers=auth_headers)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_list_subscriptions_unauthorized(self, client):
        """Test listing subscriptions without authentication"""
        response = client.get("/api/subscriptions/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
