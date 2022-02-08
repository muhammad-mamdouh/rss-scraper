from celery.schedules import crontab


def register_system_wide_periodic_tasks(app):
    app.conf.beat_schedule = {
        "schedule-update-for-followed-feeds": {
            "task": "rss_scraper.feeds.tasks.schedule_update_for_followed_feeds_periodic_task",
            "schedule": crontab(minute="*/30"),  # Run every 30 minutes
        }
    }
