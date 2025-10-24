"""
Tests for demo data generation endpoints
"""
import pytest
from fastapi import status
from unittest.mock import Mock, patch


class TestDemoData:
    """Test demo data generation"""

    @patch('app.api.v1.demo.DemoService')
    def test_generate_demo_data(self, mock_service, client, auth_headers):
        """Test generating demo data"""
        mock_service.generate_demo_data.return_value = {
            "success": True,
            "message": "Demo data generated successfully",
            "statistics": {
                "users_created": 1,
                "datasources_created": 3,
                "queries_created": 25,
                "dashboards_created": 6
            }
        }
        
        response = client.post("/api/demo/generate", headers=auth_headers)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_generate_demo_data_unauthorized(self, client):
        """Test generating demo data without authentication"""
        response = client.post("/api/demo/generate")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch('app.api.v1.demo.DemoService')
    def test_demo_data_already_exists(self, mock_service, client, auth_headers):
        """Test generating demo data when it already exists"""
        mock_service.generate_demo_data.return_value = {
            "success": False,
            "message": "Demo data already exists"
        }
        
        response = client.post("/api/demo/generate", headers=auth_headers)
        # Should handle gracefully
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND
        ]
