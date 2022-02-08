from unittest import mock

import pytest
from rest_framework import status

from rss_scraper.feeds.enums import FeedParsingErrorCodes
from rss_scraper.feeds.errors import (
    FeedIsGoneError,
    FeedNotAvailableError,
    FeedUrlChangedError,
)
from rss_scraper.feeds.services import FeedReaderService
from rss_scraper.feeds.tests.mock_feed_parser_data import (
    feed_content_not_changed_data,
    feed_is_gone_data,
    feed_url_changed_with_valid_data,
    feed_url_changed_without_valid_data,
    not_valid_feed,
    valid_parsed_feed_content,
)

pytestmark = pytest.mark.django_db


class TestFeedReaderService:
    BASE_FEED_URL = "https://feeds.feedburner.com/tweakers/mixed"
    VALID_STATUS_CODES = [status.HTTP_200_OK, status.HTTP_301_MOVED_PERMANENTLY]

    @mock.patch("feedparser.parse", return_value=valid_parsed_feed_content)
    def test__service__with_valid_feed_data__should_be_processed_successfully(
        self, _, feed_service: FeedReaderService
    ):
        feed_service.process_feed_data_from_source()

        assert valid_parsed_feed_content["status"] in self.VALID_STATUS_CODES
        assert (
            feed_service.feed_instance.title
            == valid_parsed_feed_content["feed"]["title"]
        )
        assert feed_service.feed_instance.items.count() == len(
            valid_parsed_feed_content["entries"]
        )

    @mock.patch("feedparser.parse", return_value=valid_parsed_feed_content)
    def test__service__with_valid_feed_data_and_already_updated_feed__should_save_items_one_by_one(
        self, _, feed_service: FeedReaderService
    ):
        feed_service.first_time_to_be_read_from_source = False
        assert not feed_service.feed_instance.items.count()

        feed_service.process_feed_data_from_source()

        assert valid_parsed_feed_content["status"] in self.VALID_STATUS_CODES
        assert (
            feed_service.feed_instance.title
            == valid_parsed_feed_content["feed"]["title"]
        )
        assert feed_service.feed_instance.items.count() == len(
            valid_parsed_feed_content["entries"]
        )

    @mock.patch("feedparser.parse", return_value=not_valid_feed)
    @mock.patch("rss_scraper.feeds.services.FeedReaderService.update_feed_items")
    @mock.patch("rss_scraper.feeds.services.FeedReaderService.update_feed_instance")
    def test__service__with_not_valid_feed_data__should_raises_feed_not_valid_error(
        self,
        update_feed_instance_mock,
        update_feed_items_mock,
        _,
        feed_service: FeedReaderService,
    ):
        with pytest.raises(FeedNotAvailableError) as err_info:
            feed_service.process_feed_data_from_source()

        assert err_info.value.code not in self.VALID_STATUS_CODES
        assert not feed_service.feed_instance.items.count()
        update_feed_instance_mock.assert_not_called()
        update_feed_items_mock.assert_not_called()

    @mock.patch("feedparser.parse", return_value=feed_is_gone_data)
    @mock.patch("rss_scraper.feeds.services.FeedReaderService.update_feed_items")
    @mock.patch("rss_scraper.feeds.services.FeedReaderService.update_feed_instance")
    def test__service__with_feed_is_gone__should_raises_feed_is_gone_error(
        self,
        update_feed_instance_mock,
        update_feed_items_mock,
        _,
        feed_service: FeedReaderService,
    ):
        with pytest.raises(FeedIsGoneError) as err_info:
            feed_service.process_feed_data_from_source()

        assert err_info.value.code == FeedParsingErrorCodes.IS_GONE.value
        update_feed_instance_mock.assert_not_called()
        update_feed_items_mock.assert_not_called()

    @mock.patch("feedparser.parse", return_value=feed_content_not_changed_data)
    @mock.patch("rss_scraper.feeds.services.FeedReaderService.update_feed_items")
    @mock.patch("rss_scraper.feeds.services.FeedReaderService.update_feed_instance")
    def test__service__with_feed_content_not_changed__should_pass_without_updating_feed_data(
        self,
        update_feed_instance_mock,
        update_feed_items_mock,
        _,
        feed_service: FeedReaderService,
    ):
        feed_service.process_feed_data_from_source()

        update_feed_instance_mock.assert_not_called()
        update_feed_items_mock.assert_not_called()

    @mock.patch("feedparser.parse", return_value=feed_url_changed_without_valid_data)
    @mock.patch("rss_scraper.feeds.services.FeedReaderService.update_feed_items")
    @mock.patch("rss_scraper.feeds.services.FeedReaderService.update_feed_instance")
    def test__service__with_feed_url_changed_without_valid_data__should_raises_feed_url_changed_error(
        self,
        update_feed_instance_mock,
        update_feed_items_mock,
        _,
        feed_service: FeedReaderService,
    ):
        with pytest.raises(FeedUrlChangedError) as err_info:
            feed_service.process_feed_data_from_source()

        assert err_info.value.code == FeedParsingErrorCodes.URL_CHANGED.value
        update_feed_instance_mock.assert_not_called()
        update_feed_items_mock.assert_not_called()

    @mock.patch("feedparser.parse", return_value=feed_url_changed_with_valid_data)
    def test__service__with_feed_url_changed_with_valid_data__should_be_processed_successfully(
        self,
        _,
        feed_service: FeedReaderService,
    ):
        old_feed_instance_url = feed_service.feed_instance.url

        feed_service.process_feed_data_from_source()

        assert (
            feed_url_changed_with_valid_data["status"]
            == FeedParsingErrorCodes.URL_CHANGED.value
        )
        assert feed_service.feed_instance.url != old_feed_instance_url
