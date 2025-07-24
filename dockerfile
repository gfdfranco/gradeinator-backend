FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies including postgresql-client
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/dev.txt

# Copy application code
COPY . .

# Make sure scripts have execute permissions (more explicit)
RUN chmod 755 scripts/entrypoint.sh scripts/run_migrations.sh

# Set entrypoint using bash explicitly
ENTRYPOINT ["bash", "./scripts/entrypoint.sh"]

# Default command
CMD ["python", "app.py"]