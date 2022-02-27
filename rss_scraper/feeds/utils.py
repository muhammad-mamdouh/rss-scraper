import datetime
import time
from typing import Optional

import pytz
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from rss_scraper.feeds.models import Feed


def get_datetime_from_struct_time(
    time_struct: Optional[time.struct_time] = None
) -> Optional[datetime.datetime]:
    """
    Create a datetime object with respect to the django timezone settings from a time struct.
    """
    if not time_struct:
        return

    return datetime.datetime(
        time_struct.tm_year,
        time_struct.tm_mon,
        time_struct.tm_mday,
        time_struct.tm_hour,
        time_struct.tm_min,
        time_struct.tm_sec,
        tzinfo=pytz.timezone(settings.TIME_ZONE),
    )


def notify_feed_creator_with_stalled_feed(feed_instance: Feed):
    """
    Send email to the feed creator in case the system failed to read/update the feed,
        after exceeding the valid amount of retries.
    """
    template = "feeds/emails/email_stalled_feed.txt"
    context = {
        "feed_title": feed_instance.title,
        "feed_id": feed_instance.id,
    }

    send_mail(
        subject=_(
            "[RSS Scraper] Sorry, One of your registered feeds has been stalled!"
        ),
        message=render_to_string(template, context),
        from_email="noreply@rss-scraper.com",
        recipient_list=[feed_instance.user.email],
    )
