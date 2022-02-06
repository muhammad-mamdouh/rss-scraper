from django.db.models import QuerySet
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from rss_scraper.feeds.api.serializers import FeedModelSerializer
from rss_scraper.feeds.models import Feed


class FeedViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    """
    Generic viewset to handle feed API endpoints.

    Retrieve action:
        - Returns a feed instance created by the authenticated user.

    List action:
        - Returns paginated list of feeds created by the authenticated user.

    TODO: Use caching at list and retrieve API endpoints, also invalidate it at every DB write.
    """

    serializer_class = FeedModelSerializer
    queryset = Feed.objects.all()

    def get_queryset(self) -> QuerySet:
        """
        :return: Feeds created by the authenticated user.
        """
        return self.queryset.filter(user=self.request.user)
