from unittest.mock import ANY

import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient

from config.settings.base import REST_FRAMEWORK
from rss_scraper.feeds.api.serializers import FeedModelSerializer
from rss_scraper.feeds.models import Feed, Item
from rss_scraper.users.models import User

pytestmark = pytest.mark.django_db


def test__list_api__with_anonymous_user__should_return_403(api_client: APIClient):
    response = api_client.get(reverse("api:feed-list"))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Authentication credentials were not provided."


def test__list_api__with_authenticated_user__should_return_paginated_feeds_list(
    api_client: APIClient, user: User
):
    # Arrange
    baker.make(Feed, user=user, _quantity=11)
    api_client.force_login(user)

    # Act
    response = api_client.get(reverse("api:feed-list"))

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == REST_FRAMEWORK["PAGE_SIZE"]


def test__list_api__with_feeds_for_different_users__should_return_feeds_of_authenticated_user(
    api_client: APIClient, user: User
):
    # Arrange
    user_2 = baker.make(User)
    user_1_feeds_count = 4
    baker.make(Feed, user=user, _quantity=user_1_feeds_count)
    baker.make(Feed, user=user_2, _quantity=5)
    api_client.force_login(user)

    # Act
    response = api_client.get(reverse("api:feed-list"))

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == user_1_feeds_count


def test__retrieve_by_id_api__with_anonymous_user__should_return_403(
    api_client: APIClient,
):
    response = api_client.get(reverse("api:feed-detail", kwargs={"pk": 1}))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Authentication credentials were not provided."


