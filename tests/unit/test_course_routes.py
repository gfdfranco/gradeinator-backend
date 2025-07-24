import pytest
from unittest.mock import patch, MagicMock
from datetime import date
from app import create_app


class TestCourseRoutes:
    """Unit tests for course routes."""

    @pytest.fixture
    def app(self):
        """Create test app."""
        return create_app('testing')

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()

    @pytest.fixture
    def authenticated_session(self):
        """Mock authenticated session."""
        return {
            'user': {
                'sub': 'test-user-123',
                'email': 'test@example.com',
                'name': 'Test User'
            }
        }

    def test_require_auth_decorator_with_user(self, client, authenticated_session):
        """Test require_auth decorator allows authenticated users."""
        with client.session_transaction() as sess:
            sess.update(authenticated_session)

        with patch('app.models.course.Course.query') as mock_query:
            mock_query.filter_by.return_value.all.return_value = []

            response = client.get('/api/courses/')
            assert response.status_code == 200

    def test_require_auth_decorator_without_user(self, client):
        """Test require_auth decorator blocks unauthenticated users."""
        response = client.get('/api/courses/')
        assert response.status_code == 401
        data = response.get_json()
        assert data['message'] == 'Authentication required'

    def test_course_list_get(self, client, authenticated_session):
        """Test GET /api/courses/ returns user's courses."""
        with client.session_transaction() as sess:
            sess.update(authenticated_session)

        mock_course = MagicMock()
        mock_course.to_dict.return_value = {
            'id': 1,
            'name': 'Test Course',
            'course_code': 'TEST101',
            'is_active': True
        }

        with patch('app.models.course.Course.query') as mock_query:
            mock_query.filter_by.return_value.all.return_value = [mock_course]

            response = client.get('/api/courses/')
            assert response.status_code == 200
            data = response.get_json()
            assert len(data) == 1
            assert data[0]['name'] == 'Test Course'

    def test_course_create_success(self, client, authenticated_session):
        """Test POST /api/courses/ creates a new course."""
        with client.session_transaction() as sess:
            sess.update(authenticated_session)

        course_data = {
            'name': 'New Course',
            'course_code': 'NEW101',
            'start_date': '2024-01-15',
            'end_date': '2024-05-15',
            'is_active': True
        }

        mock_course = MagicMock()
        mock_course.to_dict.return_value = {
            'id': 1,
            'name': 'New Course',
            'course_code': 'NEW101'
        }

        with patch('app.models.course.Course.create_course') as mock_create, \
             patch('app.db.session') as mock_session:
            mock_create.return_value = mock_course

            response = client.post('/api/courses/', json=course_data)
            assert response.status_code == 201

            mock_create.assert_called_once()
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()

    def test_course_create_validation_error(self, client, authenticated_session):
        """Test POST /api/courses/ handles validation errors."""
        with client.session_transaction() as sess:
            sess.update(authenticated_session)

        course_data = {
            'name': 'New Course',
            'course_code': 'XY',  # Too short
            'start_date': '2024-01-15',
            'end_date': '2024-05-15'
        }

        with patch('app.models.course.Course.create_course') as mock_create:
            error_msg = "Course code must be at least 4 characters long"
            mock_create.side_effect = ValueError(error_msg)

            response = client.post('/api/courses/', json=course_data)
            assert response.status_code == 400
            data = response.get_json()
            assert error_msg in data['message']

    def test_course_get_by_id_success(self, client, authenticated_session):
        """Test GET /api/courses/{id} returns specific course."""
        with client.session_transaction() as sess:
            sess.update(authenticated_session)

        mock_course = MagicMock()
        mock_course.to_dict.return_value = {
            'id': 1,
            'name': 'Test Course',
            'course_code': 'TEST101'
        }

        with patch('app.models.course.Course.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = mock_course

            response = client.get('/api/courses/1')
            assert response.status_code == 200
            data = response.get_json()
            assert data['name'] == 'Test Course'

    def test_course_get_by_id_not_found(self, client, authenticated_session):
        """Test GET /api/courses/{id} returns 404 for non-existent course."""
        with client.session_transaction() as sess:
            sess.update(authenticated_session)

        with patch('app.models.course.Course.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = None

            response = client.get('/api/courses/999')
            assert response.status_code == 404

    def test_course_put_missing_fields(self, client, authenticated_session):
        """Test PUT /api/courses/{id} requires all fields."""
        with client.session_transaction() as sess:
            sess.update(authenticated_session)

        # Missing 'end_date' field
        update_data = {
            'name': 'Updated Course',
            'course_code': 'UPD101',
            'is_active': True,
            'start_date': '2024-01-15'
        }

        mock_course = MagicMock()

        with patch('app.models.course.Course.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = mock_course

            response = client.put('/api/courses/1', json=update_data)
            assert response.status_code == 400
            data = response.get_json()
            # Flask-RESTX validates input before reaching our code
            assert 'Input payload validation failed' in data['message']

    def test_course_patch_partial_update(self, client, authenticated_session):
        """Test PATCH /api/courses/{id} allows partial updates."""
        with client.session_transaction() as sess:
            sess.update(authenticated_session)

        update_data = {
            'name': 'Updated Course Name'
        }

        mock_course = MagicMock()
        mock_course.to_dict.return_value = {
            'id': 1,
            'name': 'Updated Course Name'
        }
        mock_course.start_date = date(2024, 1, 15)
        mock_course.end_date = date(2024, 5, 15)

        with patch('app.models.course.Course.query') as mock_query, \
             patch('app.db.session') as mock_session:
            mock_query.filter_by.return_value.first.return_value = mock_course

            response = client.patch('/api/courses/1', json=update_data)
            assert response.status_code == 200

            mock_session.commit.assert_called_once()

    def test_course_archive(self, client, authenticated_session):
        """Test PATCH /api/courses/{id}/archive sets is_active to False."""
        with client.session_transaction() as sess:
            sess.update(authenticated_session)

        mock_course = MagicMock()
        mock_course.to_dict.return_value = {
            'id': 1,
            'is_active': False
        }

        with patch('app.models.course.Course.query') as mock_query, \
             patch('app.db.session') as mock_session:
            mock_query.filter_by.return_value.first.return_value = mock_course

            response = client.patch('/api/courses/1/archive')
            assert response.status_code == 200

            assert mock_course.is_active is False
            mock_session.commit.assert_called_once()

    def test_course_unarchive(self, client, authenticated_session):
        """Test PATCH /api/courses/{id}/unarchive sets is_active to True."""
        with client.session_transaction() as sess:
            sess.update(authenticated_session)

        mock_course = MagicMock()
        mock_course.to_dict.return_value = {
            'id': 1,
            'is_active': True
        }

        with patch('app.models.course.Course.query') as mock_query, \
             patch('app.db.session') as mock_session:
            mock_query.filter_by.return_value.first.return_value = mock_course

            response = client.patch('/api/courses/1/unarchive')
            assert response.status_code == 200

            assert mock_course.is_active is True
            mock_session.commit.assert_called_once()
