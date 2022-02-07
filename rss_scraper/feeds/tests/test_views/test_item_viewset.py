import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient

from config.settings.base import REST_FRAMEWORK
from rss_scraper.feeds.api.serializers import ItemDynamicFieldsModelSerializer
from rss_scraper.feeds.enums import ItemStatus
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


def test__mark_item_as_read_api__with_anonymous_user__should_return_403(
    api_client: APIClient,
):
    response = api_client.post(reverse("api:item-mark-as-read", kwargs={"pk": 1}))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Authentication credentials were not provided."


def test__mark_item_as_read_api__with_new_item__should_return_200(
    api_client: APIClient, user: User
):
    feed_instance = baker.make(Feed, user=user)
    item_instance = baker.make(Item, feed=feed_instance)
    api_client.force_login(user)

    response = api_client.post(
        reverse("api:item-mark-as-read", kwargs={"pk": item_instance.id})
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == ItemStatus.READ


def test__mark_item_as_read_api__with_already_read_item__should_return_400(
    api_client: APIClient, user: User
):
    feed_instance = baker.make(Feed, user=user)
    item_instance = baker.make(Item, status=ItemStatus.READ, feed=feed_instance)
    api_client.force_login(user)

    response = api_client.post(
        reverse("api:item-mark-as-read", kwargs={"pk": item_instance.id})
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["non_field_errors"] == [
        "You've already marked this feed item as read."
    ]


def test__mark_item_as_read_api__with_item_of_not_owned_feed__should_return_404(
    api_client: APIClient, user: User
):
    user_2 = baker.make(User)
    feed_instance = baker.make(Feed, user=user_2)
    item_instance = baker.make(Item, status=ItemStatus.READ, feed=feed_instance)
    api_client.force_login(user)

    response = api_client.post(
        reverse("api:item-mark-as-read", kwargs={"pk": item_instance.id})
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Not found."


def test__list_items_api__with_anonymous_user__should_return_403(api_client: APIClient):
    response = api_client.get(reverse("api:item-list"))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Authentication credentials were not provided."


def test__list_items_api__with_authenticated_user__should_return_paginated_global_items_list(
    api_client: APIClient, user: User
):
    # Arrange
    feed_instance_1 = baker.make(Feed, user=user)
    feed_instance_2 = baker.make(Feed, user=user)
    baker.make(Item, feed=feed_instance_1, _quantity=5)
    baker.make(Item, feed=feed_instance_2, _quantity=6)
    api_client.force_login(user)

    # Act
    response = api_client.get(reverse("api:item-list"))

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == REST_FRAMEWORK["PAGE_SIZE"]


def test__list_items_api__with_items_for_different_users__should_return_items_of_feeds_of_authenticated_user(
    api_client: APIClient, user: User
):
    user_1_items_count = 4
    user_2_items_count = 9
    user_2 = baker.make(User)
    feed_instance_of_user_1 = baker.make(Feed, user=user)
    feed_instance_of_user_2 = baker.make(Feed, user=user_2)
    baker.make(Item, feed=feed_instance_of_user_1, _quantity=user_1_items_count)
    baker.make(Item, feed=feed_instance_of_user_2, _quantity=user_2_items_count)
    api_client.force_login(user)

    response = api_client.get(reverse("api:item-list"))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == user_1_items_count


def test__list_items_api__with_global_filter_on_read_status__should_return_global_read_items_list(
    api_client: APIClient, user: User, items_for_different_feed_instances
):
    global_number_of_items_with_read_status = 5
    api_client.force_login(user)

    response = api_client.get(
        reverse("api:item-list") + f"?status={ItemStatus.READ.value}"
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == global_number_of_items_with_read_status


def test__list_items_api__with_global_filter_on_unread_status__should_return_global_unread_items_list(
    api_client: APIClient, user: User, items_for_different_feed_instances
):
    global_number_of_items_with_unread_status = 9
    api_client.force_login(user)

    response = api_client.get(
        reverse("api:item-list") + f"?status={ItemStatus.NEW.value}"
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == global_number_of_items_with_unread_status


def test__list_items_api__with_filter_on_read_status_per_a_feed__should_return_read_items_per_feed_list(
    api_client: APIClient, user: User, items_for_different_feed_instances
):
    number_of_items_with_read_status_of_first_feed = 2
    feed_instance_1, _ = items_for_different_feed_instances
    api_client.force_login(user)

    response = api_client.get(
        reverse("api:item-list")
        + f"?status={ItemStatus.READ.value}&feed={feed_instance_1.id}"
    )

    assert response.status_code == status.HTTP_200_OK
    assert (
        len(response.json()["results"])
        == number_of_items_with_read_status_of_first_feed
    )


def test__list_items_api__with_filter_on_unread_status_per_a_feed__should_return_unread_items_per_feed_list(
    api_client: APIClient, user: User, items_for_different_feed_instances
):
    number_of_items_with_unread_status_of_second_feed = 5
    _, feed_instance_2 = items_for_different_feed_instances
    api_client.force_login(user)

    response = api_client.get(
        reverse("api:item-list")
        + f"?status={ItemStatus.NEW.value}&feed={feed_instance_2.id}"
    )

    assert response.status_code == status.HTTP_200_OK
    assert (
        len(response.json()["results"])
        == number_of_items_with_unread_status_of_second_feed
    )
