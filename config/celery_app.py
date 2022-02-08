"""
Set the default Django settings module for the 'celery' program.
"""
import os

from celery import Celery

from config.celery_beat import register_system_wide_periodic_tasks

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("rss_scraper")
register_system_wide_periodic_tasks(app)

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
