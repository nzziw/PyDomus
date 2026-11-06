#!/bin/sh
set -e   # stop on the first error

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn pydomus.wsgi:application --bind 0.0.0.0:8000 --workers 3
