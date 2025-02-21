#!/bin/bash
set -e

# Install dependencies
pip install --no-cache-dir -r requirements-base.txt

# Run migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput --clear
