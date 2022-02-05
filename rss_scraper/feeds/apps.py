from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class FeedsConfig(AppConfig):
    name = "rss_scraper.feeds"
    verbose_name = _("Feeds")

    def ready(self):
        try:
            import rss_scraper.users.signals  # noqa F401
        except ImportError:
            pass
