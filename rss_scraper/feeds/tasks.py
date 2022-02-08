import logging

from celery.exceptions import MaxRetriesExceededError
from django.conf import settings

from config import celery_app
from rss_scraper.feeds.errors import (
    FeedIsGoneError,
    FeedNotAvailableError,
    FeedUrlChangedError,
)
from rss_scraper.feeds.models import Feed
from rss_scraper.feeds.services import FeedReaderService
from rss_scraper.feeds.utils import notify_feed_creator_with_stalled_feed

logger = logging.getLogger(__name__)


@celery_app.task(
    max_retries=settings.FEED_UPDATE_TASK_MAX_RETRIES,
    default_retry_delay=settings.FEED_UPDATE_TASK_RETRY_DELAY_IN_SECONDS,
)
def update_feed_data_from_source_task(feed_instance_id: int, *args, **kwargs):
    """
    Update feed data from the source at the background.

    TODO: Apply exponential backoff retrial mechanism.
    TODO: Move task meta logging data to a decorator.
    :param feed_instance_id:
    """
    task_name = "schedule_update_for_followed_feeds_periodic_task"
    logger.info(f"Started on {task_name}")

    try:
        feed_instance = Feed.objects.get(id=feed_instance_id)
        feed_reader_service = FeedReaderService(feed_instance)
        feed_reader_service.process_feed_data_from_source()
        logger.info(
            f"Feed with id: {feed_instance.id} has been updated successfully. Task_name: {task_name}."
        )
    except Feed.DoesNotExist:
        logger.error(
            f"No feed instance with id: {feed_instance_id}. Task_name: {task_name}."
        )
    except (FeedIsGoneError, FeedUrlChangedError, FeedNotAvailableError):
        try:
            update_feed_data_from_source_task.retry()
        except MaxRetriesExceededError:
            logger.error(
                f"Updating feed with id: {feed_instance.id} has exceeded the max number of retries. "
                f"Task_name: {task_name}."
            )
            feed_instance.deactivate_auto_update()
            notify_feed_creator_with_stalled_feed(feed_instance)
            logger.info(
                f"Feed creator with email: {feed_instance.user.email} has been notified, "
                f"also we disabled the auto active updater for feed with id: {feed_instance.id}. "
                f"Task_name: {task_name}."
            )

    logger.info(f"Finished of {task_name}, feed_id: {feed_instance_id}.")


@celery_app.task()
def schedule_update_for_followed_feeds_periodic_task(*args, **kwargs):
    """
    Schedule a background task to update all the followed feed objects with active auto update.
    """
    task_name = "schedule_update_for_followed_feeds_periodic_task"
    logger.info(f"Started on {task_name}.")
    feed_ids = Feed.objects.filter(
        is_followed=True, auto_update_is_active=True
    ).values_list("id", flat=True)

    for feed_id in feed_ids:
        update_feed_data_from_source_task.delay(feed_id)

    logger.info(f"Finished of {task_name}, feed_ids: {feed_ids}.")
