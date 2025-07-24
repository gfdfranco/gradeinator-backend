import pytest
from datetime import date
from app.models.course import Course
from app import db


@pytest.fixture
def sample_course_data():
    """Sample course data for testing."""
    return {
        'name': 'Introduction to Python',
        'course_code': 'PYTH101',
        'course_uuid': str(uuid.uuid4()),  # Dynamically generated UUID
        'user_id': 'test-user-123',
        'start_date': date(2024, 1, 15),
        'end_date': date(2024, 5, 15),
        'is_active': True
    }


@pytest.fixture
def another_course_data():
    """Another sample course for testing."""
    return {
        'name': 'Advanced JavaScript',
        'course_code': 'JS201',
        'course_uuid': '123e4567-e89b-12d3-a456-426614174001',  # Hardcoded UUID
        'user_id': 'test-user-123',
        'start_date': date(2024, 2, 1),
        'end_date': date(2024, 6, 1),
        'is_active': True
    }


@pytest.fixture
def archived_course_data():
    """Sample archived course for testing."""
    return {
        'name': 'Old Course',
        'course_code': 'OLD101',
        'course_uuid': '123e4567-e89b-12d3-a456-426614174002',  # Hardcoded UUID
        'user_id': 'test-user-123',
        'start_date': date(2023, 1, 15),
        'end_date': date(2023, 5, 15),
        'is_active': False
    }


@pytest.fixture
def different_user_course_data():
    """Course data for a different user."""
    return {
        'name': 'Other User Course',
        'course_code': 'OTHER101',
        'course_uuid': '123e4567-e89b-12d3-a456-426614174003',  # Hardcoded UUID
        'user_id': 'other-user-456',
        'start_date': date(2024, 3, 1),
        'end_date': date(2024, 7, 1),
        'is_active': True
    }


@pytest.fixture
def create_test_course(sample_course_data):
    """Create a test course in the database."""
    def _create_course(course_data=None):
        if course_data is None:
            course_data = sample_course_data.copy()
        else:
            course_data = course_data.copy()

        # Create course directly with the data
        course = Course(**course_data)
        db.session.add(course)
        db.session.commit()
        return course

    return _create_course


# Additional fixtures for specific testing scenarios
@pytest.fixture
def predictable_course_uuids():
    """Predefined UUIDs for testing."""
    return {
        'course_1': '123e4567-e89b-12d3-a456-426614174000',
        'course_2': '123e4567-e89b-12d3-a456-426614174001',
        'course_3': '123e4567-e89b-12d3-a456-426614174002',
        'course_4': '123e4567-e89b-12d3-a456-426614174003',
        'course_5': '123e4567-e89b-12d3-a456-426614174004',
    }


@pytest.fixture
def authenticated_user_session():
    """Mock authenticated user session."""
    return {
        'user': {
            'sub': 'test-user-123',
            'email': 'test@example.com',
            'name': 'Test User',
            'given_name': 'Test',
            'family_name': 'User'
        }
    }


@pytest.fixture
def other_user_session():
    """Mock session for a different user."""
    return {
        'user': {
            'sub': 'other-user-456',
            'email': 'other@example.com',
            'name': 'Other User'
        }
    }
