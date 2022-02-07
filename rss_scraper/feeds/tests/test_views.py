import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient

from config.settings.base import REST_FRAMEWORK
from rss_scraper.feeds.api.serializers import FeedModelSerializer
from rss_scraper.feeds.models import Feed
from rss_scraper.users.models import User

pytestmark = pytest.mark.django_db


class TestFeedViewSetV1:
    def test__list_api__with_anonymous_user__should_return_403(
        self, api_client: APIClient
    ):
        response = api_client.get(reverse("api:feed-list"))

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert (
            response.json()["detail"] == "Authentication credentials were not provided."
        )

    def test__list_api__with_authenticated_user__should_return_paginated_feeds_list(
        self, api_client: APIClient, user: User
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
        self, api_client: APIClient, user: User
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
        self, api_client: APIClient
    ):
        response = api_client.get(reverse("api:feed-detail", kwargs={"pk": 1}))

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert (
            response.json()["detail"] == "Authentication credentials were not provided."
        )

    def test__retrieve_by_id_api__with_authenticated_user__should_return_200(
        self, api_client: APIClient, user: User
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
        self, api_client: APIClient, user: User
    ):
        user_2 = baker.make(User)
        feed_instance = baker.make(Feed, user=user_2)
        api_client.force_login(user)

        response = api_client.get(
            reverse("api:feed-detail", kwargs={"pk": feed_instance.id})
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Not found."
