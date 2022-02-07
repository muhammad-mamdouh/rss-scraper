import pytest

from rss_scraper.feeds.enums import FeedParsingErrorCodes
from rss_scraper.feeds.errors import (
    FeedContentNotChangedError,
    FeedIsGoneError,
    FeedNotAvailableError,
    FeedParsingError,
    FeedUrlChangedError,
)
from rss_scraper.feeds.tests.factories import (
    raise_feed_content_not_changed_error,
    raise_feed_is_gone_error,
    raise_feed_not_available_error,
    raise_feed_parsing_error,
    raise_feed_url_changed_error,
)


def test__feed_parsing_error():
    with pytest.raises(FeedParsingError) as err_info:
        raise_feed_parsing_error()

    assert type(err_info.value.code) is int
    assert type(err_info.value.message) is str


def test__feed_is_gone_error():
    with pytest.raises(FeedIsGoneError) as err_info:
        raise_feed_is_gone_error()

    assert err_info.value.code == FeedParsingErrorCodes.IS_GONE.value
    assert type(err_info.value.message) is str


def test__feed_url_changed_error():
    with pytest.raises(FeedUrlChangedError) as err_info:
        raise_feed_url_changed_error()

    assert err_info.value.code == FeedParsingErrorCodes.URL_CHANGED.value
    assert type(err_info.value.message) is str


def test__feed_content_not_changed_error():
    with pytest.raises(FeedContentNotChangedError) as err_info:
        raise_feed_content_not_changed_error()

    assert err_info.value.code == FeedParsingErrorCodes.CONTENT_NOT_CHANGED.value
    assert type(err_info.value.message) is str


def test__feed_not_available_error():
    with pytest.raises(FeedNotAvailableError) as err_info:
        raise_feed_not_available_error()

    assert type(err_info.value.code) is int
    assert type(err_info.value.message) is str
