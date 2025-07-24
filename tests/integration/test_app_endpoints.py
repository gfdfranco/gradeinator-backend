"""
Integration tests for main application endpoints.

Tests the main application endpoints (/, /health) with full Flask app context.
"""
import json
import pytest
from app import create_app


class TestRootEndpoint:
    """Test the root endpoint."""
    def test_root_endpoint_returns_200(self, client):
        """Test that GET / returns 200."""
        response = client.get('/')
        assert response.status_code == 200

    def test_root_endpoint_returns_json(self, client):
        """Test that GET / returns JSON."""
        response = client.get('/')
        assert response.content_type == 'application/json'

    def test_root_endpoint_environment_testing(self, client):
        """Test that environment is 'testing' in test mode."""
        response = client.get('/')
        data = json.loads(response.data)
        assert data['message'] == 'API is running'


class TestGeneralEndpoint:
    """Test the general namespace endpoints."""
    def test_general_hello_returns_200(self, client):
        """Test that GET /api/general/ returns 200."""
        response = client.get('/api/general/')
        assert response.status_code == 200

    def test_general_hello_returns_json(self, client):
        """Test that GET /api/general/ returns JSON."""
        response = client.get('/api/general/')
        assert response.content_type == 'application/json'


class TestHealthEndpoint:
    """Test the health check endpoint."""
    def test_health_endpoint_returns_200(self, client):
        """Test that GET /api/general/health returns 200."""
        response = client.get('/api/general/health')
        assert response.status_code == 200

    def test_health_endpoint_returns_json(self, client):
        """Test that GET /api/general/health returns JSON."""
        response = client.get('/api/general/health')
        assert response.content_type == 'application/json'

    def test_health_endpoint_json_structure(self, client):
        """Test that health endpoint returns expected JSON structure."""
        response = client.get('/api/general/health')
        data = json.loads(response.data)

        required_keys = ['status', 'timestamp', 'version', 'environment']
        for key in required_keys:
            assert key in data

    def test_health_endpoint_status_healthy(self, client):
        """Test that GET /api/general/health returns 'healthy' status."""
        response = client.get('/api/general/health')
        data = json.loads(response.data)
        assert data['status'] == 'healthy'

    def test_health_endpoint_environment_testing(self, client):
        """Test that health endpoint returns testing environment in tests."""
        response = client.get('/api/general/health')
        assert response.status_code == 200

        data = response.get_json()
        # In test environment, should be 'testing'
        assert data['environment'] == 'testing'


class TestAppErrorHandling:
    """Test error handling."""

    def test_404_for_nonexistent_route(self, client):
        """Test that nonexistent routes return 404."""
        response = client.get('/nonexistent')
        assert response.status_code == 404

    def test_405_for_wrong_method_health(self, client):
        """Test that wrong HTTP method on health returns 405."""
        response = client.post('/api/general/health')
        assert response.status_code == 405
