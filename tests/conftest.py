"""
Test configuration and fixtures.

This file contains pytest fixtures that are available to all tests.
"""
import pytest
import os
from app import create_app, db


@pytest.fixture(scope='session')
def app():
    """Create application for the tests."""
    # Force testing environment
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app('testing')

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def app_context(app):
    """Create an application context."""
    with app.app_context():
        yield app


@pytest.fixture(autouse=True)
def db_session(app):
    """Create a database session for testing with automatic cleanup."""
    with app.app_context():
        # Start a transaction
        connection = db.engine.connect()
        transaction = connection.begin()

        # Configure session to use the transaction
        db.session.configure(bind=connection)

        yield db.session

        # Rollback the transaction and close connection
        transaction.rollback()
        connection.close()
        db.session.remove()


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
