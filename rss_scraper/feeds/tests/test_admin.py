import pytest
from django.urls import reverse
from rest_framework import status

from rss_scraper.feeds.mixins import (
    DisableAdminAddPermission,
    DisableAdminDeletePermission,
)
from rss_scraper.feeds.models import Feed, Item

pytestmark = pytest.mark.django_db


class TestAdminSiteForFeedModel:
    def test__list_page__given_valid_admin_user__should_return_200_ok(
        self, admin_client
    ):
        url = reverse("admin:feeds_feed_changelist")
        response = admin_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test__change_feed_page__given_valid_admin_user_and_feed_instance__should_return_200_ok(
        self, admin_client, feed_instance: Feed
    ):
        url = reverse("admin:feeds_feed_change", args=[feed_instance.id])
        response = admin_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test__add_feed_page__given_valid_admin_user__should_return_200_ok(
        self, admin_client
    ):
        url = reverse("admin:feeds_feed_add")
        response = admin_client.get(url)

        assert response.status_code == status.HTTP_200_OK


class TestAdminSiteForItemModel:
    def test__list_page__given_valid_admin_user__should_return_200_ok(
        self, admin_client
    ):
        url = reverse("admin:feeds_item_changelist")
        response = admin_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test__change_item_page__given_valid_admin_user_and_item_instance__should_return_200_ok(
        self, admin_client, item_instance: Item
    ):
        url = reverse("admin:feeds_item_change", args=[item_instance.id])
        response = admin_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test__add_item_page__given_valid_admin_user__should_return_200_ok(
        self, admin_client
    ):
        url = reverse("admin:feeds_item_add")
        response = admin_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test__has_add_permission__with_disable_admin_add_permission_mixin__should_return_false(
        self, admin_client
    ):
        class ModelAdminWithoutAddPermission(DisableAdminAddPermission):
            pass

        assert (
            ModelAdminWithoutAddPermission().has_add_permission(admin_client) is False
        )

    def test__has_delete_permission__with_disable_admin_delete_permission_mixin__should_return_false(
        self, admin_client
    ):
        class ModelAdminWithoutDeletePermission(DisableAdminDeletePermission):
            pass

        assert (
            ModelAdminWithoutDeletePermission().has_delete_permission(admin_client)
            is False
        )
