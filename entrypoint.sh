#!/bin/sh

# Wait for the database to be ready
echo "Waiting for postgres..."

# The `pg_isready` command checks the connection. We loop until it succeeds.
# The variables are read from the environment set in docker-compose.yml
while ! pg_isready -h "$DB_HOST" -p "5432" -U "$DB_USER" > /dev/null 2> /dev/null; do
  sleep 1
done

echo "PostgreSQL started"

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Create superuser (will only run on the first start)
echo "Creating superuser..."
python manage.py createsuperuser --noinput || true

echo "Create demo data..."
python manage.py generate_demo

# Start Gunicorn process in the background
echo "Starting Gunicorn..."
gunicorn newwork_backend.wsgi:application --bind 0.0.0.0:8000 &

# Start Nginx in the foreground
echo "Starting Nginx..."
nginx -g 'daemon off;'