#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "DEBUG=False" > .env
echo "ALLOWED_HOSTS=.onrender.com" >> .env
echo "DJANGO_SETTINGS_MODULE=gull_autos.settings" >> .env
echo "PYTHONPATH=/opt/render/project/src" >> .env

# Make sure the project directory is in PYTHONPATH
export PYTHONPATH=/opt/render/project/src:$PYTHONPATH

# Run Django commands
python manage.py collectstatic --noinput
python manage.py migrate