def test__retrieve_by_id_api__with_authenticated_user__should_return_200(
    api_client: APIClient, user: User
):
    feed_instance = baker.make(Feed, user=user)
    api_client.force_login(user)
    serializer = FeedModelSerializer(feed_instance)

    response = api_client.get(
        reverse("api:feed-detail", kwargs={"pk": feed_instance.id})
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == serializer.data


def test__retrieve_by_id_api__with_authenticated_user_and_not_created_feed__should_return_404(
    api_client: APIClient, user: User
):
    user_2 = baker.make(User)
    feed_instance = baker.make(Feed, user=user_2)
    api_client.force_login(user)

    response = api_client.get(
        reverse("api:feed-detail", kwargs={"pk": feed_instance.id})
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Not found."


def test__create_api__with_anonymous_user__should_return_403(api_client: APIClient):
    response = api_client.post(reverse("api:feed-list"))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Authentication credentials were not provided."


def test__create_api__with_authenticated_user_and_valid_url__should_return_201(
    api_client: APIClient, user: User, random_url: str
):
    api_client.force_login(user)

    response = api_client.post(reverse("api:feed-list"), data={"url": random_url})

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "url": random_url,
        "title": "",
        "description": "",
        "auto_update_is_active": True,
        "is_followed": True,
        "image": None,
        "last_update_by_source_at": None,
        "id": ANY,
        "updated_at": ANY,
        "created_at": ANY,
    }


def test__create_api__with_authenticated_user_and_not_valid_url__should_return_url_not_valid(
    api_client: APIClient, user: User, random_url: str
):
    api_client.force_login(user)

    response = api_client.post(reverse("api:feed-list"), data={"url": "not valid url"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["url"] == ["Enter a valid URL."]


def test__create_api__with_authenticated_user_and_not_passing_url__should_return_url_not_valid(
    api_client: APIClient, user: User
):
    api_client.force_login(user)

    response = api_client.post(reverse("api:feed-list"), data={"url": "not valid url"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["url"] == ["Enter a valid URL."]


def test__create_api__with_authenticated_user_and_duplicated_url__should_return_url_already_registered(
    api_client: APIClient, user: User, random_url
):
    baker.make(Feed, url=random_url, user=user)
    api_client.force_login(user)

    response = api_client.post(reverse("api:feed-list"), data={"url": random_url})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["non_field_errors"] == [
        "You've already registered a feed with this url before."
    ]


def test__follow_api__with_anonymous_user__should_return_403(api_client: APIClient):
    response = api_client.post(reverse("api:feed-follow", kwargs={"pk": 1}))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Authentication credentials were not provided."


def test__follow_api__with_authenticated_user_and_unfollowed_feed__should_return_200(
    api_client: APIClient, user: User
):
    feed_instance = baker.make(Feed, is_followed=False, user=user)
    api_client.force_login(user)

    response = api_client.post(
        reverse("api:feed-follow", kwargs={"pk": feed_instance.id})
    )
    feed_instance.refresh_from_db()
    serializer = FeedModelSerializer(feed_instance)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == serializer.data


def test__follow_api__with_authenticated_user_and_followed_feed__should_return_400(
    api_client: APIClient, user: User
):
    feed_instance = baker.make(Feed, user=user)
    api_client.force_login(user)

    response = api_client.post(
        reverse("api:feed-follow", kwargs={"pk": feed_instance.id})
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["non_field_errors"] == ["You've already followed this feed."]


def test__follow_api__with_authenticated_user_and_not_owned_unfollowed_feed__should_return_404(
    api_client: APIClient, user: User
):
    user_2 = baker.make(User)
    feed_instance = baker.make(Feed, is_followed=False, user=user_2)
    api_client.force_login(user)

    response = api_client.post(
        reverse("api:feed-follow", kwargs={"pk": feed_instance.id})
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Not found."


def test__unfollow_api__with_anonymous_user__should_return_403(api_client: APIClient):
    response = api_client.post(reverse("api:feed-unfollow", kwargs={"pk": 1}))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Authentication credentials were not provided."


def test__unfollow_api__with_authenticated_user_and_followed_feed__should_return_200(
    api_client: APIClient, user: User
):
    feed_instance = baker.make(Feed, user=user)
    api_client.force_login(user)

    response = api_client.post(
        reverse("api:feed-unfollow", kwargs={"pk": feed_instance.id})
    )
    feed_instance.refresh_from_db()
    serializer = FeedModelSerializer(feed_instance)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == serializer.data


def test__unfollow_api__with_authenticated_user_and_unfollowed_feed__should_return_400(
    api_client: APIClient, user: User
):
    feed_instance = baker.make(Feed, is_followed=False, user=user)
    api_client.force_login(user)

    response = api_client.post(
        reverse("api:feed-unfollow", kwargs={"pk": feed_instance.id})
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["non_field_errors"] == [
        "You've already unfollowed this feed."
    ]


def test__unfollow_api__with_authenticated_user_and_not_owned_followed_feed__should_return_404(
    api_client: APIClient, user: User
):
    user_2 = baker.make(User)
    feed_instance = baker.make(Feed, user=user_2)
    api_client.force_login(user)

    response = api_client.post(
        reverse("api:feed-unfollow", kwargs={"pk": feed_instance.id})
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Not found."


def test__force_update_api__with_anonymous_user__should_return_403(
    api_client: APIClient,
):
    response = api_client.put(reverse("api:feed-force-update", kwargs={"pk": 1}))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Authentication credentials were not provided."


def test__force_update_api__with_authenticated_user_and_not_owned_feed__should_return_404(
    api_client: APIClient, user: User
):
    user_2 = baker.make(User)
    feed_instance = baker.make(Feed, auto_update_is_active=False, user=user_2)
    api_client.force_login(user)

    response = api_client.put(
        reverse("api:feed-force-update", kwargs={"pk": feed_instance.id})
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Not found."


def test__force_update_api__with_authenticated_user_and_not_auto_update_feed__should_return_200(
    api_client: APIClient, user: User
):
    feed_instance = baker.make(Feed, auto_update_is_active=False, user=user)
    api_client.force_login(user)

    response = api_client.put(
        reverse("api:feed-force-update", kwargs={"pk": feed_instance.id})
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["auto_update_is_active"] is True


def test__feed_items_api__with_anonymous_user__should_return_403(api_client: APIClient):
    response = api_client.get(reverse("api:feed-items", kwargs={"pk": 1}))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Authentication credentials were not provided."


def test__feed_items_api__with_authenticated_user_and_not_owned_feed__should_return_404(
    api_client: APIClient, user: User
):
    user_2 = baker.make(User)
    feed_instance = baker.make(Feed, user=user_2)
    api_client.force_login(user)

    response = api_client.get(
        reverse("api:feed-items", kwargs={"pk": feed_instance.id})
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Not found."


def test__feed_items_api__with_authenticated_user_and_owned_feed__should_return_paginated_items_list(
    api_client: APIClient, user: User
):
    feed_instance = baker.make(Feed, user=user)
    baker.make(Item, feed=feed_instance, _quantity=11)
    api_client.force_login(user)

    response = api_client.get(
        reverse("api:feed-items", kwargs={"pk": feed_instance.id})
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == REST_FRAMEWORK["PAGE_SIZE"]


def test__feed_items_api__with_items_for_different_users__should_return_items_of_authenticated_user(
    api_client: APIClient, user: User
):
    # Arrange
    items_of_feed_1_count = 4
    user_1_items_of_feed_2_count = 8
    feed_instance_1 = baker.make(Feed, user=user)
    feed_instance_2 = baker.make(Feed, user=user)
    baker.make(Item, feed=feed_instance_1, _quantity=items_of_feed_1_count)
    baker.make(Item, feed=feed_instance_2, _quantity=user_1_items_of_feed_2_count)

    user_2 = baker.make(User)
    feed_instance_3 = baker.make(Feed, user=user_2)
    baker.make(Item, feed=feed_instance_3, _quantity=items_of_feed_1_count)

    api_client.force_login(user)

    # Act
    response = api_client.get(
        reverse("api:feed-items", kwargs={"pk": feed_instance_2.id})
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == user_1_items_of_feed_2_count
