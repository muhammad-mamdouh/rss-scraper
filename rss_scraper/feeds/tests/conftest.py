import pytest
from model_bakery import baker

from rss_scraper.feeds.models import Feed, Item


@pytest.fixture
def feed_instance(user) -> Feed:
    return baker.make(Feed, user=user)


@pytest.fixture
def item_instance(feed_instance) -> Item:
    return baker.make(Item, feed=feed_instance)
