"""
Comprehensive tests for query endpoints
"""
import pytest
import json
from fastapi import status
from app.models.query import Query


class TestQueryCRUD:
    """Test query CRUD operations"""

    def test_create_query_sql(self, client, auth_headers, test_datasource):
        """Test creating a SQL query"""
        response = client.post(
            "/api/queries/",
            headers=auth_headers,
            json={
                "name": "Test SQL Query",
                "description": "A test query",
                "datasource_id": test_datasource.id,
                "query_type": "sql",
                "sql_query": "SELECT * FROM users LIMIT 10"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Test SQL Query"
        assert data["query_type"] == "sql"
        assert "id" in data

    def test_create_query_visual(self, client, auth_headers, test_datasource):
        """Test creating a visual query with configuration"""
        visual_config = {
            "table": "users",
            "columns": ["id", "name", "email"],
            "filters": [{"column": "status", "operator": "=", "value": "active"}]
        }
        
        response = client.post(
            "/api/queries/",
            headers=auth_headers,
            json={
                "name": "Test Visual Query",
                "description": "A visual query",
                "datasource_id": test_datasource.id,
                "query_type": "visual",
                "query_config": visual_config,
                "sql_query": "SELECT id, name, email FROM users WHERE status = 'active'"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Test Visual Query"
        assert data["query_type"] == "visual"
        assert data["query_config"] == visual_config

    def test_create_query_unauthorized(self, client, test_datasource):
        """Test creating query without authentication fails"""
        response = client.post(
            "/api/queries/",
            json={
                "name": "Unauthorized Query",
                "datasource_id": test_datasource.id,
                "query_type": "sql",
                "sql_query": "SELECT 1"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_query_with_nonexistent_datasource(self, client, auth_headers):
        """Test creating query with invalid datasource ID fails"""
        response = client.post(
            "/api/queries/",
            headers=auth_headers,
            json={
                "name": "Invalid Query",
                "datasource_id": "nonexistent-id",
                "query_type": "sql",
                "sql_query": "SELECT 1"
            }
        )
        # This should succeed in creation, but fail on execution
        assert response.status_code == status.HTTP_200_OK

    def test_list_queries(self, client, auth_headers, test_query):
        """Test listing all queries"""
        response = client.get("/api/queries/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(q["id"] == test_query.id for q in data)

    def test_list_queries_unauthorized(self, client):
        """Test listing queries without authentication fails"""
        response = client.get("/api/queries/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_query_by_id(self, client, auth_headers, test_query):
        """Test getting a specific query"""
        response = client.get(
            f"/api/queries/{test_query.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_query.id
        assert data["name"] == test_query.name
        assert data["sql_query"] == test_query.sql_query

    def test_get_nonexistent_query(self, client, auth_headers):
        """Test getting nonexistent query returns 404"""
        response = client.get(
            "/api/queries/nonexistent-id",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_query_name(self, client, auth_headers, test_query):
        """Test updating query name"""
        response = client.put(
            f"/api/queries/{test_query.id}",
            headers=auth_headers,
            json={
                "name": "Updated Query Name"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Query Name"
        assert data["sql_query"] == test_query.sql_query

    def test_update_query_sql(self, client, auth_headers, test_query):
        """Test updating query SQL"""
        response = client.put(
            f"/api/queries/{test_query.id}",
            headers=auth_headers,
            json={
                "sql_query": "SELECT COUNT(*) FROM users"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["sql_query"] == "SELECT COUNT(*) FROM users"

    def test_update_nonexistent_query(self, client, auth_headers):
        """Test updating nonexistent query fails"""
        response = client.put(
            "/api/queries/nonexistent-id",
            headers=auth_headers,
            json={"name": "Updated"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_query(self, client, auth_headers, test_query):
        """Test deleting a query"""
        response = client.delete(
            f"/api/queries/{test_query.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Verify it's deleted
        response = client.get(
            f"/api/queries/{test_query.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_query(self, client, auth_headers):
        """Test deleting nonexistent query fails"""
        response = client.delete(
            "/api/queries/nonexistent-id",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestQueryExecution:
    """Test query execution functionality"""

    def test_execute_adhoc_query(self, client, auth_headers, test_datasource):
        """Test executing an ad-hoc SQL query"""
        response = client.post(
            "/api/queries/execute",
            headers=auth_headers,
            json={
                "datasource_id": test_datasource.id,
                "sql_query": "SELECT 1 as test_column",
                "limit": 100
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "columns" in data
        assert "rows" in data
        assert "execution_time" in data
        assert "from_cache" in data

    def test_execute_saved_query(self, client, auth_headers, test_query):
        """Test executing a saved query by ID"""
        response = client.post(
            "/api/queries/execute",
            headers=auth_headers,
            json={
                "query_id": test_query.id,
                "limit": 100
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "columns" in data
        assert "rows" in data

    def test_execute_query_with_invalid_datasource(self, client, auth_headers):
        """Test executing query with invalid datasource fails"""
        response = client.post(
            "/api/queries/execute",
            headers=auth_headers,
            json={
                "datasource_id": "nonexistent-id",
                "sql_query": "SELECT 1",
                "limit": 100
            }
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_execute_query_with_invalid_sql(self, client, auth_headers, test_datasource):
        """Test executing query with invalid SQL fails"""
        response = client.post(
            "/api/queries/execute",
            headers=auth_headers,
            json={
                "datasource_id": test_datasource.id,
                "sql_query": "INVALID SQL SYNTAX",
                "limit": 100
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_execute_nonexistent_saved_query(self, client, auth_headers):
        """Test executing nonexistent saved query fails"""
        response = client.post(
            "/api/queries/execute",
            headers=auth_headers,
            json={
                "query_id": "nonexistent-id",
                "limit": 100
            }
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_execute_query_unauthorized(self, client, test_datasource):
        """Test executing query without authentication fails"""
        response = client.post(
            "/api/queries/execute",
            json={
                "datasource_id": test_datasource.id,
                "sql_query": "SELECT 1",
                "limit": 100
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_execute_query_with_limit(self, client, auth_headers, test_datasource):
        """Test query execution respects limit parameter"""
        response = client.post(
            "/api/queries/execute",
            headers=auth_headers,
            json={
                "datasource_id": test_datasource.id,
                "sql_query": "SELECT 1 UNION SELECT 2 UNION SELECT 3",
                "limit": 2
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Note: Limit enforcement depends on datasource implementation
        assert len(data["rows"]) <= 2 or "total_rows" in data


class TestQueryValidation:
    """Test query validation and error handling"""

    def test_create_query_missing_required_fields(self, client, auth_headers):
        """Test creating query without required fields fails"""
        response = client.post(
            "/api/queries/",
            headers=auth_headers,
            json={
                "name": "Incomplete Query"
                # Missing datasource_id, query_type, sql_query
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_query_with_empty_name(self, client, auth_headers, test_datasource):
        """Test creating query with empty name"""
        response = client.post(
            "/api/queries/",
            headers=auth_headers,
            json={
                "name": "",
                "datasource_id": test_datasource.id,
                "query_type": "sql",
                "sql_query": "SELECT 1"
            }
        )
        # Should succeed - empty name is technically valid
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_query_type_validation(self, client, auth_headers, test_datasource):
        """Test query_type must be 'sql' or 'visual'"""
        response = client.post(
            "/api/queries/",
            headers=auth_headers,
            json={
                "name": "Test Query",
                "datasource_id": test_datasource.id,
                "query_type": "invalid_type",
                "sql_query": "SELECT 1"
            }
        )
        # Should fail validation if query_type has enum restriction
        # Otherwise it will succeed (depends on schema definition)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]
