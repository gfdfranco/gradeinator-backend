"""
Integration tests for core application endpoints.

Tests the main application endpoints (/, /health) with full Flask app context.
"""
import pytest
import json


class TestRootEndpoint:
    """Tests for the root endpoint (/)."""

    def test_root_endpoint_returns_200(self, client):
        """Test that GET / returns 200 status code."""
        response = client.get('/general/')
        assert response.status_code == 200

    def test_root_endpoint_returns_json(self, client):
        """Test that GET / returns JSON content type."""
        response = client.get('/general/')
        assert response.content_type == 'application/json'

    def test_root_endpoint_json_structure(self, client):
        """Test that GET / returns correct JSON structure."""
        response = client.get('/general/')
        data = json.loads(response.data)

        expected_keys = {'message', 'environment', 'debug'}
        assert set(data.keys()) == expected_keys

    def test_root_endpoint_message_content(self, client):
        """Test that GET / returns correct message."""
        response = client.get('/general/')
        data = json.loads(response.data)

        assert data['message'] == 'Gradeinator API is running!'

    def test_root_endpoint_environment_testing(self, client):
        """Test that environment is 'testing' in test mode."""
        response = client.get('/general/')
        data = json.loads(response.data)

        assert data['environment'] == 'testing'


class TestHealthEndpoint:
    """Tests for the health check endpoint (/health)."""

    def test_health_endpoint_returns_200(self, client):
        """Test that GET /health returns 200 status code."""
        response = client.get('/health')
        assert response.status_code == 200

    def test_health_endpoint_returns_json(self, client):
        """Test that GET /health returns JSON content type."""
        response = client.get('/health')
        assert response.content_type == 'application/json'

    def test_health_endpoint_json_structure(self, client):
        """Test that GET /health returns correct JSON structure."""
        response = client.get('/health')
        data = json.loads(response.data)

        expected_keys = {'status', 'environment'}
        assert set(data.keys()) == expected_keys

    def test_health_endpoint_status_healthy(self, client):
        """Test that GET /health returns 'healthy' status."""
        response = client.get('/health')
        data = json.loads(response.data)

        assert data['status'] == 'healthy'

    def test_health_endpoint_environment_testing(self, client):
        """Test that environment is 'testing' in test mode."""
        response = client.get('/health')
        data = json.loads(response.data)

        assert data['environment'] == 'testing'


class TestAppErrorHandling:
    """Tests for application-level error handling."""

    def test_404_for_nonexistent_endpoint(self, client):
        """Test that non-existent endpoints return 404."""
        response = client.get('/nonexistent')
        assert response.status_code == 404

    def test_405_for_wrong_method_root(self, client):
        """Test that wrong HTTP method on root returns 405."""
        response = client.post('/')
        assert response.status_code == 405

    def test_405_for_wrong_method_health(self, client):
        """Test that wrong HTTP method on health returns 405."""
        response = client.post('/health')
        assert response.status_code == 405
