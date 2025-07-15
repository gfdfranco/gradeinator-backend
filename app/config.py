import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class"""
    # Flask Configuration
    SECRET_KEY = os.environ.get('APP_SECRET_KEY') or 'dev-fallback-secret-key'
    FLASK_ENV = os.environ.get('FLASK_ENV') or 'development'
    DEBUG = os.environ.get('FLASK_DEBUG', '0').lower() in ['true', '1', 'yes']

    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # AWS Cognito Configuration (OAuth only)
    AWS_COGNITO_REGION = os.environ.get('AWS_COGNITO_REGION')
    AWS_COGNITO_USERPOOL_ID = os.environ.get('AWS_COGNITO_USERPOOL_ID')
    AWS_COGNITO_APP_CLIENT_ID = os.environ.get('AWS_COGNITO_APP_CLIENT_ID')
    AWS_COGNITO_APP_CLIENT_SECRET = os.environ.get('AWS_COGNITO_APP_CLIENT_SECRET')
    AWS_COGNITO_DOMAIN = os.environ.get('AWS_COGNITO_DOMAIN')

    # Flask-RESTX Configuration
    RESTX_MASK_SWAGGER = False
    RESTX_VALIDATE = True


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    SECRET_KEY = 'test-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    AWS_COGNITO_DOMAIN = 'test.auth.us-east-1.amazoncognito.com'
    AWS_COGNITO_APP_CLIENT_ID = 'test-client-id'
    AWS_COGNITO_APP_CLIENT_SECRET = 'test-secret'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
