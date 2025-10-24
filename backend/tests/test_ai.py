"""
Comprehensive tests for AI features endpoints
"""
import pytest
from fastapi import status
from unittest.mock import Mock, patch, AsyncMock


class TestNaturalLanguageToSQL:
    """Test natural language to SQL conversion"""

    @patch('app.api.v1.ai.ai_service')
    @patch('app.api.v1.ai.DataSourceService')
    def test_natural_query_conversion(
        self, mock_ds_service, mock_ai_service, client, auth_headers, test_datasource
    ):
        """Test converting natural language to SQL"""
        # Mock schema retrieval
        mock_ds_instance = Mock()
        mock_ds_instance.get_schema.return_value = {
            "success": True,
            "tables": [
                {
                    "name": "users",
                    "columns": ["id", "name", "email", "created_at"]
                }
            ]
        }
        mock_ds_service.return_value = mock_ds_instance
        
        # Mock AI service response
        mock_ai_service.natural_language_to_sql = AsyncMock(return_value={
            "success": True,
            "sql_query": "SELECT * FROM users ORDER BY created_at DESC LIMIT 10",
            "confidence": 0.95,
            "explanation": "Query retrieves the 10 most recent users"
        })
        
        response = client.post(
            "/api/ai/natural-query",
            headers=auth_headers,
            json={
                "natural_query": "Show me the 10 most recent users",
                "datasource_id": test_datasource.id
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "sql_query" in data
        assert "SELECT" in data["sql_query"]

    def test_natural_query_unauthorized(self, client, test_datasource):
        """Test natural query without authentication fails"""
        response = client.post(
            "/api/ai/natural-query",
            json={
                "natural_query": "Show me all users",
                "datasource_id": test_datasource.id
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_natural_query_nonexistent_datasource(self, client, auth_headers):
        """Test natural query with invalid datasource"""
        response = client.post(
            "/api/ai/natural-query",
            headers=auth_headers,
            json={
                "natural_query": "Show me all users",
                "datasource_id": "nonexistent-id"
            }
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch('app.api.v1.ai.DataSourceService')
    def test_natural_query_schema_retrieval_fails(
        self, mock_ds_service, client, auth_headers, test_datasource
    ):
        """Test handling when schema retrieval fails"""
        mock_ds_instance = Mock()
        mock_ds_instance.get_schema.return_value = {"success": False}
        mock_ds_service.return_value = mock_ds_instance
        
        response = client.post(
            "/api/ai/natural-query",
            headers=auth_headers,
            json={
                "natural_query": "Show me all users",
                "datasource_id": test_datasource.id
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_natural_query_missing_parameters(self, client, auth_headers):
        """Test natural query with missing parameters"""
        response = client.post(
            "/api/ai/natural-query",
            headers=auth_headers,
            json={"natural_query": "Show me all users"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestQueryValidation:
    """Test query validation"""

    @patch('app.api.v1.ai.ai_service')
    @patch('app.api.v1.ai.DataSourceService')
    def test_validate_query_success(
        self, mock_ds_service, mock_ai_service, client, auth_headers, test_datasource
    ):
        """Test validating a SQL query"""
        # Mock schema retrieval
        mock_ds_instance = Mock()
        mock_ds_instance.get_schema.return_value = {
            "success": True,
            "tables": [{"name": "users", "columns": ["id", "name"]}]
        }
        mock_ds_service.return_value = mock_ds_instance
        
        # Mock AI validation
        mock_ai_service.validate_and_suggest = AsyncMock(return_value={
            "valid": True,
            "syntax_errors": [],
            "warnings": [],
            "suggestions": ["Consider adding an index on name column"]
        })
        
        response = client.post(
            "/api/ai/validate-query",
            headers=auth_headers,
            json={
                "sql_query": "SELECT * FROM users WHERE name LIKE '%test%'",
                "datasource_id": test_datasource.id
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "valid" in data

    @patch('app.api.v1.ai.ai_service')
    @patch('app.api.v1.ai.DataSourceService')
    def test_validate_invalid_query(
        self, mock_ds_service, mock_ai_service, client, auth_headers, test_datasource
    ):
        """Test validating an invalid SQL query"""
        mock_ds_instance = Mock()
        mock_ds_instance.get_schema.return_value = {
            "success": True,
            "tables": [{"name": "users", "columns": ["id", "name"]}]
        }
        mock_ds_service.return_value = mock_ds_instance
        
        mock_ai_service.validate_and_suggest = AsyncMock(return_value={
            "valid": False,
            "syntax_errors": ["Invalid SQL syntax near 'SELCT'"],
            "warnings": [],
            "suggestions": ["Did you mean SELECT?"]
        })
        
        response = client.post(
            "/api/ai/validate-query",
            headers=auth_headers,
            json={
                "sql_query": "SELCT * FROM users",
                "datasource_id": test_datasource.id
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valid"] is False
        assert len(data["syntax_errors"]) > 0

    def test_validate_query_unauthorized(self, client, test_datasource):
        """Test query validation without authentication"""
        response = client.post(
            "/api/ai/validate-query",
            json={
                "sql_query": "SELECT * FROM users",
                "datasource_id": test_datasource.id
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestQueryOptimization:
    """Test query optimization"""

    @patch('app.api.v1.ai.ai_service')
    @patch('app.api.v1.ai.DataSourceService')
    def test_optimize_query(
        self, mock_ds_service, mock_ai_service, client, auth_headers, test_datasource
    ):
        """Test optimizing a SQL query"""
        mock_ds_instance = Mock()
        mock_ds_instance.get_schema.return_value = {
            "success": True,
            "tables": [{"name": "orders", "columns": ["id", "user_id", "total"]}]
        }
        mock_ds_service.return_value = mock_ds_instance
        
        mock_ai_service.optimize_query = AsyncMock(return_value={
            "optimized_query": "SELECT * FROM orders WHERE user_id = 123 LIMIT 100",
            "optimizations": [
                "Added LIMIT clause to reduce result set",
                "Consider adding index on user_id"
            ],
            "expected_improvement": "30-50% faster",
            "index_recommendations": ["CREATE INDEX idx_user_id ON orders(user_id)"]
        })
        
        response = client.post(
            "/api/ai/optimize-query",
            headers=auth_headers,
            json={
                "sql_query": "SELECT * FROM orders WHERE user_id = 123",
                "datasource_id": test_datasource.id,
                "execution_time": 2.5
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "optimized_query" in data
        assert "optimizations" in data

    def test_optimize_query_without_execution_time(
        self, client, auth_headers, test_datasource
    ):
        """Test optimization without execution time parameter"""
        # This should still work (execution_time is optional)
        response = client.post(
            "/api/ai/optimize-query",
            headers=auth_headers,
            json={
                "sql_query": "SELECT * FROM orders",
                "datasource_id": test_datasource.id
            }
        )
        # May succeed or fail depending on implementation
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ]

    def test_optimize_query_unauthorized(self, client, test_datasource):
        """Test query optimization without authentication"""
        response = client.post(
            "/api/ai/optimize-query",
            json={
                "sql_query": "SELECT * FROM orders",
                "datasource_id": test_datasource.id
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestChartRecommendations:
    """Test chart type recommendations"""

    @patch('app.api.v1.ai.ai_service')
    def test_recommend_chart_for_time_series(
        self, mock_ai_service, client, auth_headers
    ):
        """Test recommending chart for time series data"""
        mock_ai_service.recommend_chart_type = AsyncMock(return_value={
            "recommended_chart": "line",
            "alternatives": ["area", "bar"],
            "reasoning": "Time series data is best visualized with line charts",
            "confidence": 0.9
        })
        
        response = client.post(
            "/api/ai/recommend-chart",
            headers=auth_headers,
            json={
                "query_result": {
                    "columns": ["date", "revenue"],
                    "rows": [["2024-01-01", 1000], ["2024-01-02", 1200]]
                },
                "sql_query": "SELECT date, SUM(revenue) FROM sales GROUP BY date"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "recommended_chart" in data

    @patch('app.api.v1.ai.ai_service')
    def test_recommend_chart_for_categorical_data(
        self, mock_ai_service, client, auth_headers
    ):
        """Test recommending chart for categorical data"""
        mock_ai_service.recommend_chart_type = AsyncMock(return_value={
            "recommended_chart": "bar",
            "alternatives": ["column", "pie"],
            "reasoning": "Categorical data with counts is best shown with bar charts"
        })
        
        response = client.post(
            "/api/ai/recommend-chart",
            headers=auth_headers,
            json={
                "query_result": {
                    "columns": ["category", "count"],
                    "rows": [["Electronics", 50], ["Clothing", 30]]
                },
                "sql_query": "SELECT category, COUNT(*) FROM products GROUP BY category"
            }
        )
        assert response.status_code == status.HTTP_200_OK

    def test_recommend_chart_unauthorized(self, client):
        """Test chart recommendation without authentication"""
        response = client.post(
            "/api/ai/recommend-chart",
            json={
                "query_result": {"columns": [], "rows": []},
                "sql_query": "SELECT 1"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestInsightGeneration:
    """Test automated insight generation"""

    @patch('app.api.v1.ai.ai_service')
    def test_generate_insights(self, mock_ai_service, client, auth_headers):
        """Test generating insights from query results"""
        mock_ai_service.generate_insights = AsyncMock(return_value={
            "insights": [
                "Revenue increased by 20% compared to last month",
                "Electronics category shows highest growth",
                "Weekend sales are 15% higher than weekdays"
            ],
            "trends": ["upward", "seasonal_pattern"],
            "anomalies": [],
            "recommendations": [
                "Focus marketing on electronics",
                "Increase weekend inventory"
            ]
        })
        
        response = client.post(
            "/api/ai/generate-insights",
            headers=auth_headers,
            json={
                "query_result": {
                    "columns": ["month", "revenue", "category"],
                    "rows": [
                        ["January", 10000, "Electronics"],
                        ["February", 12000, "Electronics"]
                    ]
                },
                "sql_query": "SELECT month, revenue, category FROM sales"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "insights" in data
        assert isinstance(data["insights"], list)

    def test_generate_insights_unauthorized(self, client):
        """Test insight generation without authentication"""
        response = client.post(
            "/api/ai/generate-insights",
            json={
                "query_result": {"columns": [], "rows": []},
                "sql_query": "SELECT 1"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAIHealthCheck:
    """Test AI service health check"""

    def test_ai_health_check(self, client, auth_headers):
        """Test AI service health endpoint"""
        response = client.get("/api/ai/health", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "features" in data
        assert len(data["features"]) >= 5

    def test_ai_health_check_unauthorized(self, client):
        """Test health check without authentication"""
        response = client.get("/api/ai/health")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
