#!/bin/bash

set -e

echo "Waiting for database..."
# For SQLite, no wait needed, but keeping structure for future PostgreSQL migration

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear || true

echo "Starting server..."
exec "$@"

