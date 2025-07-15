import pytest
from unittest.mock import patch, MagicMock
from app import create_app


@pytest.fixture
def app():
    app = create_app('testing')
    app.config.update({
        'AWS_COGNITO_DOMAIN': 'test-domain.auth.us-east-1.amazoncognito.com',
        'AWS_COGNITO_APP_CLIENT_ID': 'test-client-id',
        'AWS_COGNITO_APP_CLIENT_SECRET': 'test-secret',
        'AWS_COGNITO_REGION': 'us-east-1',
        'AWS_COGNITO_USERPOOL_ID': 'us-east-1_test123'
    })
    return app


@pytest.fixture
def client(app):
    return app.test_client()


class TestAuthIntegration:
    @patch('app.routes.auth.current_app.oauth.cognito')
    def test_full_login_flow(self, mock_oauth, client):
        """Test the complete login flow."""
        # Mock the OAuth client to avoid real HTTP requests
        mock_oauth.authorize_redirect.return_value = ('redirect_response', 302)

        # 1. Get login redirect
        response = client.get('/api/auth/login')
        assert response.status_code == 302

        # 2. Simulate successful callback
        mock_oauth.authorize_access_token.return_value = {
            'userinfo': {
                'sub': 'integration-test-user',
                'email': 'integration@test.com',
                'name': 'Integration Test'
            }
        }

        callback_response = client.get('/api/auth/callback?code=test-code')
        assert callback_response.status_code == 200

        # 3. Verify user can access profile
        profile_response = client.get('/api/auth/profile')
        assert profile_response.status_code == 200

        # 4. Test logout
        logout_response = client.get('/api/auth/logout')
        assert logout_response.status_code == 302
