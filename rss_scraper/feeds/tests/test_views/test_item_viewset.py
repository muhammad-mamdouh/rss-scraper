import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient

from rss_scraper.feeds.api.serializers import ItemDynamicFieldsModelSerializer
from rss_scraper.feeds.models import Feed, Item
from rss_scraper.users.models import User

pytestmark = pytest.mark.django_db


def test__retrieve_item_by_id_api__with_anonymous_user__should_return_403(
    api_client: APIClient,
):
    response = api_client.get(reverse("api:item-detail", kwargs={"pk": 1}))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Authentication credentials were not provided."


def test__retrieve_item_by_id_api__with_item_of_owned_feed__should_return_200(
    api_client: APIClient, user: User
):
    feed_instance = baker.make(Feed, user=user)
    item_instance = baker.make(Item, feed=feed_instance)
    api_client.force_login(user)
    serializer = ItemDynamicFieldsModelSerializer(item_instance)

    response = api_client.get(
        reverse("api:item-detail", kwargs={"pk": item_instance.id})
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == serializer.data


def test__retrieve_item_by_id_api__with_item_of_not_owned_feed__should_return_404(
    api_client: APIClient, user: User
):
    user_2 = baker.make(User)
    feed_instance = baker.make(Feed, user=user_2)
    item_instance = baker.make(Item, feed=feed_instance)
    api_client.force_login(user)

    response = api_client.get(
        reverse("api:item-detail", kwargs={"pk": item_instance.id})
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Not found."
