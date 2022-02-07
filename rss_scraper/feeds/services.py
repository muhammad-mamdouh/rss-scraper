from collections import namedtuple
from typing import Any, Type, Union

import feedparser
from rest_framework import status

from rss_scraper.feeds.enums import FeedParsingErrorCodes
from rss_scraper.feeds.errors import (
    FeedContentNotChangedError,
    FeedIsGoneError,
    FeedNotAvailableError,
    FeedParsingError,
    FeedUrlChangedError,
)
from rss_scraper.feeds.models import Feed, Item
from rss_scraper.feeds.utils import get_datetime_from_struct_time

FeedParsedData = namedtuple(
    "FeedParsedData",
    [
        "has_error",
        "exception",
        "status_code",
        "feed",
        "items",
        "href",
        "etag",
        "last_modified",
    ],
)


class FeedReaderService:
    """
    Read and update an RSS feed.
    TODO: add logging.

    Usage:
        - feed_service_obj = FeedReaderService(feed_instance)
        - feed_service_obj.process_feed_data_from_source()
        - Make sure to take decisions on the parsing errors
            `FeedUrlChangedError`, `FeedIsGoneError`, `FeedContentNotChangedError`, `FeedNotAvailableError`
    """

    def __init__(self, feed_instance: Feed):
        self.feed_instance = feed_instance
        self.first_time_to_be_read_from_source = not self.feed_instance.title

    def update_feed_instance(self, feed_server_data: dict[str, Any], **kwargs):
        """
        Update feed instance from the parsed feed server data.

        :param feed_server_data: parsed feed data object using feed parser package.
        :param kwargs: like `modified` and `etag` or the newly redirected to `href`.
        """
        self.feed_instance.auto_update_is_active = True
        self.feed_instance.title = feed_server_data.get(
            "title", self.feed_instance.title
        )
        self.feed_instance.description = feed_server_data.get(
            "subtitle", self.feed_instance.description
        )
        self.feed_instance.url = kwargs.get("href", self.feed_instance.url)
        self.feed_instance.last_update_by_source_at = kwargs.get(
            "modified", self.feed_instance.last_update_by_source_at
        )

        if kwargs.get("etag") or self.feed_instance.e_tag:
            self.feed_instance.e_tag = kwargs.get("etag") or self.feed_instance.e_tag

        if feed_server_data.get("image") and (
            feed_image_url := feed_server_data["image"].get("href")
        ):
            self.feed_instance.image = feed_image_url

        self.feed_instance.save()

    def update_feed_items(self, items_server_data: list[dict[str, Any]]):
        """
        Update or create a feed item from the parsed items entries.

        :param items_server_data: List of parsed item entries.
        """
        if self.first_time_to_be_read_from_source:
            refined_items = [
                {
                    "feed": self.feed_instance,
                    "url": item.get("link"),
                    "title": item.get("title"),
                    "description": item.get("summary"),
                    "published_at": get_datetime_from_struct_time(
                        item["published_parsed"]
                    ),
                }
                for item in items_server_data
            ]

            Item.objects.bulk_create([Item(**item) for item in refined_items])
            return

        for item in items_server_data:
            Item.objects.update_or_create(
                feed=self.feed_instance,
                url=item.get("link"),
                defaults={
                    "title": item.get("title"),
                    "description": item.get("summary"),
                    "published_at": get_datetime_from_struct_time(
                        item["published_parsed"]
                    ),
                },
            )

    def parsed_data_validator(
        self, feed_parsed_data: FeedParsedData
    ) -> tuple[bool, Type[FeedParsingError]]:
        """
        Validate the received/parsed feed info.

        :param feed_parsed_data: the refined feed info parsed using the feed parser.
        :return: tuple(is_valid: bool, error_type: FeedParsingError)
        """
        if not feed_parsed_data.has_error and feed_parsed_data.status_code in [
            status.HTTP_200_OK,
            status.HTTP_301_MOVED_PERMANENTLY,
        ]:
            if feed_parsed_data.status_code == status.HTTP_200_OK:
                return True, False

            if (
                feed_parsed_data.status_code == FeedParsingErrorCodes.URL_CHANGED.value
                and feed_parsed_data.feed
                and feed_parsed_data.items
            ):
                return True, False
            else:
                return False, FeedUrlChangedError

        if feed_parsed_data.status_code == FeedParsingErrorCodes.IS_GONE.value:
            return False, FeedIsGoneError

        if (
            feed_parsed_data.status_code
            == FeedParsingErrorCodes.CONTENT_NOT_CHANGED.value
        ):
            return False, FeedContentNotChangedError

        return False, FeedNotAvailableError

    def parse_feed(self) -> Union[FeedParsedData, FeedParsingError]:
        """
        Read the feed data from the source using the feedparser package, validate on the result and save the refined
            data at FeedParsedData named tuple.

        :return: the parsed feed info at `FeedParsedData` or `FeedParsingError`.
        """
        source_parsing_feed_result = feedparser.parse(
            self.feed_instance.url,
            modified=self.feed_instance.last_update_by_source_at,
            etag=self.feed_instance.e_tag,
        )
        feed_parsed_data = FeedParsedData(
            has_error=source_parsing_feed_result["bozo"],
            exception=source_parsing_feed_result.get("bozo_exception"),
            status_code=source_parsing_feed_result.get("status"),
            href=source_parsing_feed_result.get("href"),
            etag=source_parsing_feed_result.get("etag"),
            feed=source_parsing_feed_result.get("feed"),
            items=source_parsing_feed_result.get("entries"),
            last_modified=get_datetime_from_struct_time(
                source_parsing_feed_result.get("updated_parsed")
            ),
        )
        is_valid, ErrorType = self.parsed_data_validator(feed_parsed_data)

        if not is_valid:
            raise ErrorType(feed_parsed_data.status_code, feed_parsed_data.exception)

        return feed_parsed_data

    def process_feed_data_from_source(self):
        """
        Handles reading the feed data from the source and saving it at the DB.
        """
        try:
            feed_parsed_data = self.parse_feed()
            self.update_feed_instance(
                feed_parsed_data.feed,
                **{
                    "href": feed_parsed_data.href,
                    "etag": feed_parsed_data.etag,
                    "modified": feed_parsed_data.last_modified,
                },
            )
            self.update_feed_items(feed_parsed_data.items)
        except FeedContentNotChangedError:
            # Feed content not changed error will be passed, the other error should be handled by the caller.
            pass
