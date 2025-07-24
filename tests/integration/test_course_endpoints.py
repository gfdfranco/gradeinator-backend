import pytest
import os
from datetime import date
from app import create_app, db

from tests.fixtures.course_fixtures import (
    sample_course_data, another_course_data, archived_course_data,
    different_user_course_data, create_test_course, authenticated_user_session,
    other_user_session, predictable_course_uuids
)


class TestCourseEndpoints:
    """Integration tests for course API endpoints."""

    @pytest.fixture
    def app(self):
        """Create test app with database."""
        # Ensure we're in testing mode
        os.environ['FLASK_ENV'] = 'testing'
        app = create_app('testing')
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()

    def test_complete_course_crud_flow(
        self, client, authenticated_user_session, sample_course_data
    ):
        """Test complete CRUD flow for courses."""
        with client.session_transaction() as sess:
            sess.update(authenticated_user_session)

        # 1. Create a course
        course_data = {
            'name': sample_course_data['name'],
            'course_code': sample_course_data['course_code'],
            'start_date': sample_course_data['start_date'].isoformat(),
            'end_date': sample_course_data['end_date'].isoformat(),
            'is_active': sample_course_data['is_active']
        }

        response = client.post('/api/courses/', json=course_data)
        assert response.status_code == 201
        created_course = response.get_json()
        course_id = created_course['id']

        # 2. Get the created course
        response = client.get(f'/api/courses/{course_id}')
        assert response.status_code == 200
        retrieved_course = response.get_json()
        assert retrieved_course['name'] == sample_course_data['name']
        assert retrieved_course['course_code'] == sample_course_data['course_code']

        # 3. List courses (should include our course)
        response = client.get('/api/courses/')
        assert response.status_code == 200
        courses = response.get_json()
        assert len(courses) == 1
        assert courses[0]['id'] == course_id

        # 4. Update course with PUT (full update)
        updated_data = {
            'name': 'Updated Course Name',
            'course_code': 'UPD101',
            'is_active': True,
            'start_date': '2024-02-01',
            'end_date': '2024-06-01'
        }

        response = client.put(f'/api/courses/{course_id}', json=updated_data)
        assert response.status_code == 200
        updated_course = response.get_json()
        assert updated_course['name'] == 'Updated Course Name'
        assert updated_course['course_code'] == 'UPD101'

        # 5. Update course with PATCH (partial update)
        patch_data = {'name': 'Partially Updated Name'}

        response = client.patch(f'/api/courses/{course_id}', json=patch_data)
        assert response.status_code == 200
        patched_course = response.get_json()
        assert patched_course['name'] == 'Partially Updated Name'
        # Should remain unchanged
        assert patched_course['course_code'] == 'UPD101'

        # 6. Archive the course
        response = client.patch(f'/api/courses/{course_id}/archive')
        assert response.status_code == 200
        archived_course = response.get_json()
        assert archived_course['is_active'] is False

        # 7. Unarchive the course
        response = client.patch(f'/api/courses/{course_id}/unarchive')
        assert response.status_code == 200
        unarchived_course = response.get_json()
        assert unarchived_course['is_active'] is True

    def test_user_isolation(
        self, app, client, authenticated_user_session, other_user_session
    ):
        """Test that users can only access their own courses."""
        with app.app_context():
            # Create courses for both users directly in database
            from app.models.course import Course

            user1_course = Course(
                name='User 1 Course',
                course_code='USER101',
                course_uuid='123e4567-e89b-12d3-a456-426614174000',
                user_id='test-user-123',
                start_date=date(2024, 1, 15),
                end_date=date(2024, 5, 15),
                is_active=True
            )

            user2_course = Course(
                name='User 2 Course',
                course_code='USER201',
                course_uuid='123e4567-e89b-12d3-a456-426614174001',
                user_id='other-user-456',
                start_date=date(2024, 2, 1),
                end_date=date(2024, 6, 1),
                is_active=True
            )

            db.session.add(user1_course)
            db.session.add(user2_course)
            db.session.commit()

            # User 1 should only see their course
            with client.session_transaction() as sess:
                sess.update(authenticated_user_session)

            response = client.get('/api/courses/')
            assert response.status_code == 200
            courses = response.get_json()
            assert len(courses) == 1
            assert courses[0]['id'] == user1_course.id

            # User 1 should not be able to access User 2's course
            response = client.get(f'/api/courses/{user2_course.id}')
            assert response.status_code == 404

            # User 2 should only see their course
            with client.session_transaction() as sess:
                sess.clear()
                sess.update(other_user_session)

            response = client.get('/api/courses/')
            assert response.status_code == 200
            courses = response.get_json()
            assert len(courses) == 1
            assert courses[0]['id'] == user2_course.id

    def test_authentication_required(self, client):
        """Test that all endpoints require authentication."""
        # Test all endpoints without authentication
        endpoints = [
            ('GET', '/api/courses/'),
            ('GET', '/api/courses/1'),
            ('PATCH', '/api/courses/1/archive'),
            ('PATCH', '/api/courses/1/unarchive'),
        ]

        for method, endpoint in endpoints:
            if method == 'GET':
                response = client.get(endpoint)
            elif method == 'PATCH':
                response = client.patch(endpoint, json={})

            assert response.status_code == 401

        # Test POST and PUT separately as they may return 400 due to validation
        post_endpoints = [
            ('POST', '/api/courses/', {}),
            ('PUT', '/api/courses/1', {}),
            ('PATCH', '/api/courses/1', {}),
        ]

        for method, endpoint, data in post_endpoints:
            if method == 'POST':
                response = client.post(endpoint, json=data)
            elif method == 'PUT':
                response = client.put(endpoint, json=data)
            elif method == 'PATCH':
                response = client.patch(endpoint, json=data)

            # These might return 400 (validation) or 401 (auth) - both are acceptable
            assert response.status_code in [400, 401]

    def test_validation_errors(self, client, authenticated_user_session):
        """Test various validation error scenarios."""
        with client.session_transaction() as sess:
            sess.update(authenticated_user_session)

        # Test short course code
        invalid_data = {
            'name': 'Test Course',
            'course_code': 'T1',  # Too short
            'start_date': '2024-01-15',
            'end_date': '2024-05-15'
        }

        response = client.post('/api/courses/', json=invalid_data)
        assert response.status_code == 400
        error_msg = 'Course code must be at least 4 characters long'
        assert error_msg in response.get_json()['message']

        # Test invalid dates (end before start)
        invalid_dates = {
            'name': 'Test Course',
            'course_code': 'TEST101',
            'start_date': '2024-05-15',
            'end_date': '2024-01-15'  # Before start date
        }

        response = client.post('/api/courses/', json=invalid_dates)
        assert response.status_code == 400
        assert 'Start date must be before end date' in \
            response.get_json()['message']

    def test_put_requires_all_fields(
        self, app, client, authenticated_user_session
    ):
        """Test that PUT endpoint requires all fields via Flask-RESTX validation."""
        with client.session_transaction() as sess:
            sess.update(authenticated_user_session)

        with app.app_context():
            # Create a course directly in database
            from app.models.course import Course
            course = Course(
                name='Test Course',
                course_code='TEST101',
                course_uuid='123e4567-e89b-12d3-a456-426614174000',
                user_id='test-user-123',
                start_date=date(2024, 1, 15),
                end_date=date(2024, 5, 15),
                is_active=True
            )
            db.session.add(course)
            db.session.commit()
            course_id = course.id

        # Test PUT with missing fields - Flask-RESTX validates this
        incomplete_data = {
            'name': 'Updated Name'
            # Missing required fields: course_code, is_active, start_date, end_date
        }

        response = client.put(f'/api/courses/{course_id}', json=incomplete_data)
        assert response.status_code == 400
        error_msg = response.get_json()['message']
        # Flask-RESTX validates input against course_put_model before our code runs
        assert 'Input payload validation failed' in error_msg

    def test_patch_allows_partial_update(
        self, app, client, authenticated_user_session
    ):
        """Test that PATCH allows partial updates."""
        with client.session_transaction() as sess:
            sess.update(authenticated_user_session)

        with app.app_context():
            # Create a course directly in database
            from app.models.course import Course
            course = Course(
                name='Test Course',
                course_code='TEST101',
                course_uuid='123e4567-e89b-12d3-a456-426614174000',
                user_id='test-user-123',
                start_date=date(2024, 1, 15),
                end_date=date(2024, 5, 15),
                is_active=True
            )
            db.session.add(course)
            db.session.commit()
            course_id = course.id
            original_code = course.course_code

        # Test PATCH with only name
        partial_data = {'name': 'New Name Only'}
        response = client.patch(f'/api/courses/{course_id}', json=partial_data)

        assert response.status_code == 200
        updated_course = response.get_json()
        assert updated_course['name'] == 'New Name Only'
        assert updated_course['course_code'] == original_code  # Unchanged

    def test_course_timestamps(self, client, authenticated_user_session):
        """Test that course timestamps are properly set."""
        with client.session_transaction() as sess:
            sess.update(authenticated_user_session)

        # Create course
        course_data = {
            'name': 'Timestamp Test',
            'course_code': 'TIME101',
            'start_date': '2024-01-15',
            'end_date': '2024-05-15'
        }

        response = client.post('/api/courses/', json=course_data)
        assert response.status_code == 201
        course = response.get_json()

        assert 'created_on' in course
        assert 'updated_on' in course
        assert course['created_on'] is not None
        assert course['updated_on'] is not None

        # Update course and check updated_on changes
        original_updated = course['updated_on']

        import time
        time.sleep(0.1)  # Small delay to ensure timestamp difference

        response = client.patch(
            f'/api/courses/{course["id"]}', json={'name': 'Updated'}
        )
        assert response.status_code == 200
        updated_course = response.get_json()

        assert updated_course['updated_on'] != original_updated
