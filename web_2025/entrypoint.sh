#!/usr/bin/env bash
set -e

: "${DB_HOST:=db}"
: "${DB_PORT:=5432}"
: "${DB_USER:=postgres}"

echo "Waiting for Postgres at $DB_HOST:$DB_PORT ..."

until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" >/dev/null 2>&1; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - continuing"

# Выполнить миграции (по умолчанию true)
if [ "${DJANGO_MIGRATE:-true}" != "false" ]; then
  echo "Run migrations..."
  python manage.py migrate --noinput
fi

# На всякий случай (опционально) collectstatic при старте
if [ "${DJANGO_COLLECTSTATIC_ON_START:-false}" = "true" ]; then
  echo "Collect static..."
  python manage.py collectstatic --noinput
fi

exec "$@"
