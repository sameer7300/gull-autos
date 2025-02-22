#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Copy production env file
cp .env.prod .env

# Make sure the project directory is in PYTHONPATH
export PYTHONPATH=/opt/render/project/src:$PYTHONPATH

# Run Django commands
python manage.py collectstatic --noinput
python manage.py migrate
