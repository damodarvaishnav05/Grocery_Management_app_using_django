#!/usr/bin/env bash
# Exit on error
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput --clear
python manage.py migrate


# Initialize Site model (SITE_ID=1) and pre-seed catalog data
python manage.py shell -c "
from django.contrib.sites.models import Site
import os
render_host = os.getenv('RENDER_EXTERNAL_HOSTNAME', '').strip()
target_domain = render_host if render_host else 'om-super-mart.onrender.com'
site, _ = Site.objects.get_or_create(id=1, defaults={'domain': target_domain, 'name': 'Om Super Mart'})
if site.domain != target_domain or site.name != 'Om Super Mart':
    site.domain = target_domain
    site.name = 'Om Super Mart'
    site.save()

try:
    from allauth.socialaccount.models import SocialApp
    client_id = os.getenv('GOOGLE_CLIENT_ID', '').strip()
    secret = os.getenv('GOOGLE_CLIENT_SECRET', '').strip()
    if client_id and secret:
        app, created = SocialApp.objects.get_or_create(provider='google', defaults={'name': 'Google (Om Super Mart)', 'client_id': client_id, 'secret': secret})
        if not created:
            if client_id and app.client_id != client_id:
                app.client_id = client_id
            if secret and app.secret != secret:
                app.secret = secret
            app.save()
        if not app.sites.filter(id=site.id).exists():
            app.sites.add(site)
        print('SocialApp configured successfully for site:', site.domain)
except Exception as e:
    print('SocialApp init note:', e)

try:
    from products.seed import seed_all_groceries
    seed_all_groceries()
    print('Om Super Mart catalog pre-seeded successfully.')
except Exception as e:
    print('Catalog seeding note:', e)
"
