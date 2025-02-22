#!/bin/sh
# Ensure PORT has a value
if [ -z "$PORT" ]; then
    export PORT=8000
fi

# Start Gunicorn with the specified port
exec gunicorn gull_autos.wsgi:application --bind "0.0.0.0:${PORT}"
