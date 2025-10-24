"""
Tests for comments endpoints
"""
import pytest
from fastapi import status
from unittest.mock import Mock, patch


class TestComments:
    """Test comment CRUD operations"""

    @patch('app.api.v1.comments.CommentService')
    def test_create_comment(self, mock_service, client, auth_headers, test_dashboard):
        """Test creating a comment"""
        mock_service.create_comment.return_value = {
            "id": "comment-123",
            "content": "Great dashboard!",
            "dashboard_id": test_dashboard.id,
            "user_id": "user-123",
            "created_at": "2024-01-01T00:00:00"
        }
        
        response = client.post(
            "/api/comments/",
            headers=auth_headers,
            json={
                "content": "Great dashboard!",
                "dashboard_id": test_dashboard.id
            }
        )
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]

    def test_create_comment_unauthorized(self, client, test_dashboard):
        """Test creating comment without authentication"""
        response = client.post(
            "/api/comments/",
            json={
                "content": "Test comment",
                "dashboard_id": test_dashboard.id
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch('app.api.v1.comments.CommentService')
    def test_get_comments(self, mock_service, client, auth_headers, test_dashboard):
        """Test getting comments"""
        mock_service.get_comments.return_value = [
            {"id": "1", "content": "Comment 1"},
            {"id": "2", "content": "Comment 2"}
        ]
        
        response = client.get(
            f"/api/comments/?dashboard_id={test_dashboard.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK

    def test_get_comments_unauthorized(self, client):
        """Test getting comments without authentication"""
        response = client.get("/api/comments/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
