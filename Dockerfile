# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=gull_autos.settings \
    DEBUG=False \
    ALLOWED_HOSTS="*" \
    PYTHONPATH=/app \
    WEB_CONCURRENCY=4 \
    PORT=10000

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

# Install gunicorn
RUN pip install gunicorn

# Copy requirements and project
COPY . .

# Configure health check
HEALTHCHECK --interval=30s --timeout=100s --start-period=30s --retries=10 \
    CMD curl -f http://localhost:$PORT/ || exit 1

# Use shell form to evaluate environment variables
CMD gunicorn gull_autos.wsgi:application --bind=0.0.0.0:$PORT
