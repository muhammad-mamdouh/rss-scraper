from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from rss_scraper.feeds.models import Feed


class FeedModelSerializer(serializers.ModelSerializer):
    """
    Model serializer to serialize and deserialize feed instances.
    """

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Feed
        common_fields = (
            "id",
            "user",
            "title",
            "description",
            "auto_update_is_active",
            "is_followed",
            "image",
            "last_update_by_source_at",
            "updated_at",
            "created_at",
        )
        fields = common_fields + ("url",)
        read_only_fields = common_fields
        validators = [
            UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=("url", "user"),
                message=_("You've already registered a feed with this url before."),
            )
        ]
