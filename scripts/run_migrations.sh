#!/bin/bash

# Wait for database to be ready (simplified approach)
echo "Waiting for database..."
sleep 10

echo "Database should be ready!"

# Check if migrations directory exists
if [ ! -d "migrations" ]; then
    echo "Initializing migrations..."
    flask db init
fi

# Check if there are any migration files
if [ -z "$(ls -A migrations/versions 2>/dev/null)" ]; then
    echo "Creating initial migration..."
    flask db migrate -m "Initial migration with Course model"
fi

# Apply migrations
echo "Applying migrations..."
flask db upgrade

echo "Migrations completed!" 