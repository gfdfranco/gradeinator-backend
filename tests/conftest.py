"""
Global test configuration and fixtures.

This file contains pytest fixtures that are available to all tests.
"""
import pytest
import tempfile
import os
from app import create_app, db


@pytest.fixture(scope="session")
def app():
    """
    Create application for testing.

    Uses session scope so the app is created once per test session.
    """
    app = create_app('testing')
    return app


@pytest.fixture(scope="function")
def client(app):
    """
    Test client for making HTTP requests.

    Function scope ensures a fresh client for each test.
    """
    return app.test_client()


@pytest.fixture(scope="function")
def app_context(app):
    """
    Application context for tests that need it.

    Automatically provides Flask application context.
    """
    with app.app_context():
        yield app


@pytest.fixture(scope="function")
def fresh_db(app):
    """
    Fresh database for each test.

    Creates all tables, yields the db, then drops all tables.
    Ensures test isolation.
    """
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()
