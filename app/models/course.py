import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date
from sqlalchemy.ext.hybrid import hybrid_property
from app import db


class Course(db.Model):
    """Course model for managing academic courses."""

    __tablename__ = 'courses'

    # Primary key
    id = Column(Integer, primary_key=True)

    # Course identification
    name = Column(String(255), nullable=False)
    # Use String for UUID to be compatible with SQLite and PostgreSQL
    _course_uuid = Column('course_uuid', String(36), unique=True, nullable=False)
    course_code = Column(String(20), nullable=False)

    # Status
    is_active = Column(Boolean, nullable=False, default=True)

    # User relationship (Cognito user ID)
    user_id = Column(String(255), nullable=False)  # Cognito user ID

    # Course dates
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    # Timestamps
    created_on = Column(
        DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_on = Column(
        DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __init__(self, **kwargs):
        # Set defaults before calling super().__init__
        if 'is_active' not in kwargs:
            kwargs['is_active'] = True

        if 'created_on' not in kwargs:
            kwargs['created_on'] = datetime.now(timezone.utc)

        if 'updated_on' not in kwargs:
            kwargs['updated_on'] = datetime.now(timezone.utc)

        # Handle course_uuid parameter
        if 'course_uuid' in kwargs:
            self._course_uuid = str(kwargs.pop('course_uuid'))
        else:
            self._course_uuid = str(uuid.uuid4())

        super().__init__(**kwargs)

    @hybrid_property
    def course_uuid(self):
        """Get course UUID as string."""
        return self._course_uuid

    @course_uuid.setter
    def course_uuid(self, value):
        """Set course UUID, ensuring it's stored as string."""
        self._course_uuid = str(value) if value else str(uuid.uuid4())

    def __repr__(self):
        return f'<Course {self.course_uuid}: {self.name}>'

    def to_dict(self):
        """Convert course to dictionary for API responses."""
        return {
            'id': self.id,
            'name': self.name,
            'course_uuid': str(self.course_uuid),
            'course_code': self.course_code,
            'is_active': self.is_active,
            'user_id': self.user_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_on': self.created_on.isoformat() if self.created_on else None,
            'updated_on': self.updated_on.isoformat() if self.updated_on else None
        }

    @classmethod
    def validate_course_code(cls, course_code):
        """Validate course code format and length."""
        if not course_code or len(course_code) < 4:
            raise ValueError("Course code must be at least 4 characters long")
        return course_code

    @classmethod
    def create_course(
        cls, name, course_code, user_id,
        start_date, end_date, is_active=True, course_uuid=None
    ):
        """Create a new course with validation."""
        # Validate course code
        cls.validate_course_code(course_code)

        # Validate dates
        if start_date >= end_date:
            raise ValueError("Start date must be before end date")

        # Create course data
        course_data = {
            'name': name,
            'course_code': course_code,
            'user_id': user_id,
            'start_date': start_date,
            'end_date': end_date,
            'is_active': is_active
        }

        # Add UUID if provided
        if course_uuid:
            course_data['course_uuid'] = course_uuid

        # Create new course
        course = cls(**course_data)
        return course
