import random

from rss_scraper.feeds import errors


def raise_feed_parsing_error():
    raise errors.FeedParsingError(random.randint(400, 500), "error message")


def raise_feed_is_gone_error():
    raise errors.FeedIsGoneError(410, "error message")


def raise_feed_url_changed_error():
    raise errors.FeedUrlChangedError(301, "error message")


def raise_feed_content_not_changed_error():
    raise errors.FeedContentNotChangedError(304, "error message")


def raise_feed_not_available_error():
    raise errors.FeedNotAvailableError(random.randint(400, 500), "error message")
