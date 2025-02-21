#!/bin/bash
# Install dependencies
pip install -r requirements-base.txt

# Run migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput --clear
