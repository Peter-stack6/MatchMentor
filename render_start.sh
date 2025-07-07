echo "🚀 Starting Gunicorn..."
gunicorn backend.wsgi:application
