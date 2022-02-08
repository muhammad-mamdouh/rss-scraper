import random

from rss_scraper.feeds import errors
from rss_scraper.feeds.enums import FeedParsingErrorCodes


def raise_feed_parsing_error():
    raise errors.FeedParsingError(random.randint(400, 500), "error message")


def raise_feed_is_gone_error():
    raise errors.FeedIsGoneError(FeedParsingErrorCodes.IS_GONE.value, "error message")


def raise_feed_url_changed_error():
    raise errors.FeedUrlChangedError(
        FeedParsingErrorCodes.URL_CHANGED.value, "error message"
    )


def raise_feed_content_not_changed_error():
    raise errors.FeedContentNotChangedError(
        FeedParsingErrorCodes.CONTENT_NOT_CHANGED.value, "error message"
    )


def raise_feed_not_available_error():
    raise errors.FeedNotAvailableError(random.randint(400, 500), "error message")
