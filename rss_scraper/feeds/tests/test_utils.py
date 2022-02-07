import datetime
import time

import pytz
from django.conf import settings

from rss_scraper.feeds.utils import get_datetime_from_struct_time


def test__get_datetime_from_struct_time__given_time_struct__should_have_valid_datetime(
    time_struct: time.struct_time,
):
    returned_datetime = get_datetime_from_struct_time(time_struct)

    assert type(returned_datetime) is datetime.datetime
    assert returned_datetime.tzinfo == pytz.timezone(settings.TIME_ZONE)
    assert returned_datetime.year == time_struct.tm_year
