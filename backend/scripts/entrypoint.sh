#!/bin/bash

echo "==== Uganda Primary AI Learning System ===="
echo "DATABASE_URL set: $([ -n "$DATABASE_URL" ] && echo YES || echo NO)"
echo "DATABASE_PUBLIC_URL set: $([ -n "$DATABASE_PUBLIC_URL" ] && echo YES || echo NO)"

# Parse DB host/port for health check
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
echo "Waiting for DB at $DB_HOST:$DB_PORT ..."
for i in $(seq 1 30); do
  nc -z "$DB_HOST" "$DB_PORT" 2>/dev/null && echo "DB is ready!" && break
  echo "  attempt $i/30 ..."
  sleep 2
done

# Redis — optional
if [ -n "$REDIS_URL" ] || [ -n "$REDIS_HOST" ]; then
  REDIS_HOST_CLEAN="${REDIS_HOST:-redis}"
  REDIS_PORT_CLEAN="${REDIS_PORT:-6379}"
  for i in $(seq 1 10); do
    nc -z "$REDIS_HOST_CLEAN" "$REDIS_PORT_CLEAN" 2>/dev/null && echo "Redis ready!" && break
    sleep 2
  done
fi

echo "--- Running migrations ---"
python manage.py migrate --noinput --verbosity 1
echo "--- Migrations done (exit $?) ---"

echo "--- Collecting static files ---"
python manage.py collectstatic --noinput --clear || echo "collectstatic warning — continuing"

echo "--- Creating admin user ---"
python << 'PYEOF'
import os, sys, traceback
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
try:
    import django
    django.setup()
    print("Django setup OK")
    from apps.users.models import User
    uname = os.environ.get('ADMIN_USERNAME', 'Evinia')
    pwd   = os.environ.get('ADMIN_PASSWORD', 'johnson@angel')
    email = os.environ.get('ADMIN_EMAIL', 'twiinarides@gmail.com')
    print(f"Target admin username: {uname}")
    u, created = User.objects.get_or_create(username=uname)
    u.email = email
    u.first_name = 'Evinia'
    u.last_name = 'Administrator'
    u.role = 'super_admin'
    u.is_staff = True
    u.is_superuser = True
    u.is_active = True
    u.is_verified = True
    u.force_password_change = False
    u.set_password(pwd)
    u.save()
    total = User.objects.count()
    print(f"[OK] Admin {'created' if created else 'updated'}: {uname}  (total users: {total})")
except Exception:
    print("[ERROR] Admin creation failed with exception:")
    traceback.print_exc()
PYEOF

echo "--- Starting server ---"
exec "$@"
