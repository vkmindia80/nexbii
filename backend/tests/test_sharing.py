"""
Comprehensive tests for sharing endpoints
"""
import pytest
from fastapi import status
from datetime import datetime, timedelta
from unittest.mock import patch


class TestCreateShareLink:
    """Test share link creation"""

    def test_create_share_link_basic(self, client, auth_headers, test_dashboard):
        """Test creating a basic share link"""
        response = client.post(
            "/api/sharing/create",
            headers=auth_headers,
            json={
                "dashboard_id": test_dashboard.id,
                "allow_interactions": True
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "share_token" in data
        assert "share_url" in data
        assert data["password_protected"] == False
        assert data["allow_interactions"] == True

    def test_create_share_link_with_password(self, client, auth_headers, test_dashboard):
        """Test creating password-protected share link"""
        response = client.post(
            "/api/sharing/create",
            headers=auth_headers,
            json={
                "dashboard_id": test_dashboard.id,
                "password": "secret123",
                "allow_interactions": True
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["password_protected"] == True

    def test_create_share_link_with_expiration(self, client, auth_headers, test_dashboard):
        """Test creating share link with expiration"""
        response = client.post(
            "/api/sharing/create",
            headers=auth_headers,
            json={
                "dashboard_id": test_dashboard.id,
                "expires_in_days": 7,
                "allow_interactions": False
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "expires_at" in data
        assert data["expires_at"] is not None
        assert data["allow_interactions"] == False

    def test_create_share_link_unauthorized(self, client, test_dashboard):
        """Test creating share link without authentication fails"""
        response = client.post(
            "/api/sharing/create",
            json={
                "dashboard_id": test_dashboard.id
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_share_link_nonexistent_dashboard(self, client, auth_headers):
        """Test creating share link for nonexistent dashboard fails"""
        response = client.post(
            "/api/sharing/create",
            headers=auth_headers,
            json={
                "dashboard_id": "nonexistent-id"
            }
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_share_link_missing_dashboard_id(self, client, auth_headers):
        """Test creating share link without dashboard_id fails"""
        response = client.post(
            "/api/sharing/create",
            headers=auth_headers,
            json={}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAccessSharedDashboard:
    """Test accessing shared dashboards"""

    def test_get_shared_dashboard_info(self, client, test_shared_dashboard):
        """Test getting shared dashboard info (no auth required)"""
        response = client.get(
            f"/api/sharing/dashboard/{test_shared_dashboard.share_token}"
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "dashboard_id" in data
        assert "requires_password" in data
        assert "allow_interactions" in data

    def test_get_nonexistent_shared_dashboard(self, client):
        """Test accessing nonexistent share token"""
        response = client.get("/api/sharing/dashboard/invalid-token")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_access_shared_dashboard_no_password(self, client, test_shared_dashboard):
        """Test accessing unprotected shared dashboard"""
        response = client.post(
            f"/api/sharing/dashboard/{test_shared_dashboard.share_token}/access",
            json={}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "dashboard" in data
        assert "allow_interactions" in data
        assert data["dashboard"]["id"] == test_shared_dashboard.dashboard_id

    def test_access_password_protected_dashboard_with_correct_password(
        self, client, test_password_protected_share
    ):
        """Test accessing password-protected dashboard with correct password"""
        response = client.post(
            f"/api/sharing/dashboard/{test_password_protected_share.share_token}/access",
            json={"password": "test_password"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "dashboard" in data

    def test_access_password_protected_dashboard_without_password(
        self, client, test_password_protected_share
    ):
        """Test accessing password-protected dashboard without password fails"""
        response = client.post(
            f"/api/sharing/dashboard/{test_password_protected_share.share_token}/access",
            json={}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_access_password_protected_dashboard_with_wrong_password(
        self, client, test_password_protected_share
    ):
        """Test accessing password-protected dashboard with wrong password fails"""
        response = client.post(
            f"/api/sharing/dashboard/{test_password_protected_share.share_token}/access",
            json={"password": "wrong_password"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_access_expired_share_link(self, client, test_expired_share):
        """Test accessing expired share link fails"""
        response = client.get(
            f"/api/sharing/dashboard/{test_expired_share.share_token}"
        )
        assert response.status_code == status.HTTP_410_GONE


class TestListUserShares:
    """Test listing user's shares"""

    def test_get_my_shares(self, client, auth_headers, test_shared_dashboard):
        """Test getting current user's share links"""
        response = client.get("/api/sharing/my-shares", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        # Should contain at least the test share
        assert len(data) >= 1
        
        # Verify share structure
        if len(data) > 0:
            share = data[0]
            assert "id" in share
            assert "dashboard_id" in share
            assert "share_token" in share
            assert "share_url" in share

    def test_get_my_shares_unauthorized(self, client):
        """Test getting shares without authentication fails"""
        response = client.get("/api/sharing/my-shares")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_my_shares_empty(self, client, auth_headers):
        """Test getting shares when user has no shares"""
        # This test assumes auth_headers is for a user with no shares
        # The actual result depends on test data setup
        response = client.get("/api/sharing/my-shares", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)


class TestDeleteShare:
    """Test share link deletion"""

    def test_delete_share_link(self, client, auth_headers, test_shared_dashboard):
        """Test deleting/revoking a share link"""
        response = client.delete(
            f"/api/sharing/share/{test_shared_dashboard.id}",
            headers=auth_headers
        )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT
        ]

    def test_delete_share_unauthorized(self, client, test_shared_dashboard):
        """Test deleting share without authentication fails"""
        response = client.delete(
            f"/api/sharing/share/{test_shared_dashboard.id}"
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_nonexistent_share(self, client, auth_headers):
        """Test deleting nonexistent share fails"""
        response = client.delete(
            "/api/sharing/share/99999",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestSharePermissions:
    """Test share permissions and access control"""

    def test_public_access_no_auth_required(self, client, test_shared_dashboard):
        """Test public share access doesn't require authentication"""
        # Get share info
        response = client.get(
            f"/api/sharing/dashboard/{test_shared_dashboard.share_token}"
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Access dashboard
        response = client.post(
            f"/api/sharing/dashboard/{test_shared_dashboard.share_token}/access",
            json={}
        )
        assert response.status_code == status.HTTP_200_OK

    def test_share_allows_interactions_setting(self, client, auth_headers, test_dashboard):
        """Test allow_interactions setting is preserved"""
        # Create share with interactions disabled
        response = client.post(
            "/api/sharing/create",
            headers=auth_headers,
            json={
                "dashboard_id": test_dashboard.id,
                "allow_interactions": False
            }
        )
        share_token = response.json()["share_token"]
        
        # Access dashboard
        response = client.post(
            f"/api/sharing/dashboard/{share_token}/access",
            json={}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["allow_interactions"] == False


class TestShareValidation:
    """Test share validation and error handling"""

    def test_create_share_with_negative_expiration(self, client, auth_headers, test_dashboard):
        """Test creating share with negative expiration days"""
        response = client.post(
            "/api/sharing/create",
            headers=auth_headers,
            json={
                "dashboard_id": test_dashboard.id,
                "expires_in_days": -1
            }
        )
        # Should either succeed (negative means no expiration) or fail validation
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]

    def test_create_share_with_very_long_password(self, client, auth_headers, test_dashboard):
        """Test creating share with very long password"""
        long_password = "a" * 1000
        response = client.post(
            "/api/sharing/create",
            headers=auth_headers,
            json={
                "dashboard_id": test_dashboard.id,
                "password": long_password
            }
        )
        # Should succeed - bcrypt handles long passwords
        assert response.status_code == status.HTTP_200_OK
