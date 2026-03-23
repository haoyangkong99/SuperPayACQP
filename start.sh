#!/bin/bash
set -e

# Navigate to the Django project directory
cd SuperPayACQP

# Run migrations
python manage.py migrate

# Start background task processor in background
python manage.py process_tasks --duration=0 &

# Start Gunicorn web server (foreground process)
exec gunicorn SuperPayACQP.wsgi:application --bind 0.0.0.0:${PORT:-8000}
