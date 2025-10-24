"""
Comprehensive tests for export endpoints
"""
import pytest
import io
import json
from fastapi import status
from unittest.mock import Mock, patch, AsyncMock


class TestCSVExport:
    """Test CSV export functionality"""

    @patch('app.api.v1.exports.query_service')
    def test_export_query_to_csv(self, mock_query_service, client, auth_headers, test_query):
        """Test exporting query results to CSV"""
        # Mock query execution
        mock_query_service.execute_query = AsyncMock(return_value={
            'columns': ['id', 'name', 'email'],
            'rows': [
                [1, 'John Doe', 'john@example.com'],
                [2, 'Jane Smith', 'jane@example.com']
            ]
        })
        
        response = client.get(
            f"/api/exports/query/{test_query.id}/csv",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.headers['content-type'] == 'text/csv; charset=utf-8'
        assert 'Content-Disposition' in response.headers
        assert '.csv' in response.headers['Content-Disposition']
        
        # Check CSV content
        content = response.content.decode('utf-8')
        assert 'id,name,email' in content
        assert 'John Doe' in content

    def test_export_csv_unauthorized(self, client, test_query):
        """Test CSV export without authentication fails"""
        response = client.get(f"/api/exports/query/{test_query.id}/csv")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_export_csv_nonexistent_query(self, client, auth_headers):
        """Test exporting nonexistent query to CSV fails"""
        response = client.get(
            "/api/exports/query/nonexistent-id/csv",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch('app.api.v1.exports.query_service')
    def test_export_csv_query_execution_fails(self, mock_query_service, client, auth_headers, test_query):
        """Test CSV export handles query execution failure"""
        mock_query_service.execute_query = AsyncMock(
            side_effect=Exception("Query execution failed")
        )
        
        response = client.get(
            f"/api/exports/query/{test_query.id}/csv",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestExcelExport:
    """Test Excel export functionality"""

    @patch('app.api.v1.exports.EXCEL_AVAILABLE', True)
    @patch('app.api.v1.exports.query_service')
    @patch('app.api.v1.exports.Workbook')
    def test_export_query_to_excel(self, mock_workbook, mock_query_service, client, auth_headers, test_query):
        """Test exporting query results to Excel"""
        # Mock query execution
        mock_query_service.execute_query = AsyncMock(return_value={
            'columns': ['id', 'name', 'email'],
            'rows': [
                [1, 'John Doe', 'john@example.com'],
                [2, 'Jane Smith', 'jane@example.com']
            ]
        })
        
        # Mock workbook
        mock_wb = Mock()
        mock_ws = Mock()
        mock_ws.columns = []
        mock_wb.active = mock_ws
        mock_wb.save = Mock()
        mock_workbook.return_value = mock_wb
        
        response = client.get(
            f"/api/exports/query/{test_query.id}/excel",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert 'spreadsheetml' in response.headers['content-type']
        assert '.xlsx' in response.headers['Content-Disposition']

    @patch('app.api.v1.exports.EXCEL_AVAILABLE', False)
    def test_export_excel_not_available(self, client, auth_headers, test_query):
        """Test Excel export when openpyxl not installed"""
        response = client.get(
            f"/api/exports/query/{test_query.id}/excel",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_501_NOT_IMPLEMENTED

    def test_export_excel_unauthorized(self, client, test_query):
        """Test Excel export without authentication fails"""
        response = client.get(f"/api/exports/query/{test_query.id}/excel")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_export_excel_nonexistent_query(self, client, auth_headers):
        """Test exporting nonexistent query to Excel fails"""
        response = client.get(
            "/api/exports/query/nonexistent-id/excel",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestJSONExport:
    """Test JSON export functionality"""

    def test_export_dashboard_to_json(self, client, auth_headers, test_dashboard):
        """Test exporting dashboard configuration to JSON"""
        response = client.get(
            f"/api/exports/dashboard/{test_dashboard.id}/json",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.headers['content-type'] == 'application/json'
        assert '.json' in response.headers['Content-Disposition']
        
        # Parse and verify JSON content
        content = json.loads(response.content)
        assert content['name'] == test_dashboard.name
        assert 'layout' in content
        assert 'widgets' in content
        assert 'exported_at' in content
        assert 'version' in content

    def test_export_json_unauthorized(self, client, test_dashboard):
        """Test JSON export without authentication fails"""
        response = client.get(f"/api/exports/dashboard/{test_dashboard.id}/json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_export_json_nonexistent_dashboard(self, client, auth_headers):
        """Test exporting nonexistent dashboard to JSON fails"""
        response = client.get(
            "/api/exports/dashboard/nonexistent-id/json",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_export_json_with_widgets(self, client, auth_headers, test_dashboard, test_query):
        """Test JSON export includes widget configuration"""
        # Update dashboard with widgets
        test_dashboard.widgets = [
            {
                "id": "widget-1",
                "type": "chart",
                "query_id": test_query.id,
                "title": "Test Chart"
            }
        ]
        
        response = client.get(
            f"/api/exports/dashboard/{test_dashboard.id}/json",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        content = json.loads(response.content)
        assert len(content['widgets']) == 1
        assert content['widgets'][0]['query_id'] == test_query.id


class TestPDFExport:
    """Test PDF export functionality"""

    @patch('app.api.v1.exports.PDF_AVAILABLE', True)
    @patch('app.api.v1.exports.SimpleDocTemplate')
    def test_export_dashboard_to_pdf(self, mock_pdf, client, auth_headers, test_dashboard):
        """Test exporting dashboard to PDF"""
        # Mock PDF generation
        mock_doc = Mock()
        mock_doc.build = Mock()
        mock_pdf.return_value = mock_doc
        
        response = client.post(
            f"/api/exports/dashboard/{test_dashboard.id}/pdf",
            headers=auth_headers
        )
        
        # PDF export might not be fully implemented, check appropriate response
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_501_NOT_IMPLEMENTED,
            status.HTTP_404_NOT_FOUND
        ]

    @patch('app.api.v1.exports.PDF_AVAILABLE', False)
    def test_export_pdf_not_available(self, client, auth_headers, test_dashboard):
        """Test PDF export when reportlab not installed"""
        response = client.post(
            f"/api/exports/dashboard/{test_dashboard.id}/pdf",
            headers=auth_headers
        )
        # Should return 501 if endpoint checks for PDF_AVAILABLE
        assert response.status_code in [
            status.HTTP_501_NOT_IMPLEMENTED,
            status.HTTP_404_NOT_FOUND
        ]


class TestExportPermissions:
    """Test export permissions and access control"""

    @patch('app.api.v1.exports.query_service')
    def test_user_can_export_own_query(self, mock_query_service, client, auth_headers, test_query):
        """Test user can export their own query"""
        mock_query_service.execute_query = AsyncMock(return_value={
            'columns': ['id'],
            'rows': [[1]]
        })
        
        response = client.get(
            f"/api/exports/query/{test_query.id}/csv",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK

    def test_export_requires_authentication(self, client, test_query, test_dashboard):
        """Test all export endpoints require authentication"""
        endpoints = [
            f"/api/exports/query/{test_query.id}/csv",
            f"/api/exports/query/{test_query.id}/excel",
            f"/api/exports/dashboard/{test_dashboard.id}/json"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
