from unittest import mock

import pytest
from celery.exceptions import MaxRetriesExceededError, Retry
from model_bakery import baker

from rss_scraper.feeds.enums import FeedParsingErrorCodes
from rss_scraper.feeds.errors import FeedIsGoneError, FeedNotAvailableError
from rss_scraper.feeds.models import Feed
from rss_scraper.feeds.tasks import (
    schedule_update_for_followed_feeds_periodic_task,
    update_feed_data_from_source_task,
)
from rss_scraper.users.models import User

pytestmark = pytest.mark.django_db


@mock.patch("rss_scraper.feeds.tasks.update_feed_data_from_source_task.delay")
def test__periodic_task__given_feeds_with_different_followed_and_active__should_run_only_followed_and_active_feeds(
    update_feed_data_from_source_task, user: User
):
    """
    Given feeds with different `is_followed` and different `auto_update_is_active`,
        the `schedule_update_for_followed_feeds_periodic_task` should only schedule feeds with
        `is_followed` and `auto_update_is_active` is True.
    """
    user_2 = baker.make(User)
    baker.make(
        Feed, is_followed=True, auto_update_is_active=True, user=user, _quantity=3
    )
    baker.make(
        Feed, is_followed=True, auto_update_is_active=True, user=user_2, _quantity=3
    )
    baker.make(
        Feed, is_followed=False, auto_update_is_active=True, user=user, _quantity=2
    )
    baker.make(
        Feed, is_followed=True, auto_update_is_active=False, user=user_2, _quantity=4
    )
    expected_to_be_updated_feed_ids = Feed.objects.filter(
        is_followed=True, auto_update_is_active=True
    ).values_list("id", flat=True)

    schedule_update_for_followed_feeds_periodic_task.run()

    assert update_feed_data_from_source_task.call_count == len(
        expected_to_be_updated_feed_ids
    )


@mock.patch(
    "rss_scraper.feeds.services.FeedReaderService.process_feed_data_from_source"
)
def test__update_feed_data_from_source_task__given_not_valid_feed_id__should_not_call_reader_service(
    process_feed_data_from_source_mock,
):
    update_feed_data_from_source_task.run(99)

    process_feed_data_from_source_mock.assert_not_called()


@mock.patch(
    "rss_scraper.feeds.services.FeedReaderService.process_feed_data_from_source"
)
def test__update_feed_data_from_source_task__given_valid_feed_id__should_process_parsed_feed_data(
    process_feed_data_from_source_mock, feed_instance: Feed
):
    """
    Given valid feed object id to be updated using the `update_feed_data_from_source_task`
        `FeedReaderService.process_feed_data_from_source()` should be called once.

    Note: We don't test on the inner working of the `process_feed_data_from_source()` as its test cases
        are covered at the test_services module.
    """
    update_feed_data_from_source_task.run(feed_instance.id)

    process_feed_data_from_source_mock.assert_called()


@mock.patch("rss_scraper.feeds.tasks.update_feed_data_from_source_task.retry")
@mock.patch(
    "rss_scraper.feeds.services.FeedReaderService.process_feed_data_from_source"
)
def test__update_feed_data_from_source_task__given_non_valid_feed_parsing__should_retry_the_update_task(
    process_feed_data_from_source_mock,
    update_feed_data_from_source_task_retry_mock,
    feed_instance: Feed,
):
    process_feed_data_from_source_mock.side_effect = FeedNotAvailableError(
        FeedParsingErrorCodes.IS_GONE.value, ""
    )
    update_feed_data_from_source_task_retry_mock.side_effect = Retry()

    with pytest.raises(Retry):
        update_feed_data_from_source_task.run(feed_instance.id)

    assert feed_instance.auto_update_is_active
    assert process_feed_data_from_source_mock.call_count == 1
    assert update_feed_data_from_source_task_retry_mock.call_count == 1


@mock.patch("rss_scraper.feeds.tasks.notify_feed_creator_with_stalled_feed")
@mock.patch("rss_scraper.feeds.tasks.update_feed_data_from_source_task.retry")
@mock.patch(
    "rss_scraper.feeds.services.FeedReaderService.process_feed_data_from_source"
)
def test__update_feed_data_from_source_task__given_exceeding_max_task_retries__should_notify_user_and_deactivate_feed(
    process_feed_data_from_source_mock,
    update_feed_data_from_source_task_retry_mock,
    notify_feed_creator_with_stalled_feed_mock,
    feed_instance: Feed,
):
    process_feed_data_from_source_mock.side_effect = FeedIsGoneError(
        FeedParsingErrorCodes.IS_GONE.value, ""
    )
    update_feed_data_from_source_task_retry_mock.side_effect = MaxRetriesExceededError()

    update_feed_data_from_source_task.run(feed_instance.id)
    feed_instance.refresh_from_db()

    update_feed_data_from_source_task_retry_mock.assert_called()
    notify_feed_creator_with_stalled_feed_mock.assert_called()
    assert feed_instance.auto_update_is_active is False
