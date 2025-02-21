#!/bin/sh
# Ensure PORT is set
if [ -z "$PORT" ]; then
    export PORT=8000
fi

# Run migrations
python manage.py migrate --noinput

# Start Gunicorn with the PORT from Railway
exec gunicorn gull_autos.wsgi:application --bind "0.0.0.0:$PORT" --workers 2 --threads 4 --timeout 0
