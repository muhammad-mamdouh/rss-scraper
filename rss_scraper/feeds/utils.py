import datetime
import time

import pytz
from django.conf import settings


def get_datetime_from_struct_time(time_struct: time.struct_time) -> datetime.datetime:
    """
    Create a datetime object with respect to the django timezone settings from a time struct.
    """

    return datetime.datetime(
        time_struct.tm_year,
        time_struct.tm_mon,
        time_struct.tm_mday,
        time_struct.tm_hour,
        time_struct.tm_min,
        time_struct.tm_sec,
        tzinfo=pytz.timezone(settings.TIME_ZONE),
    )
