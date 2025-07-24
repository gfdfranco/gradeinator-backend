import pytest
from datetime import datetime, date, timezone
from app.models.course import Course
from app import create_app, db


class TestCourseModel:
    """Unit tests for the Course model."""

    @pytest.fixture
    def app(self):
        """Create test app."""
        app = create_app('testing')
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()

    @pytest.fixture
    def sample_course_data(self):
        """Sample course data for testing."""
        return {
            'name': 'Introduction to Python',
            'course_code': 'PYTH101',
            'course_uuid': '123e4567-e89b-12d3-a456-426614174000',  # Hardcoded UUID
            'user_id': 'test-user-123',
            'start_date': date(2024, 1, 15),
            'end_date': date(2024, 5, 15),
            'is_active': True
        }

    def test_course_creation(self, app, sample_course_data):
        """Test creating a new course."""
        with app.app_context():
            course = Course(**sample_course_data)

            assert course.name == 'Introduction to Python'
            assert course.course_code == 'PYTH101'
            assert course.user_id == 'test-user-123'
            assert course.start_date == date(2024, 1, 15)
            assert course.end_date == date(2024, 5, 15)
            assert course.is_active is True
            assert course.course_uuid is not None

    def test_course_creation_with_defaults(self, app):
        """Test course creation with default values."""
        with app.app_context():
            course = Course(
                name='Test Course',
                course_code='TEST101',
                user_id='user-123',
                start_date=date(2024, 1, 1),
                end_date=date(2024, 12, 31)
            )

            assert course.is_active is True  # Default value
            assert course.course_uuid is not None
            assert course.created_on is not None
            assert course.updated_on is not None

    def test_course_validation_course_code_too_short(self, app):
        """Test course code validation fails for short codes."""
        with app.app_context():
            error_msg = "Course code must be at least 4 characters long"
            with pytest.raises(ValueError, match=error_msg):
                Course.validate_course_code('CS1')

    def test_course_validation_course_code_valid(self, app):
        """Test course code validation passes for valid codes."""
        with app.app_context():
            assert Course.validate_course_code('CS101') == 'CS101'
            assert Course.validate_course_code('MATH1234') == 'MATH1234'

    def test_course_validation_course_code_empty(self, app):
        """Test course code validation fails for empty code."""
        with app.app_context():
            error_msg = "Course code must be at least 4 characters long"
            with pytest.raises(ValueError, match=error_msg):
                Course.validate_course_code('')

            with pytest.raises(ValueError, match=error_msg):
                Course.validate_course_code(None)

    def test_create_course_class_method(self, app):
        """Test the create_course class method."""
        with app.app_context():
            course = Course.create_course(
                name='Advanced Python',
                course_code='PYTH201',
                user_id='user-456',
                start_date=date(2024, 2, 1),
                end_date=date(2024, 6, 1)
            )

            assert course.name == 'Advanced Python'
            assert course.course_code == 'PYTH201'
            assert course.user_id == 'user-456'
            assert course.is_active is True

    def test_create_course_invalid_dates(self, app):
        """Test create_course fails with invalid dates."""
        with app.app_context():
            with pytest.raises(ValueError, match="Start date must be before end date"):
                Course.create_course(
                    name='Test Course',
                    course_code='TEST101',
                    user_id='user-123',
                    start_date=date(2024, 6, 1),  # After end date
                    end_date=date(2024, 2, 1)
                )

    def test_create_course_same_dates(self, app):
        """Test create_course fails with same start and end dates."""
        with app.app_context():
            same_date = date(2024, 3, 1)
            with pytest.raises(ValueError, match="Start date must be before end date"):
                Course.create_course(
                    name='Test Course',
                    course_code='TEST101',
                    user_id='user-123',
                    start_date=same_date,
                    end_date=same_date
                )

    def test_create_course_invalid_course_code(self, app):
        """Test create_course fails with invalid course code."""
        with app.app_context():
            error_msg = "Course code must be at least 4 characters long"
            with pytest.raises(ValueError, match=error_msg):
                Course.create_course(
                    name='Test Course',
                    course_code='T1',  # Too short
                    user_id='user-123',
                    start_date=date(2024, 1, 1),
                    end_date=date(2024, 12, 31)
                )

    def test_course_to_dict(self, app, sample_course_data):
        """Test converting course to dictionary."""
        with app.app_context():
            course = Course(**sample_course_data)
            course_dict = course.to_dict()

            assert course_dict['name'] == 'Introduction to Python'
            assert course_dict['course_code'] == 'PYTH101'
            assert course_dict['user_id'] == 'test-user-123'
            assert course_dict['start_date'] == '2024-01-15'
            assert course_dict['end_date'] == '2024-05-15'
            assert course_dict['is_active'] is True
            assert 'course_uuid' in course_dict
            assert 'id' in course_dict

    def test_course_repr(self, app, sample_course_data):
        """Test course string representation."""
        with app.app_context():
            course = Course(**sample_course_data)
            repr_str = repr(course)

            assert 'Course' in repr_str
            assert 'Introduction to Python' in repr_str
            assert str(course.course_uuid) in repr_str

    def test_course_timestamps(self, app, sample_course_data):
        """Test that timestamps are set correctly."""
        with app.app_context():
            course = Course(**sample_course_data)

            assert course.created_on is not None
            assert course.updated_on is not None
            assert isinstance(course.created_on, datetime)
            assert isinstance(course.updated_on, datetime)

            # Should be UTC timezone
            assert course.created_on.tzinfo is not None
            assert course.updated_on.tzinfo is not None

    def test_course_creation_with_hardcoded_uuid(self, app, sample_course_data):
        """Test creating a course with a specific UUID."""
        with app.app_context():
            expected_uuid = '123e4567-e89b-12d3-a456-426614174000'
            course = Course(**sample_course_data)

            assert course.name == 'Introduction to Python'
            assert course.course_uuid == expected_uuid
            assert str(course.course_uuid) == expected_uuid

    def test_course_to_dict_with_known_uuid(self, app, sample_course_data):
        """Test converting course to dictionary with known UUID."""
        with app.app_context():
            course = Course(**sample_course_data)
            course_dict = course.to_dict()

            assert course_dict['course_uuid'] == '123e4567-e89b-12d3-a456-426614174000'
            assert course_dict['name'] == 'Introduction to Python'

    def test_course_repr_with_known_uuid(self, app, sample_course_data):
        """Test course string representation with known UUID."""
        with app.app_context():
            course = Course(**sample_course_data)
            repr_str = repr(course)

            assert 'Course 123e4567-e89b-12d3-a456-426614174000' in repr_str
            assert 'Introduction to Python' in repr_str
