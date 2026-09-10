from django.apps import AppConfig
from django.db.models.signals import post_migrate
import os


def configure_social_auth_and_site(sender, **kwargs):
    try:
        from django.contrib.sites.models import Site
        site, _ = Site.objects.get_or_create(
            id=1,
            defaults={
                "domain": "om-super-mart.onrender.com",
                "name": "Om Super Mart",
            }
        )
        if site.domain in ["example.com", "localhost:8000"]:
            site.domain = "om-super-mart.onrender.com"
            site.name = "Om Super Mart"
            site.save()

        from allauth.socialaccount.models import SocialApp
        client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
        secret = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()

        google_apps = SocialApp.objects.filter(provider="google")
        if not google_apps.exists():
            if client_id and secret:
                app = SocialApp.objects.create(
                    provider="google",
                    name="Google (Om Super Mart)",
                    client_id=client_id,
                    secret=secret,
                )
                app.sites.add(site)
        else:
            app = google_apps.first()
            if not app.sites.filter(id=site.id).exists():
                app.sites.add(site)
            if client_id and app.client_id != client_id:
                app.client_id = client_id
                app.save()
            if secret and app.secret != secret:
                app.secret = secret
                app.save()
    except Exception:
        # Ignore during early migrations or table-creation phases
        pass


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'Customer Accounts'

    def ready(self):
        post_migrate.connect(configure_social_auth_and_site, sender=self)
