import pytest
from rest_framework import exceptions

from rss_scraper.feeds.api.serializers import (
    FeedModelSerializer,
    ItemDynamicFieldsModelSerializer,
)
from rss_scraper.feeds.models import Item

pytestmark = pytest.mark.django_db


class TestFeedModelSerializer:
    def test__feed_serializer__given_valid_url__should_pass_validations(
        self, random_url: str, dummy_drf_request
    ):
        serializer = FeedModelSerializer(
            data={"url": random_url}, context={"request": dummy_drf_request}
        )

        assert serializer.is_valid()
        assert set(serializer.validated_data) == {"url", "user"}
        assert set(serializer.fields.keys()) == {
            "id",
            "user",
            "url",
            "title",
            "description",
            "auto_update_is_active",
            "is_followed",
            "image",
            "last_update_by_source_at",
            "updated_at",
            "created_at",
        }

    def test__feed_serializer__without_url__should_raise_url_is_required(
        self, random_url: str, dummy_drf_request
    ):
        serializer = FeedModelSerializer(
            data={}, context={"request": dummy_drf_request}
        )

        with pytest.raises(exceptions.ValidationError) as err_info:
            serializer.is_valid(raise_exception=True)

        assert err_info.type == exceptions.ValidationError
        assert err_info.value.args[0]["url"] == ["This field is required."]

    def test__feed_serializer__duplicate_url_for_same_user__should_raise_validation_error(
        self, random_url: str, dummy_drf_request
    ):
        # Arrange
        url = random_url

        # Act
        serializer_1 = FeedModelSerializer(
            data={"url": url}, context={"request": dummy_drf_request}
        )
        serializer_2 = FeedModelSerializer(
            data={"url": url}, context={"request": dummy_drf_request}
        )

        # Assert
        serializer_1_is_valid = serializer_1.is_valid()
        assert serializer_1_is_valid
        serializer_1.save()

        with pytest.raises(exceptions.ValidationError) as err_info:
            serializer_2.is_valid(raise_exception=True)

        assert err_info.type == exceptions.ValidationError
        assert err_info.value.args[0]["non_field_errors"] == [
            "You've already registered a feed with this url before."
        ]


class TestItemDynamicFieldsModelSerializer:
    def test__item_serializer__given_valid_item__should_return_expected_fields(
        self, item_instance: Item
    ):
        serializer = ItemDynamicFieldsModelSerializer(item_instance)

        assert set(serializer.data.keys()) == {
            "id",
            "title",
            "description",
            "status",
            "published_at",
            "updated_at",
            "created_at",
            "feed",
        }

    def test__dynamic_item_serializer__using_exclude_field__should_not_return_at_expected_fields(
        self, item_instance: Item
    ):
        excluded_fields = ("feed",)
        serializer = ItemDynamicFieldsModelSerializer(item_instance, exclude=excluded_fields)

        assert set(excluded_fields) not in set(serializer.data.keys())

    def test__dynamic_item_serializer___using_custom_fields__should_return_only_included_fields(
        self, item_instance: Item
    ):
        included_fields = ("id", "title")

        serializer = ItemDynamicFieldsModelSerializer(
            item_instance, fields=included_fields
        )

        assert set(included_fields) == set(serializer.data.keys())
