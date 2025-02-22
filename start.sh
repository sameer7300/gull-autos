#!/usr/bin/env bash
# exit on error
set -o errexit

cd /opt/render/project/src
export PYTHONPATH=/opt/render/project/src
exec gunicorn gull_autos.wsgi:application --bind 0.0.0.0:$PORT --log-file -
