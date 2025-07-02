# Gradeinator
**Gradeinator** is a tool that helps university professors efficiently manage and present student evaluations and grades.

## Gradeinator Backend

A Flask-based backend application for the Gradeinator project with Docker support and comprehensive testing.

## Prerequisites

- Docker and Docker Compose
- Git

## Quick Start

### 1. Environment Setup

Before running the application, you need to create a `.env` file in the root directory. Use the provided sample files as templates:

- For development: Copy `.env_development.sample` to `.env`
- For production: Copy `.env_production.sample` to `.env`

```bash
# For development
cp .env_development.sample .env

# For production  
cp .env_production.sample .env
```

Edit the `.env` file with your specific configuration values.

### 2. Running the Application

Start the application with Docker Compose:

```bash
# Development environment
docker-compose -f docker-compose.dev.yml up

# Production environment (when ready)
docker-compose -f docker-compose.prod.yml up
```

The application will be available at:
- Development: `http://localhost:5001`
- Production: `http://localhost:8000`

### 3. Running Tests

Run integration tests:

```bash
# Run integration tests (simple output)
docker-compose -f docker-compose.dev.yml run --rm app sh -c "pytest tests/integration/"

# Run integration tests (verbose output)
docker-compose -f docker-compose.dev.yml run --rm app sh -c "pytest tests/integration/ -v"

# Run all tests
docker-compose -f docker-compose.dev.yml run --rm app sh -c "pytest tests/ -v"

# Run tests with code quality checks
docker-compose -f docker-compose.dev.yml run --rm app sh -c "flake8 app/ tests/ && pytest tests/ -v"
```

## Project Structure
```
gradeinator-backend/
├── app/                    # Flask application package
│   ├── __init__.py        # Application factory
│   ├── config.py          # Configuration classes
│   ├── models/            # Database models
│   │   ├── __init__.py
│   │   └── user.py        # User model
│   ├── routes/            # API routes
│   │   ├── __init__.py
│   │   └── auth.py        # Authentication routes
│   └── utils/             # Utility functions
│       ├── __init__.py
│       └── cognito.py     # AWS Cognito utilities
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── conftest.py        # Global test fixtures
│   ├── unit/              # Unit tests
│   │   ├── __init__.py
│   │   ├── models/        # Model unit tests
│   │   │   └── __init__.py
│   │   ├── services/      # Service unit tests
│   │   │   └── __init__.py
│   │   └── utils/         # Utility unit tests
│   │       └── __init__.py
│   ├── integration/       # Integration tests
│   │   ├── __init__.py
│   │   └── test_app_endpoints.py  # API endpoint tests
│   └── fixtures/          # Test fixtures
│       └── __init__.py
├── requirements/          # Requirements files
│   ├── base.txt          # Base dependencies
│   ├── dev.txt           # Development dependencies
│   └── prod.txt          # Production dependencies
├── scripts/               # Deployment scripts
│   └── entrypoint.sh     # Docker entrypoint script
├── .env_development.sample # Development environment template
├── .env_production.sample  # Production environment template
├── .flake8               # Flake8 configuration
├── .gitignore           # Git ignore rules
├── app.py               # Application entry point
├── docker-compose.dev.yml # Development Docker setup
├── docker-compose.prod.yml# Production Docker setup
├── dockerfile           # Docker image definition
├── LICENSE.md          # License
├── pytest.ini         # Pytest configuration
├── README.md          # This file
└── run_tests.py       # Test runner script
```

## License
[![License: CC BY-NC 4.0](https://licensebuttons.net/l/by-nc/4.0/80x15.png)](https://creativecommons.org/licenses/by-nc/4.0/)

Copyright (c) 2025 Gerardo Franco D. 

This project (Gradeinator) is licensed under the
[Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/).

You can view the full legal code of the license here:
[https://creativecommons.org/licenses/by-nc/4.0/legalcode](https://creativecommons.org/licenses/by-nc/4.0/legalcode)
