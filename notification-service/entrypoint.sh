#!/bin/bash
set -e

for i in {1..30}; do
    if python manage.py migrate --noinput; then
        break
    fi
    echo "Waiting for db... attempt $i/30"
    sleep 2
done

python manage.py runserver 0.0.0.0:8000
