# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements directory into the container
COPY requirements/ requirements/

# Copy the entrypoint script
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy the rest of the application code into the container at /app
COPY . .

# Expose port 5000 for the Flask application
EXPOSE 5000

# Set the entrypoint script as the default command
ENTRYPOINT ["/entrypoint.sh"]