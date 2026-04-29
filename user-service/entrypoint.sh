#!/bin/bash
set -e

echo "Waiting for database..."
for i in {1..30}; do
    if python manage.py migrate --noinput; then
        echo "Database migrations successful!"
        break
    fi
    echo "Attempt $i/30: database not ready, retrying..."
    sleep 2
done

echo "Starting user-service..."
python manage.py runserver 0.0.0.0:8000
