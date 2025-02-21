# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 8000

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

# Collect static files
RUN python manage.py collectstatic --noinput

# Run gunicorn
CMD gunicorn --bind 0.0.0.0:$PORT gull_autos.wsgi:application

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl --fail http://localhost:$PORT || exit 1
