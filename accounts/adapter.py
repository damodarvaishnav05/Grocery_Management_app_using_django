from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
import logging

logger = logging.getLogger(__name__)


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom social account adapter ensuring seamless login across all environments.
    - Deduplicates social apps between settings.py and the database to prevent MultipleObjectsReturned.
    - Gracefully handles authentication and login redirects.
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
        return super().authentication_error(
            request,
            provider_id,
            error=error,
            exception=exception,
            extra_context=extra_context,
        )

