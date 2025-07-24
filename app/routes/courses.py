from datetime import datetime
from flask import request, session
from flask_restx import Namespace, Resource, fields
from sqlalchemy.exc import IntegrityError
from app import db
from app.models.course import Course

# Create namespace for course endpoints
api = Namespace('courses', description='Course management operations')

# Define request/response models
course_model = api.model('Course', {
    'id': fields.Integer(readonly=True, description='Course ID'),
    'name': fields.String(required=True, description='Course name'),
    'course_uuid': fields.String(readonly=True, description='Course UUID'),
    'course_code': fields.String(
        required=True, description='Course code (min 4 characters)'
    ),
    'is_active': fields.Boolean(
        description='Whether the course is active', default=True
    ),
    'user_id': fields.String(
        readonly=True, description='User ID who created the course'
    ),
    'start_date': fields.Date(required=True, description='Course start date'),
    'end_date': fields.Date(required=True, description='Course end date'),
    'created_on': fields.DateTime(readonly=True, description='Creation timestamp'),
    'updated_on': fields.DateTime(readonly=True, description='Last update timestamp')
})

course_input_model = api.model('CourseInput', {
    'name': fields.String(required=True, description='Course name'),
    'course_code': fields.String(
        required=True, description='Course code (min 4 characters)'
    ),
    'is_active': fields.Boolean(
        description='Whether the course is active', default=True
    ),
    'start_date': fields.Date(required=True, description='Course start date'),
    'end_date': fields.Date(required=True, description='Course end date')
})

course_update_model = api.model('CourseUpdate', {
    'name': fields.String(description='Course name'),
    'course_code': fields.String(description='Course code (min 4 characters)'),
    'is_active': fields.Boolean(description='Whether the course is active'),
    'start_date': fields.Date(description='Course start date'),
    'end_date': fields.Date(description='Course end date')
})

# Add a new model for PUT that requires all updatable fields
course_put_model = api.model('CoursePut', {
    'name': fields.String(required=True, description='Course name'),
    'course_code': fields.String(
        required=True, description='Course code (min 4 characters)'
    ),
    'is_active': fields.Boolean(
        required=True, description='Whether the course is active'
    ),
    'start_date': fields.Date(required=True, description='Course start date'),
    'end_date': fields.Date(required=True, description='Course end date')
})


def require_auth(f):
    """Decorator to require authentication."""
    def decorated_function(*args, **kwargs):
        user = session.get('user')
        if not user:
            api.abort(401, "Authentication required")
        return f(*args, **kwargs)
    return decorated_function


@api.route('/')
class CourseList(Resource):
    @api.doc('list_courses')
    @api.marshal_list_with(course_model)
    @require_auth
    def get(self):
        """Get all courses for the authenticated user"""
        user = session.get('user')
        user_id = user.get('sub')  # Cognito user ID

        courses = Course.query.filter_by(user_id=user_id).all()
        return [course.to_dict() for course in courses]

    @api.doc('create_course')
    @api.expect(course_input_model)
    @api.marshal_with(course_model, code=201)
    @require_auth
    def post(self):
        """Create a new course"""
        user = session.get('user')
        user_id = user.get('sub')  # Cognito user ID

        data = request.get_json()

        try:
            # Parse dates
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()

            # Create course
            course = Course.create_course(
                name=data['name'],
                course_code=data['course_code'],
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                is_active=data.get('is_active', True)
            )

            db.session.add(course)
            db.session.commit()

            return course.to_dict(), 201

        except ValueError as e:
            api.abort(400, str(e))
        except IntegrityError:
            db.session.rollback()
            api.abort(400, "Course code must be unique")
        except Exception as e:
            db.session.rollback()
            api.abort(500, f"Failed to create course: {str(e)}")


