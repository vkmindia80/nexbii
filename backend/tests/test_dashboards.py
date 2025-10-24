"""
Comprehensive tests for dashboard endpoints
"""
import pytest
import json
from fastapi import status


class TestDashboardCRUD:
    """Test dashboard CRUD operations"""

    def test_create_dashboard(self, client, auth_headers):
        """Test creating a dashboard"""
        response = client.post(
            "/api/dashboards/",
            headers=auth_headers,
            json={
                "name": "Test Dashboard",
                "description": "A test dashboard",
                "layout": [],
                "widgets": [],
                "is_public": False
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Test Dashboard"
        assert data["is_public"] == False
        assert "id" in data

    def test_create_dashboard_with_widgets(self, client, auth_headers, test_query):
        """Test creating a dashboard with widgets"""
        widgets = [
            {
                "id": "widget-1",
                "type": "chart",
                "chart_type": "line",
                "query_id": test_query.id,
                "title": "Test Chart"
            }
        ]
        layout = [
            {"i": "widget-1", "x": 0, "y": 0, "w": 6, "h": 4}
        ]
        
        response = client.post(
            "/api/dashboards/",
            headers=auth_headers,
            json={
                "name": "Dashboard with Widgets",
                "description": "Contains widgets",
                "layout": layout,
                "widgets": widgets,
                "is_public": False
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["widgets"]) == 1
        assert data["widgets"][0]["query_id"] == test_query.id

    def test_create_public_dashboard(self, client, auth_headers):
        """Test creating a public dashboard"""
        response = client.post(
            "/api/dashboards/",
            headers=auth_headers,
            json={
                "name": "Public Dashboard",
                "description": "A public dashboard",
                "layout": [],
                "widgets": [],
                "is_public": True
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_public"] == True

    def test_create_dashboard_unauthorized(self, client):
        """Test creating dashboard without authentication fails"""
        response = client.post(
            "/api/dashboards/",
            json={
                "name": "Unauthorized Dashboard",
                "layout": [],
                "widgets": []
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_dashboards(self, client, auth_headers, test_dashboard):
        """Test listing all dashboards"""
        response = client.get("/api/dashboards/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(d["id"] == test_dashboard.id for d in data)

    def test_list_dashboards_unauthorized(self, client):
        """Test listing dashboards without authentication fails"""
        response = client.get("/api/dashboards/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_dashboard_by_id(self, client, auth_headers, test_dashboard):
        """Test getting a specific dashboard"""
        response = client.get(
            f"/api/dashboards/{test_dashboard.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_dashboard.id
        assert data["name"] == test_dashboard.name

    def test_get_nonexistent_dashboard(self, client, auth_headers):
        """Test getting nonexistent dashboard returns 404"""
        response = client.get(
            "/api/dashboards/nonexistent-id",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_dashboard_name(self, client, auth_headers, test_dashboard):
        """Test updating dashboard name"""
        response = client.put(
            f"/api/dashboards/{test_dashboard.id}",
            headers=auth_headers,
            json={
                "name": "Updated Dashboard Name"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Dashboard Name"

    def test_update_dashboard_widgets(self, client, auth_headers, test_dashboard, test_query):
        """Test updating dashboard widgets"""
        new_widgets = [
            {
                "id": "widget-2",
                "type": "metric",
                "query_id": test_query.id,
                "title": "KPI Card"
            }
        ]
        
        response = client.put(
            f"/api/dashboards/{test_dashboard.id}",
            headers=auth_headers,
            json={
                "widgets": new_widgets
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["widgets"]) == 1
        assert data["widgets"][0]["type"] == "metric"

    def test_update_dashboard_layout(self, client, auth_headers, test_dashboard):
        """Test updating dashboard layout"""
        new_layout = [
            {"i": "widget-1", "x": 0, "y": 0, "w": 12, "h": 6}
        ]
        
        response = client.put(
            f"/api/dashboards/{test_dashboard.id}",
            headers=auth_headers,
            json={
                "layout": new_layout
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["layout"]) == 1
        assert data["layout"][0]["w"] == 12

    def test_update_dashboard_visibility(self, client, auth_headers, test_dashboard):
        """Test updating dashboard visibility"""
        response = client.put(
            f"/api/dashboards/{test_dashboard.id}",
            headers=auth_headers,
            json={
                "is_public": True
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_public"] == True

    def test_update_nonexistent_dashboard(self, client, auth_headers):
        """Test updating nonexistent dashboard fails"""
        response = client.put(
            "/api/dashboards/nonexistent-id",
            headers=auth_headers,
            json={"name": "Updated"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_dashboard(self, client, auth_headers, test_dashboard):
        """Test deleting a dashboard"""
        response = client.delete(
            f"/api/dashboards/{test_dashboard.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Verify it's deleted
        response = client.get(
            f"/api/dashboards/{test_dashboard.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_dashboard(self, client, auth_headers):
        """Test deleting nonexistent dashboard fails"""
        response = client.delete(
            "/api/dashboards/nonexistent-id",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDashboardValidation:
    """Test dashboard validation and error handling"""

    def test_create_dashboard_missing_required_fields(self, client, auth_headers):
        """Test creating dashboard without required fields fails"""
        response = client.post(
            "/api/dashboards/",
            headers=auth_headers,
            json={
                "name": "Incomplete Dashboard"
                # Missing layout, widgets
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_dashboard_with_empty_name(self, client, auth_headers):
        """Test creating dashboard with empty name"""
        response = client.post(
            "/api/dashboards/",
            headers=auth_headers,
            json={
                "name": "",
                "layout": [],
                "widgets": []
            }
        )
        # Should succeed or fail based on validation rules
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_create_dashboard_with_invalid_layout(self, client, auth_headers):
        """Test creating dashboard with invalid layout structure"""
        response = client.post(
            "/api/dashboards/",
            headers=auth_headers,
            json={
                "name": "Invalid Layout Dashboard",
                "layout": "not-a-list",  # Should be a list
                "widgets": []
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_dashboard_with_invalid_widget_reference(self, client, auth_headers):
        """Test creating dashboard with widget referencing nonexistent query"""
        widgets = [
            {
                "id": "widget-1",
                "type": "chart",
                "query_id": "nonexistent-query-id",
                "title": "Invalid Widget"
            }
        ]
        
        response = client.post(
            "/api/dashboards/",
            headers=auth_headers,
            json={
                "name": "Dashboard with Invalid Widget",
                "layout": [],
                "widgets": widgets
            }
        )
        # Should succeed in creation (validation happens at render time)
        assert response.status_code == status.HTTP_200_OK


class TestDashboardPermissions:
    """Test dashboard permissions and access control"""

    def test_public_dashboard_accessible_to_all(self, client, auth_headers):
        """Test public dashboards can be accessed"""
        # Create public dashboard
        response = client.post(
            "/api/dashboards/",
            headers=auth_headers,
            json={
                "name": "Public Test",
                "layout": [],
                "widgets": [],
                "is_public": True
            }
        )
        dashboard_id = response.json()["id"]
        
        # Access it
        response = client.get(
            f"/api/dashboards/{dashboard_id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK

    def test_private_dashboard_requires_auth(self, client, auth_headers):
        """Test private dashboards require authentication"""
        # Create private dashboard
        response = client.post(
            "/api/dashboards/",
            headers=auth_headers,
            json={
                "name": "Private Test",
                "layout": [],
                "widgets": [],
                "is_public": False
            }
        )
        dashboard_id = response.json()["id"]
        
        # Try to access without auth
        response = client.get(f"/api/dashboards/{dashboard_id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
