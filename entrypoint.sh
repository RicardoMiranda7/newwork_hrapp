#!/bin/sh

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Start Gunicorn process in the background
echo "Starting Gunicorn..."
gunicorn newwork_backend.wsgi:application --bind 0.0.0.0:8000 &

# Start Nginx in the foreground
echo "Starting Nginx..."
nginx -g 'daemon off;'