@api.route('/<int:course_id>')
class CourseResource(Resource):
    @api.doc('get_course')
    @api.marshal_with(course_model)
    @require_auth
    def get(self, course_id):
        """Get a specific course"""
        user = session.get('user')
        user_id = user.get('sub')

        course = Course.query.filter_by(id=course_id, user_id=user_id).first()
        if not course:
            api.abort(404, "Course not found")

        return course.to_dict()

    def _update_course_fields(self, course, data):
        """Helper to update course fields from request data."""
        if 'name' in data:
            course.name = data['name']
        if 'course_code' in data:
            Course.validate_course_code(data['course_code'])
            course.course_code = data['course_code']
        if 'is_active' in data:
            course.is_active = data['is_active']
        if 'start_date' in data:
            course.start_date = datetime.strptime(
                data['start_date'], '%Y-%m-%d'
            ).date()
        if 'end_date' in data:
            course.end_date = datetime.strptime(
                data['end_date'], '%Y-%m-%d'
            ).date()

    @api.doc('update_course_full')
    @api.expect(course_put_model)  # Use the new model that requires all fields
    @api.marshal_with(course_model)
    @require_auth
    def put(self, course_id):
        """Update a course (full update - requires all fields)"""
        user = session.get('user')
        user_id = user.get('sub')

        course = Course.query.filter_by(id=course_id, user_id=user_id).first()
        if not course:
            api.abort(404, "Course not found")

        data = request.get_json()

        # Validate that all required fields are present
        required_fields = ['name', 'course_code', 'is_active', 'start_date', 'end_date']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            api.abort(
                400, f"PUT requires all fields. Missing: {', '.join(missing_fields)}"
            )

        try:
            self._update_course_fields(course, data)

            # Validate dates
            if course.start_date >= course.end_date:
                raise ValueError("Start date must be before end date")

            # Update timestamp
            course.updated_on = datetime.now()

            db.session.commit()
            return course.to_dict()

        except (ValueError, IntegrityError) as e:
            db.session.rollback()
            api.abort(400, str(e))
        except Exception as e:
            db.session.rollback()
            api.abort(500, f"Failed to update course: {str(e)}")

    @api.doc('update_course_partial')
    @api.expect(course_update_model)  # Keep the optional fields model for PATCH
    @api.marshal_with(course_model)
    @require_auth
    def patch(self, course_id):
        """Update a course (partial update - only provided fields)"""
        user = session.get('user')
        user_id = user.get('sub')

        course = Course.query.filter_by(id=course_id, user_id=user_id).first()
        if not course:
            api.abort(404, "Course not found")

        data = request.get_json()

        if not data:
            api.abort(400, "No data provided for update")

        try:
            self._update_course_fields(course, data)

            # Only validate dates if both start_date and end_date are being updated
            # or if one is being updated and we need to check against existing value
            if ('start_date' in data or 'end_date' in data):
                if course.start_date >= course.end_date:
                    raise ValueError("Start date must be before end date")

            # Update timestamp
            course.updated_on = datetime.now()

            db.session.commit()
            return course.to_dict()

        except (ValueError, IntegrityError) as e:
            db.session.rollback()
            api.abort(400, str(e))
        except Exception as e:
            db.session.rollback()
            api.abort(500, f"Failed to update course: {str(e)}")


@api.route('/<int:course_id>/archive')
class CourseArchive(Resource):
    @api.doc('archive_course')
    @api.marshal_with(course_model)
    @require_auth
    def patch(self, course_id):  # Changed from PUT to PATCH
        """Archive a course (set is_active = False)"""
        user = session.get('user')
        user_id = user.get('sub')

        course = Course.query.filter_by(id=course_id, user_id=user_id).first()
        if not course:
            api.abort(404, "Course not found")

        try:
            course.is_active = False
            course.updated_on = datetime.now()
            db.session.commit()

            return course.to_dict()
        except Exception as e:
            db.session.rollback()
            api.abort(500, f"Failed to archive course: {str(e)}")


@api.route('/<int:course_id>/unarchive')
class CourseUnarchive(Resource):
    @api.doc('unarchive_course')
    @api.marshal_with(course_model)
    @require_auth
    def patch(self, course_id):  # Changed from PUT to PATCH
        """Unarchive a course (set is_active = True)"""
        user = session.get('user')
        user_id = user.get('sub')

        course = Course.query.filter_by(id=course_id, user_id=user_id).first()
        if not course:
            api.abort(404, "Course not found")

        try:
            course.is_active = True
            course.updated_on = datetime.now()
            db.session.commit()

            return course.to_dict()
        except Exception as e:
            db.session.rollback()
            api.abort(500, f"Failed to unarchive course: {str(e)}")
