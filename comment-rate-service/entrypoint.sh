#!/bin/bash
set -e

echo "Waiting for database..."
migrate_ok=0
for i in {1..30}; do
    set +e
    python manage.py migrate --noinput 2>&1
    rc=$?
    set -e
    if [ $rc -eq 0 ]; then
        echo "Database migrations successful!"
        migrate_ok=1
        break
    else
        echo "Attempt $i/30: Database not ready yet, waiting..."
        sleep 2
    fi
done

if [ $migrate_ok -ne 1 ]; then
    echo "Migrations failed after 30 attempts."
    exit 1
fi

if [ "${COMMENT_RATE_AUTO_SEED:-0}" = "1" ]; then
    echo "Seeding demo reviews..."
    python manage.py shell -c "from app.seeds import run; run()" || echo "Seed skipped (non-fatal)"
else
    echo "Skipping demo review seed (COMMENT_RATE_AUTO_SEED != 1)"
fi

echo "Starting comment-rate-service..."
python manage.py runserver 0.0.0.0:8000
