import os
from flask import Flask, redirect, url_for, jsonify
from flask_restx import Api
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import config
from app.utils.oauth import init_oauth

# Initialize database and migration
db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name=os.getenv('FLASK_ENV', 'default')):
    """
    Application factory function.
    Configures and returns the Flask application.
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize database
    db.init_app(app)

    # Initialize migrations
    migrate.init_app(app, db)

    # Import models here to ensure they are registered with SQLAlchemy
    from app.models import Course

    # --- Environment-Specific Configurations ---
    is_production = app.config['FLASK_ENV'] == 'production'

    # 1. Configure CORS based on the environment
    if is_production:
        # In production, only allow your specific frontend domain.
        # Replace this with your actual frontend URL.
        origins = ['https://www.your-production-frontend.com']
    else:
        # In development, allow more flexible origins for local testing.
        # This typically includes your local frontend development server.
        origins = ['http://localhost:3000', 'http://127.0.0.1:3000']

    CORS(
        app,
        origins=origins,
        supports_credentials=True,
        # Expose the 'Location' header to allow frontend to see redirect URLs
        expose_headers=['Location'],
    )

    # 2. Configure Session Cookies for Security
    # In production, cookies must be secure.
    app.config.update(
        SESSION_COOKIE_SECURE=is_production,
        SESSION_COOKIE_HTTPONLY=True,
        # Use 'Lax' for a good balance of security and usability with OIDC redirects.
        # 'None' requires Secure=True, which is handled by is_production.
        SESSION_COOKIE_SAMESITE='Lax'
    )

    # 3. Initialize OAuth Client
    # Attach the configured oauth object to the app context
    oauth = init_oauth(app)
    app.oauth = oauth

    # Add a simple root route BEFORE Flask-RESTX
    @app.route('/')
    def index():
        # This is useful for the logout redirect and for simple health checks.
        return jsonify({"message": "API is running"})

    # 4. Initialize Flask-RESTX API (after root route)
    api = Api(
        app,
        version='1.0',
        title='Gradeinator API',
        description='API for the Gradeinator application, including authentication.',
        doc='/docs/',
        prefix='/api',  # Add prefix to avoid root route conflict
    )

    # 5. Register API Namespaces
    from app.routes.general import api as general_ns
    from app.routes.auth import api as auth_ns
    from app.routes.courses import api as courses_ns

    api.add_namespace(general_ns, path='/general')
    api.add_namespace(auth_ns, path='/auth')
    api.add_namespace(courses_ns, path='/courses')

    # Register CLI commands
    from app import cli
    cli.init_app(app)

    return app
