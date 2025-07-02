from flask import Flask
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy

from app.config import config

# Initialize extensions
db = SQLAlchemy()


def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)

    # Determine configuration
    if config_name is None:
        import os
        config_name = os.environ.get('FLASK_ENV', 'development')

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize extensions with app
    db.init_app(app)

    # Initialize Flask-RESTX
    api = Api(
        app,
        title="Gradeinator API",
        version="1.0",
        description="A comprehensive API for grade management",
        doc="/docs/"
    )

    # Register namespaces
    from app.routes.auth import api as auth_ns
    from app.routes.general import api as general_ns

    # Add general endpoints at root level (no path prefix)
    api.add_namespace(general_ns, path="")

    # Add auth endpoints under /auth
    api.add_namespace(auth_ns, path="/auth")

    # Create database tables
    with app.app_context():
        db.create_all()

    # Basic route for testing
    @app.route('/')
    def hello():
        return {
            "message": "Gradeinator API is running!",
            "environment": app.config['FLASK_ENV'],
            "debug": app.config['DEBUG']
        }

    @app.route('/health')
    def health_check():
        return {"status": "healthy", "environment": app.config['FLASK_ENV']}

    return app
