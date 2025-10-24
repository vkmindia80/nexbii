"""
Tests for data source endpoints
"""
import pytest
import json
from fastapi import status


class TestDataSources:
    """Test data source endpoints"""

    def test_create_datasource(self, client, auth_headers):
        """Test creating a data source"""
        response = client.post(
            "/api/datasources/",
            headers=auth_headers,
            json={
                "name": "Test DB",
                "type": "sqlite",
                "config": {"database": ":memory:"}
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Test DB"
        assert data["type"] == "sqlite"
        assert "id" in data

    def test_create_datasource_unauthorized(self, client):
        """Test creating data source without auth fails"""
        response = client.post(
            "/api/datasources/",
            json={
                "name": "Test DB",
                "type": "sqlite",
                "config": {"database": ":memory:"}
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_datasources(self, client, auth_headers, test_datasource):
        """Test listing data sources"""
        response = client.get("/api/datasources/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(ds["id"] == test_datasource.id for ds in data)

    def test_get_datasource(self, client, auth_headers, test_datasource):
        """Test getting a specific data source"""
        response = client.get(
            f"/api/datasources/{test_datasource.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_datasource.id
        assert data["name"] == test_datasource.name

    def test_get_nonexistent_datasource(self, client, auth_headers):
        """Test getting nonexistent data source returns 404"""
        response = client.get(
            "/api/datasources/nonexistent-id",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_datasource(self, client, auth_headers, test_datasource):
        """Test deleting a data source"""
        response = client.delete(
            f"/api/datasources/{test_datasource.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Verify it's deleted
        response = client.get(
            f"/api/datasources/{test_datasource.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_test_connection_sqlite(self, client, auth_headers):
        """Test SQLite connection testing"""
        response = client.post(
            "/api/datasources/test",
            headers=auth_headers,
            json={
                "type": "sqlite",
                "config": {"database": ":memory:"}
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "message" in data
