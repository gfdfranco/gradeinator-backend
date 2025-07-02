from flask import current_app, request
from flask_restx import Namespace, Resource, fields

from app import db
from app.models.user import User

# Create namespace
api = Namespace('auth', description='Authentication related operations')

# Define models for documentation
user_model = api.model('User', {
    'id': fields.Integer(required=True, description='User ID'),
    'username': fields.String(required=True, description='Username'),
    'email': fields.String(required=True, description='Email address'),
    'created_at': fields.DateTime(description='Creation timestamp')
})

user_input_model = api.model('UserInput', {
    'username': fields.String(required=True, description='Username'),
    'email': fields.String(required=True, description='Email address')
})

test_response_model = api.model('TestResponse', {
    'message': fields.String(description='Response message'),
    'cognito_region': fields.String(description='AWS Cognito region'),
    'environment': fields.String(description='Current environment')
})

users_response_model = api.model('UsersResponse', {
    'users': fields.List(fields.Nested(user_model)),
    'count': fields.Integer(description='Number of users')
})


@api.route('/test')
class AuthTest(Resource):
    @api.doc('test_auth')
    @api.marshal_with(test_response_model)
    def get(self):
        """Test route to verify auth is working"""
        return {
            "message": "Auth blueprint is working!",
            "cognito_region": current_app.config.get('AWS_COGNITO_REGION'),
            "environment": current_app.config.get('FLASK_ENV')
        }


@api.route('/users')
class UserList(Resource):
    @api.doc('list_users')
    @api.marshal_with(users_response_model)
    def get(self):
        """Get all users"""
        try:
            users = User.query.all()
            return {
                "users": [user.to_dict() for user in users],
                "count": len(users)
            }
        except Exception as e:
            api.abort(500, f"Database error: {str(e)}")

    @api.doc('create_user')
    @api.expect(user_input_model)
    @api.marshal_with(user_model, code=201)
    def post(self):
        """Create a new user"""
        try:
            data = api.payload
            user = User(
                username=data['username'],
                email=data['email']
            )
            db.session.add(user)
            db.session.commit()
            return user.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            api.abort(500, f"Database error: {str(e)}")
