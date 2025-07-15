import pytest
from unittest.mock import patch, MagicMock
from flask import session, url_for
from app import create_app


@pytest.fixture
def app():
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'SERVER_NAME': 'localhost:5000'
    })
    return app


@pytest.fixture
def client(app):
    return app.test_client()


class TestAuthRoutes:
    def test_login_redirects_to_cognito(self, client):
        """Test that login endpoint redirects to Cognito."""
        with patch('app.routes.auth.current_app.oauth.cognito') as mock_oauth:
            mock_oauth.authorize_redirect.return_value = ('redirect_response', 302)

            response = client.get('/api/auth/login')

            assert response.status_code == 302
            # Use url_for to generate the expected URL dynamically
            with client.application.app_context():
                expected_callback_url = url_for('auth_callback', _external=True)
                mock_oauth.authorize_redirect.assert_called_once_with(
                    expected_callback_url
                )

    @patch('app.routes.auth.current_app.oauth.cognito')
    def test_callback_success(self, mock_oauth, client):
        """Test successful OAuth callback."""
        # Mock successful token exchange
        mock_oauth.authorize_access_token.return_value = {
            'userinfo': {
                'sub': 'test-user-id',
                'email': 'test@example.com',
                'name': 'Test User'
            }
        }

        response = client.get('/api/auth/callback?code=test-code&state=test-state')

        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Login successful'
        assert data['user']['email'] == 'test@example.com'

    @patch('app.routes.auth.current_app.oauth.cognito')
    def test_callback_failure(self, mock_oauth, client):
        """Test OAuth callback failure."""
        # Mock token exchange failure
        mock_oauth.authorize_access_token.side_effect = (
            Exception('Token exchange failed')
        )
        response = client.get('/api/auth/callback?code=invalid-code')

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'Authentication failed'

    def test_profile_authenticated_user(self, client):
        """Test profile endpoint with authenticated user."""
        with client.session_transaction() as sess:
            sess['user'] = {
                'sub': 'test-user-id',
                'email': 'test@example.com',
                'name': 'Test User'
            }

        response = client.get('/api/auth/profile')

        assert response.status_code == 200
        data = response.get_json()
        assert data['email'] == 'test@example.com'

    def test_profile_unauthenticated_user(self, client):
        """Test profile endpoint without authentication."""
        response = client.get('/api/auth/profile')

        assert response.status_code == 401

    def test_logout_redirects_to_cognito(self, client):
        """Test that logout redirects to Cognito logout."""
        # Use simpler approach with environment variables
        with patch.dict('os.environ', {
            'AWS_COGNITO_DOMAIN': 'test.auth.us-east-1.amazoncognito.com',
            'AWS_COGNITO_APP_CLIENT_ID': 'test-client-id'
        }):
            response = client.get('/api/auth/logout')

            assert response.status_code == 302
            assert 'test.auth.us-east-1.amazoncognito.com/logout' in response.location
            assert 'client_id=test-client-id' in response.location
