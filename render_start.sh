#!/usr/bin/env bash
set -o errexit

echo "📦 Running database migrations..."
python manage.py migrate --noinput

echo "👤 Creating superuser (if needed)..."
python manage.py createsuperuser --noinput || true

echo "🚀 Starting Gunicorn..."
gunicorn backend.wsgi:application