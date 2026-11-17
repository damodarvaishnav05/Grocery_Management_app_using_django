import os
import logging
from django.shortcuts import redirect
from django.contrib import messages
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

logger = logging.getLogger(__name__)


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom social account adapter ensuring seamless login across mobile and desktop.
    - Deduplicates social apps between settings.py and the database to prevent MultipleObjectsReturned.
    - Gracefully handles missing credentials without crashing with 500 server errors.
    - Gracefully catches authentication errors and guides the user.
    """

    def list_apps(self, request, provider=None, client_id=None):
        apps = super().list_apps(request, provider=provider, client_id=client_id)
        seen = set()
        deduped = []
        for app in apps:
            key = (getattr(app, "provider", None), getattr(app, "client_id", None))
            if key not in seen:
                seen.add(key)
                deduped.append(app)
        return deduped

    def get_app(self, request, provider, client_id=None):
        from allauth.socialaccount.models import SocialApp
        try:
            return super().get_app(request, provider=provider, client_id=client_id)
        except SocialApp.DoesNotExist:
            logger.warning(f"SocialApp for provider '{provider}' is not configured in database or environment.")
            cid = os.getenv("GOOGLE_CLIENT_ID", "").strip()
            sec = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
            if cid and sec:
                app, _ = SocialApp.objects.get_or_create(
                    provider=provider,
                    defaults={
                        "name": f"{provider.title()} (Om Super Mart)",
                        "client_id": cid,
                        "secret": sec,
                    }
                )
                return app
            # If not configured in environment, create a temporary placeholder to prevent 500 crash
            placeholder = SocialApp(
                provider=provider,
                name=f"{provider.title()} (Om Super Mart)",
                client_id="not-configured",
                secret="not-configured"
            )
            return placeholder

    def authentication_error(
        self,
        request,
        provider_id,
        error=None,
        exception=None,
        extra_context=None,
    ):
        logger.warning(
            f"Social account authentication error for provider {provider_id}: error={error}, exception={exception}"
        )
        messages.warning(
            request,
            "Google sign-in could not be completed. Please log in with your email or username below."
        )
        return redirect("accounts:login")
