import datetime
import time

import pytest
import pytz
from django.conf import settings
from django.core import mail
from django.utils.translation import gettext_lazy as _

from rss_scraper.feeds.models import Feed
from rss_scraper.feeds.utils import (
    get_datetime_from_struct_time,
    notify_feed_creator_with_stalled_feed,
)

pytestmark = pytest.mark.django_db


def test__get_datetime_from_struct_time__given_time_struct__should_have_valid_datetime(
    time_struct: time.struct_time,
):
    returned_datetime = get_datetime_from_struct_time(time_struct)

    assert type(returned_datetime) is datetime.datetime
    assert returned_datetime.tzinfo == pytz.timezone(settings.TIME_ZONE)
    assert returned_datetime.year == time_struct.tm_year


def test__get_datetime_from_struct_time__given_non_valid_time_struct__should_return_none():
    returned_datetime = get_datetime_from_struct_time()

    assert returned_datetime is None


def test__notify_feed_creator_with_stalled_feed__with_valid_feed_instance__should_send_email_to_feed_creator(
    feed_instance: Feed,
):
    notify_feed_creator_with_stalled_feed(feed_instance)

    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == _(
        "[RSS Scraper] Sorry, One of your registered feeds has been stalled!"
    )
    assert mail.outbox[0].recipients() == [feed_instance.user.email]
