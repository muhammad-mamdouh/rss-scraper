from enum import Enum

from django.db import models


class ItemStatus(models.IntegerChoices):
    NEW, READ = range(1, 3)


class FeedParsingErrorCodes(Enum):
    IS_GONE = 410
    URL_CHANGED = 301
    CONTENT_NOT_CHANGED = 304
