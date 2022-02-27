import pytest
from django.db import IntegrityError, transaction
from model_bakery import baker

from rss_scraper.feeds.enums import ItemStatus
from rss_scraper.feeds.models import Feed, Item

pytestmark = pytest.mark.django_db


def test__feed_create__given_instance__qs_count_returns_1(feed_instance: Feed):
    assert isinstance(feed_instance, Feed)
    assert Feed.objects.count() == 1
    assert (
        str(feed_instance)
        == f"Feed(id={feed_instance.id}, url={feed_instance.url}, user={feed_instance.user})"
    )


def test__feed_create__given_duplicate_url_and_user__should_raise_integrity_error(
    feed_instance: Feed,
):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            baker.make(Feed, url=feed_instance.url, user=feed_instance.user)

    assert Feed.objects.count() == 1


def test__mark_feed_as_followed__given_unfollowed_feed__should_change_it_to_followed(
    feed_instance: Feed,
):
    feed_instance.unfollow()
    assert not feed_instance.is_followed

    feed_instance.follow()

    assert feed_instance.is_followed


def test__mark_feed_as_unfollowed__given_followed_feed__should_change_it_to_unfollowed(
    feed_instance: Feed,
):
    assert feed_instance.is_followed

    feed_instance.unfollow()

    assert feed_instance.is_followed is False


def test__feed_activate_auto_update__given_unactive_feed__should_change_it_to_active(
    feed_instance: Feed,
):
    feed_instance.deactivate_auto_update()
    assert not feed_instance.auto_update_is_active

    feed_instance.activate_auto_update()

    assert feed_instance.auto_update_is_active


def test__feed_disable_auto_update__given_active_feed__should_disable_auto_active(
    feed_instance: Feed,
):
    assert feed_instance.auto_update_is_active

    feed_instance.deactivate_auto_update()

    assert feed_instance.auto_update_is_active is False


def test__item_create__given_instance__qs_count_returns_1(item_instance: Item):
    assert isinstance(item_instance, Item)
    assert Feed.objects.count() == 1
    assert Item.objects.count() == 1
    assert (
        str(item_instance)
        == f"Item(id={item_instance.id}, url={item_instance.url}, feed={item_instance.feed})"
    )


def test__mark_item_as_read__given_new_item__should_change_its_status_to_read(
    item_instance: Item,
):
    assert item_instance.status == ItemStatus.NEW

    item_instance.mark_as_read()

    assert item_instance.status == ItemStatus.READ
