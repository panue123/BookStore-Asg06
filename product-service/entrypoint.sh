#!/bin/sh
set -e
python manage.py migrate --noinput
python manage.py shell -c "
from modules.catalog.seeds.categories_seed import run as seed_cats
from modules.catalog.seeds.products_seed import run as seed_prods
print('=== Seeding categories (multi-domain) ===')
seed_cats()
print('=== Seeding products (multi-domain) ===')
seed_prods()
print('=== Seed complete ===')"
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2
