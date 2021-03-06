import time
from typing import Tuple

import pytest
from django.test import RequestFactory
from faker import Faker
from model_bakery import baker

from rss_scraper.feeds.enums import ItemStatus
from rss_scraper.feeds.models import Feed, Item
from rss_scraper.feeds.services import FeedReaderService
from rss_scraper.users.models import User

fake = Faker()


@pytest.fixture
def feed_instance(user) -> Feed:
    return baker.make(Feed, user=user)


@pytest.fixture
def item_instance(feed_instance) -> Item:
    return baker.make(Item, feed=feed_instance)


@pytest.fixture
def random_url() -> str:
    return fake.url()


@pytest.fixture
def dummy_drf_request(user: User):
    request_factory = RequestFactory()
    request = request_factory.get("/fake-url/")
    request.user = user

    return request


@pytest.fixture
def items_for_different_feed_instances(user: User) -> Tuple[Feed, Feed]:
    feed_instance_1 = baker.make(Feed, user=user)
    feed_instance_2 = baker.make(Feed, user=user)
    baker.make(Item, status=ItemStatus.NEW, feed=feed_instance_1, _quantity=4)
    baker.make(Item, status=ItemStatus.NEW, feed=feed_instance_2, _quantity=5)
    baker.make(Item, status=ItemStatus.READ, feed=feed_instance_1, _quantity=2)
    baker.make(Item, status=ItemStatus.READ, feed=feed_instance_2, _quantity=3)

    return feed_instance_1, feed_instance_2


@pytest.fixture
def time_struct() -> time.struct_time:
    return time.struct_time((2022, 2, 7, 17, 12, 36, 0, 38, 0))


@pytest.fixture
def feed_service(user: User) -> FeedReaderService:
    base_feed_url = "https://feeds.feedburner.com/tweakers/mixed"
    feed_instance = baker.make(Feed, url=base_feed_url, user=user)
    return FeedReaderService(feed_instance)
