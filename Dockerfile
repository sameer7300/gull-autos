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

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install Python dependencies in stages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt || \
    (pip install --no-cache-dir -r requirements.txt 2>&1 | tee pip_error.log && \
    echo "Error log:" && cat pip_error.log && exit 1)

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run gunicorn
CMD gunicorn --bind 0.0.0.0:$PORT gull_autos.wsgi:application

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl --fail http://localhost:$PORT || exit 1
