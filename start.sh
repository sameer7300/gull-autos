#!/bin/bash
set -e

# Default port
DEFAULT_PORT=8000

# Get port from environment or use default
PORT="${PORT:-$DEFAULT_PORT}"

# Run migrations
python manage.py migrate --noinput

# Start Gunicorn
exec gunicorn \
    --bind "0.0.0.0:${PORT}" \
    --workers 2 \
    --threads 4 \
    --timeout 0 \
    --access-logfile - \
    --error-logfile - \
    gull_autos.wsgi:application
