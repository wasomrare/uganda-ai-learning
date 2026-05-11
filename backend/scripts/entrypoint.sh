#!/bin/bash
set -e

echo "==== Uganda Primary AI Learning System ===="

# Wait for PostgreSQL
# Parse host/port from DATABASE_URL if DB_HOST not explicitly set
if [ -z "$DB_HOST" ] && [ -n "$DATABASE_URL" ]; then
  DB_HOST=$(echo "$DATABASE_URL" | sed -E 's|.*@([^:/]+)[:/].*|\1|')
  DB_PORT=$(echo "$DATABASE_URL" | sed -E 's|.*@[^:]+:([0-9]+)/.*|\1|')
fi
if [ -z "$DB_HOST" ] && [ -n "$DATABASE_PUBLIC_URL" ]; then
  DB_HOST=$(echo "$DATABASE_PUBLIC_URL" | sed -E 's|.*@([^:/]+)[:/].*|\1|')
  DB_PORT=$(echo "$DATABASE_PUBLIC_URL" | sed -E 's|.*@[^:]+:([0-9]+)/.*|\1|')
fi
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
echo "Waiting for database at $DB_HOST:$DB_PORT ..."
for i in $(seq 1 30); do
  nc -z "$DB_HOST" "$DB_PORT" && break
  echo "  attempt $i/30 — retrying in 2s..."
  sleep 2
done
echo "Database is ready!"

# Wait for Redis only if REDIS_URL or REDIS_HOST is set
if [ -n "$REDIS_URL" ] || [ -n "$REDIS_HOST" ]; then
  REDIS_HOST_CLEAN="${REDIS_HOST:-redis}"
  REDIS_PORT_CLEAN="${REDIS_PORT:-6379}"
  echo "Waiting for Redis at $REDIS_HOST_CLEAN:$REDIS_PORT_CLEAN ..."
  for i in $(seq 1 15); do
    nc -z "$REDIS_HOST_CLEAN" "$REDIS_PORT_CLEAN" && break
    echo "  attempt $i/15 — retrying in 2s..."
    sleep 2
  done
  echo "Redis is ready!"
else
  echo "Redis not configured — skipping."
fi

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
