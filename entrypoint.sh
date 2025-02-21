#!/bin/sh
# Run migrations
python manage.py migrate --noinput

# Start Gunicorn with Railway's exact configuration
exec gunicorn gull_autos.wsgi:application \
    --bind "0.0.0.0:10000" \
    --workers "$WEB_CONCURRENCY" \
    --threads 4 \
    --timeout 0 \
    --access-logfile - \
    --error-logfile -
