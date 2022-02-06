import pytest
from django.test import RequestFactory
from faker import Faker
from model_bakery import baker

from rss_scraper.feeds.models import Feed, Item
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
