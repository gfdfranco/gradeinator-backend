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
    POSTGRES_DB = os.environ.get('POSTGRES_DB')
    POSTGRES_USER = os.environ.get('POSTGRES_USER')
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
    DATABASE_URL = os.environ.get('DATABASE_URL')

    # Define a boolean variable for the presence of all required credentials
    has_postgres_credentials = all(
        [POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB]
    )
    # If DATABASE_URL is not provided, construct it
    if not DATABASE_URL and has_postgres_credentials:
        DATABASE_URL = (
            f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
            f"@db:5432/{POSTGRES_DB}"
        )
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # AWS Cognito Configuration
    AWS_COGNITO_REGION = os.environ.get('AWS_COGNITO_REGION')
    AWS_COGNITO_USERPOOL_ID = os.environ.get('AWS_COGNITO_USERPOOL_ID')
    AWS_COGNITO_APP_CLIENT_ID = os.environ.get('AWS_COGNITO_APP_CLIENT_ID')

    # Flask-RESTX Configuration
    RESTX_MASK_SWAGGER = False
    RESTX_VALIDATE = True
    SWAGGER_UI_DOC_EXPANSION = 'list'
    SWAGGER_UI_OPERATION_ID = True
    SWAGGER_UI_REQUEST_DURATION = True


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
    FLASK_ENV = 'testing'
    # Use SQLite for testing (faster and no external dependencies)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    # Override other settings for testing
    SECRET_KEY = 'testing-secret-key'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
