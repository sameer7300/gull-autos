# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=gull_autos.settings \
    DEBUG=False \
    ALLOWED_HOSTS=".railway.app,localhost,127.0.0.1" \
    PYTHONPATH=/app \
    PORT=10000 \
    WEB_CONCURRENCY=4

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    gcc \
    python3-dev \
    libpq-dev \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install basic tools
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements files
COPY requirements-base.txt ./

# Install base dependencies first
RUN pip install --no-cache-dir -r requirements-base.txt

# Copy project
COPY . .

# Create static and media directories
RUN mkdir -p /app/staticfiles /app/media

# Collect static files
RUN python manage.py collectstatic --noinput --clear

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Use shell form for CMD to ensure environment variables are expanded
CMD sh /app/entrypoint.sh

# Configure health check to use exact port
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f "http://localhost:10000/health/" || exit 1
