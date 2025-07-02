#!/bin/bash
set -e

# Function to install requirements based on environment
install_requirements() {
    local env=$1
    
    case $env in
        "development"|"dev")
            echo "Installing development requirements..."
            pip install --no-cache-dir -r requirements/dev.txt
            ;;
        "production"|"prod")
            echo "Installing production requirements..."
            pip install --no-cache-dir -r requirements/prod.txt
            ;;
        *)
            echo "Unknown environment: $env. Installing development requirements by default..."
            pip install --no-cache-dir -r requirements/dev.txt
            ;;
    esac
}

# Function to wait for database to be ready
wait_for_db() {
    echo "Waiting for database to be ready..."
    while ! nc -z db 5432; do
        sleep 1
    done
    echo "Database is ready!"
}

# Main execution
echo "Starting application with environment: ${FLASK_ENV:-development}"

# Install requirements based on environment
install_requirements "${FLASK_ENV:-development}"

# Wait for database in production
if [ "${FLASK_ENV:-development}" = "production" ] || [ "${FLASK_ENV:-development}" = "prod" ]; then
    wait_for_db
fi

# Execute the command passed to the container
# This allows docker-compose to override the command
exec "$@" 