import pytest
from rest_framework.exceptions import ErrorDetail

from rss_scraper.feeds.api.serializers import FeedModelSerializer

pytestmark = pytest.mark.django_db


class TestFeedModelSerializer:
    def test__feed_serializer__given_valid_url__should_pass_validations(
        self, random_url: str, dummy_drf_request
    ):
        # Act
        serializer = FeedModelSerializer(
            data={"url": random_url}, context={"request": dummy_drf_request}
        )

        # Assert
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

        assert serializer.is_valid() is False
        assert serializer.errors.keys() == {"url"}
        assert serializer.errors["url"] == [
            ErrorDetail(string="This field is required.", code="required")
        ]

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
        assert serializer_1.is_valid()
        serializer_1.save()

        assert serializer_2.is_valid() is False
        assert serializer_2.errors.keys() == {"non_field_errors"}
        assert serializer_2.errors["non_field_errors"] == [
            ErrorDetail(
                string="You've already registered a feed with this url before.",
                code="unique",
            )
        ]
