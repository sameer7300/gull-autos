# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 8000
ENV DJANGO_SETTINGS_MODULE gull_autos.settings
ENV DEBUG False
ENV ALLOWED_HOSTS=".railway.app,localhost,127.0.0.1"
ENV PYTHONPATH=/app

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
COPY requirements-base.txt requirements.txt ./

# Install base dependencies first
RUN pip install --no-cache-dir -r requirements-base.txt

# Install the rest of the dependencies
RUN pip install --no-cache-dir -r requirements.txt || true

# Copy project
COPY . .

# Create static and media directories
RUN mkdir -p /app/staticfiles /app/media

# Collect static files
RUN python manage.py collectstatic --noinput --clear

# Create startup script
RUN echo '#!/bin/bash\n\
python manage.py migrate --noinput\n\
gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 0 gull_autos.wsgi:application' > /app/start.sh \
    && chmod +x /app/start.sh

# Run startup script
CMD ["/app/start.sh"]

# Configure health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:$PORT/ || exit 1
