from django.db.models import QuerySet
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from rss_scraper.feeds.api.serializers import FeedModelSerializer
from rss_scraper.feeds.models import Feed


class FeedViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    Generic viewset to handle feed API endpoints.

    List action:
        - Returns paginated list of feeds created by the authenticated user.
    """

    serializer_class = FeedModelSerializer
    queryset = Feed.objects.all()

    def get_queryset(self) -> QuerySet:
        """
        :return: Feeds created by the authenticated user.
        """
        return self.queryset.filter(user=self.request.user)
