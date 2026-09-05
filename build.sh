#!/usr/bin/env bash
# Exit on error
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput --clear
python manage.py migrate


# Initialize Site model (SITE_ID=1) and pre-seed catalog data
python manage.py shell -c "
from django.contrib.sites.models import Site
site, _ = Site.objects.get_or_create(id=1, defaults={'domain': 'om-super-mart.onrender.com', 'name': 'Om Super Mart'})
if site.name != 'Om Super Mart':
    site.domain = 'om-super-mart.onrender.com'
    site.name = 'Om Super Mart'
    site.save()

try:
    from products.seed import seed_all_groceries
    seed_all_groceries()
    print('Om Super Mart catalog pre-seeded successfully.')
except Exception as e:
    print('Catalog seeding note:', e)
"
