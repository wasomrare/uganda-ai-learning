#!/bin/bash
set -e

echo "==== Uganda Primary AI Learning System ===="
echo "Waiting for database..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.5
done
echo "Database is ready!"

echo "Waiting for Redis..."
while ! nc -z redis 6379; do
  sleep 0.5
done
echo "Redis is ready!"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Creating super admin if not exists..."
python manage.py create_superadmin || true

echo "Loading curriculum seed data..."
python manage.py load_curriculum || true

echo "Starting server..."
exec "$@"
