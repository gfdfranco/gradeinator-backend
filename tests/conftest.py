"""
Test configuration and fixtures.

This file contains pytest fixtures that are available to all tests.
"""
import os
import tempfile

import pytest

from app import create_app, db


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app('testing')

    # Ensure testing config is properly applied
    app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key',
        'FLASK_ENV': 'testing',
        'SERVER_NAME': 'localhost:5000',
        'AWS_COGNITO_DOMAIN': 'test.auth.us-east-1.amazoncognito.com',
        'AWS_COGNITO_APP_CLIENT_ID': 'test-client-id',
        'AWS_COGNITO_APP_CLIENT_SECRET': 'test-secret'
    })

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def authenticated_client(client):
    """Create authenticated test client."""
    with client.session_transaction() as sess:
        sess['user'] = {
            'sub': 'test-user-id',
            'email': 'test@example.com',
            'name': 'Test User'
        }
    return client
