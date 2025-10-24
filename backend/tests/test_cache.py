"""
Comprehensive tests for cache management endpoints
"""
import pytest
from fastapi import status
from unittest.mock import Mock, patch


class TestCacheStats:
    """Test cache statistics endpoints"""

    @patch('app.api.v1.cache.CacheService')
    def test_get_cache_stats(self, mock_cache_service, client, auth_headers):
        """Test getting cache statistics"""
        # Mock cache service
        mock_instance = Mock()
        mock_instance.get_cache_stats.return_value = {
            "hit_rate": 0.75,
            "total_hits": 300,
            "total_misses": 100,
            "cached_queries": 50,
            "memory_usage": "10 MB"
        }
        mock_cache_service.return_value = mock_instance
        
        response = client.get("/api/cache/stats", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["hit_rate"] == 0.75
        assert data["data"]["total_hits"] == 300

    def test_get_cache_stats_unauthorized(self, client):
        """Test getting cache stats without authentication fails"""
        response = client.get("/api/cache/stats")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch('app.api.v1.cache.CacheService')
    def test_get_cache_stats_with_no_data(self, mock_cache_service, client, auth_headers):
        """Test getting cache stats when no cache data exists"""
        mock_instance = Mock()
        mock_instance.get_cache_stats.return_value = {
            "hit_rate": 0.0,
            "total_hits": 0,
            "total_misses": 0,
            "cached_queries": 0
        }
        mock_cache_service.return_value = mock_instance
        
        response = client.get("/api/cache/stats", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["total_hits"] == 0


class TestCacheClear:
    """Test cache clearing operations"""

    @patch('app.api.v1.cache.CacheService')
    def test_clear_all_cache(self, mock_cache_service, client, auth_headers):
        """Test clearing all cached queries"""
        mock_instance = Mock()
        mock_instance.enabled = True
        mock_instance.clear_all_cache.return_value = True
        mock_cache_service.return_value = mock_instance
        
        response = client.delete("/api/cache/clear", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "cleared successfully" in data["message"].lower()

    def test_clear_cache_unauthorized(self, client):
        """Test clearing cache without authentication fails"""
        response = client.delete("/api/cache/clear")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch('app.api.v1.cache.CacheService')
    def test_clear_cache_service_unavailable(self, mock_cache_service, client, auth_headers):
        """Test clearing cache when service is unavailable"""
        mock_instance = Mock()
        mock_instance.enabled = False
        mock_cache_service.return_value = mock_instance
        
        response = client.delete("/api/cache/clear", headers=auth_headers)
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE

    @patch('app.api.v1.cache.CacheService')
    def test_clear_cache_failure(self, mock_cache_service, client, auth_headers):
        """Test handling cache clear failure"""
        mock_instance = Mock()
        mock_instance.enabled = True
        mock_instance.clear_all_cache.return_value = False
        mock_cache_service.return_value = mock_instance
        
        response = client.delete("/api/cache/clear", headers=auth_headers)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestDatasourceCache:
    """Test datasource-specific cache operations"""

    @patch('app.api.v1.cache.CacheService')
    def test_clear_datasource_cache(self, mock_cache_service, client, auth_headers, test_datasource):
        """Test clearing cache for specific datasource"""
        mock_instance = Mock()
        mock_instance.enabled = True
        mock_instance.invalidate_datasource_cache.return_value = 5
        mock_cache_service.return_value = mock_instance
        
        response = client.delete(
            f"/api/cache/datasource/{test_datasource.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["deleted_count"] == 5

    def test_clear_datasource_cache_unauthorized(self, client, test_datasource):
        """Test clearing datasource cache without authentication fails"""
        response = client.delete(f"/api/cache/datasource/{test_datasource.id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch('app.api.v1.cache.CacheService')
    def test_clear_nonexistent_datasource_cache(self, mock_cache_service, client, auth_headers):
        """Test clearing cache for nonexistent datasource"""
        mock_instance = Mock()
        mock_instance.enabled = True
        mock_instance.invalidate_datasource_cache.return_value = 0
        mock_cache_service.return_value = mock_instance
        
        response = client.delete(
            "/api/cache/datasource/nonexistent-id",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["deleted_count"] == 0

    @patch('app.api.v1.cache.CacheService')
    def test_clear_datasource_cache_service_unavailable(self, mock_cache_service, client, auth_headers, test_datasource):
        """Test clearing datasource cache when service unavailable"""
        mock_instance = Mock()
        mock_instance.enabled = False
        mock_cache_service.return_value = mock_instance
        
        response = client.delete(
            f"/api/cache/datasource/{test_datasource.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


class TestCacheStatsReset:
    """Test cache statistics reset"""

    @patch('app.api.v1.cache.CacheService')
    def test_reset_cache_stats(self, mock_cache_service, client, auth_headers):
        """Test resetting cache statistics"""
        mock_instance = Mock()
        mock_instance.enabled = True
        mock_instance.reset_stats.return_value = True
        mock_cache_service.return_value = mock_instance
        
        response = client.post("/api/cache/reset-stats", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "reset successfully" in data["message"].lower()

    def test_reset_cache_stats_unauthorized(self, client):
        """Test resetting cache stats without authentication fails"""
        response = client.post("/api/cache/reset-stats")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch('app.api.v1.cache.CacheService')
    def test_reset_cache_stats_service_unavailable(self, mock_cache_service, client, auth_headers):
        """Test resetting stats when service unavailable"""
        mock_instance = Mock()
        mock_instance.enabled = False
        mock_cache_service.return_value = mock_instance
        
        response = client.post("/api/cache/reset-stats", headers=auth_headers)
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE

    @patch('app.api.v1.cache.CacheService')
    def test_reset_cache_stats_failure(self, mock_cache_service, client, auth_headers):
        """Test handling cache stats reset failure"""
        mock_instance = Mock()
        mock_instance.enabled = True
        mock_instance.reset_stats.return_value = False
        mock_cache_service.return_value = mock_instance
        
        response = client.post("/api/cache/reset-stats", headers=auth_headers)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
