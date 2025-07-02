from flask_restx import Namespace, Resource, fields
from flask import current_app
import psutil
from datetime import datetime
from sqlalchemy import text

# Create namespace for general endpoints
api = Namespace('general', description='General API operations')

# Define response models
hello_response_model = api.model('HelloResponse', {
    'message': fields.String(description='API status message'),
    'environment': fields.String(description='Current environment'),
    'debug': fields.Boolean(description='Debug mode status')
})

health_response_model = api.model('HealthResponse', {
    'status': fields.String(description='Health status'),
    'timestamp': fields.DateTime(description='Check timestamp'),
    'version': fields.String(description='API version'),
    'environment': fields.String(description='Current environment'),
    'database': fields.String(description='Database connection status'),
    'uptime': fields.String(description='Application uptime'),
    'memory_usage': fields.Raw(description='Memory usage statistics')
})


@api.route('/')
class Hello(Resource):
    @api.doc('hello_world')
    @api.marshal_with(hello_response_model)
    def get(self):
        """Hello World endpoint - API welcome message"""
        return {
            'message': 'Gradeinator API is running!',
            'environment': current_app.config.get('FLASK_ENV', 'unknown'),
            'debug': current_app.config.get('DEBUG', False)
        }


@api.route('/health')
class HealthCheck(Resource):
    @api.doc('health_check')
    @api.marshal_with(health_response_model)
    def get(self):
        """Health check endpoint - API status and diagnostics"""
        from app import db

        # Check database connection
        try:
            db.session.execute(text('SELECT 1'))
            db_status = 'healthy'
        except Exception as e:
            db_status = f'unhealthy: {str(e)}'

        # Get memory usage
        try:
            memory_info = psutil.virtual_memory()
            memory_usage = {
                'total': f"{memory_info.total / (1024**3):.2f} GB",
                'available': f"{memory_info.available / (1024**3):.2f} GB",
                'percent': f"{memory_info.percent}%"
            }
        except Exception:
            memory_usage = {'error': 'Unable to retrieve memory info'}

        # Calculate uptime
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = datetime.now().timestamp() - boot_time
            uptime = f"{uptime_seconds / 3600:.1f} hours"
        except Exception:
            uptime = "unknown"

        return {
            'status': 'healthy' if db_status == 'healthy' else 'degraded',
            'timestamp': datetime.utcnow(),
            'version': '1.0',
            'environment': current_app.config.get('FLASK_ENV', 'unknown'),
            'database': db_status,
            'uptime': uptime,
            'memory_usage': memory_usage
        }
