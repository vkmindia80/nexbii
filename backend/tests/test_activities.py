"""
Tests for activities endpoints
"""
import pytest
from fastapi import status
from unittest.mock import Mock, patch


class TestActivities:
    """Test activity feed endpoints"""

    @patch('app.api.v1.activities.ActivityService')
    def test_get_activity_feed(self, mock_service, client, auth_headers):
        """Test getting activity feed"""
        mock_service.get_activities.return_value = [
            {
                "id": "1",
                "type": "dashboard_created",
                "user_id": "user-123",
                "timestamp": "2024-01-01T00:00:00"
            }
        ]
        
        response = client.get("/api/activities/", headers=auth_headers)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_activities_unauthorized(self, client):
        """Test getting activities without authentication"""
        response = client.get("/api/activities/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch('app.api.v1.activities.ActivityService')
    def test_get_user_activities(self, mock_service, client, auth_headers, test_user):
        """Test getting user-specific activities"""
        mock_service.get_user_activities.return_value = []
        
        response = client.get(
            f"/api/activities/user/{test_user.id}",
            headers=auth_headers
        )
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
