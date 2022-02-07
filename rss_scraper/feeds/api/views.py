from typing import Any

from django.db.models import QuerySet
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from rss_scraper.feeds.api.serializers import (
    FeedModelSerializer,
    ItemDynamicFieldsModelSerializer,
)
from rss_scraper.feeds.enums import ItemStatus
from rss_scraper.feeds.models import Feed, Item


class FeedViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    """
    Generic viewset to handle feed API endpoints.

    Create action:
        - Adds a new feed instance for the authenticated user.

    Retrieve action:
        - Returns a feed instance created by the authenticated user.

    List action:
        - Returns paginated list of feeds created by the authenticated user.

    TODO: Use the background task at the create API endpoint.
    TODO: Use caching at list and retrieve API endpoints, also invalidate it at every DB write.
    """

    serializer_class = FeedModelSerializer
    queryset = Feed.objects.all()

    def get_queryset(self) -> QuerySet:
        """
        :return: Feeds qs created by the authenticated user.
        """
        return self.queryset.filter(user=self.request.user)

    @action(detail=True, methods=["POST"])
    def follow(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Enables authenticated users to follow an unfollowed feed instance.

        :param kwargs:
            - pk (int) which used to get the feed instance from DB.

        :return:
            - `200 OK` if the feed instance is_followed value changed to True.
            - `400 Bad Request` if the feed instance is already followed.
            - `403 Forbidden` if the user is anonymous.
            - `404 Not Found` if provided feed doesn't exist or not created by the authenticated user.
        """
        instance = self.get_object()

        if instance.is_followed:
            raise ValidationError(
                {"non_field_errors": ["You've already followed this feed."]}
            )

        instance.follow()
        return Response(self.get_serializer(instance).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["POST"])
    def unfollow(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Enables authenticated users to stop following a followed feed instance.

        :param kwargs:
            - pk (int) which used to get the feed instance from DB.

        :return:
            - `200 OK` if the feed instance is_followed value changed to False.
            - `400 Bad Request` if the feed instance is already unfollowed.
            - `403 Forbidden` if the user is anonymous.
            - `404 Not Found` if provided feed doesn't exist or not created by the authenticated user.
        """
        instance = self.get_object()

        if not instance.is_followed:
            raise ValidationError(
                {"non_field_errors": ["You've already unfollowed this feed."]}
            )

        instance.unfollow()
        return Response(self.get_serializer(instance).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["PUT"], url_path="force-update")
    def force_update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Enables authenticated users to force update a feed instance.
        Also, if the automatic update is not active for the feed it'll be activated.

        :param kwargs:
            - pk (int) which used to get the feed instance from DB.

        :return:
            - `200 OK` after running a background task to force update a feed instance.
            - `403 Forbidden` if the user is anonymous.
            - `404 Not Found` if provided feed doesn't exist or not created by the authenticated user.
        """
        instance = self.get_object()

        if not instance.auto_update_is_active:
            instance.activate_auto_update()

        # TODO: Call the background task to update the feed content.
        return Response(self.get_serializer(instance).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["GET"])
    def items(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Enables authenticated users to retrieve a paginated list of items related to the passed feed ID.
        Also, if the automatic update is not active for the feed it'll be activated.

        :param kwargs:
            - pk (int) which used to get the feed instance from DB, and then its related items.

        :return:
            - `200 OK`
            - `403 Forbidden` if the user is anonymous.
            - `404 Not Found` if provided feed doesn't exist or not created by the authenticated user.
        """
        instance = self.get_object()
        items_queryset = instance.items.all()

        page = self.paginate_queryset(items_queryset)
        if page is not None:
            serializer = ItemDynamicFieldsModelSerializer(
                page, many=True, exclude=("feed",)
            )
            return self.get_paginated_response(serializer.data)

        serializer = ItemDynamicFieldsModelSerializer(
            items_queryset, many=True, exclude=("feed",)
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


class ItemViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    """
    Generic viewset to handle feed items API endpoints.

    Retrieve action:
        - Returns an item instance of a feed created by the authenticated user.

    List action:
        - Returns paginated list of all the items (globally) of all the feeds registered by the authenticated user.
    """

    serializer_class = ItemDynamicFieldsModelSerializer
    queryset = Item.objects.all()

    def get_queryset(self) -> QuerySet:
        """
        :return: Items qs of all the feeds registered by the authenticated user.
        """
        return self.queryset.filter(feed__user=self.request.user)

    @action(detail=True, methods=["POST"], url_path="mark-as-read")
    def mark_as_read(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Enables authenticated users to change feed item status to be read.

        :param kwargs:
            - pk (int) which used to get the feed item instance from DB.

        :return:
            - `200 OK` if the feed item instance status is new and changed to read.
            - `400 Bad Request` if the feed item instance status is already read.
            - `403 Forbidden` if the user is anonymous.
            - `404 Not Found` if provided feed item doesn't exist or not of a feed created by the authenticated user.
        """
        instance = self.get_object()

        if instance.status == ItemStatus.READ:
            raise ValidationError(
                {"non_field_errors": ["You've already marked this feed item as read."]}
            )

        instance.mark_as_read()
        return Response(self.get_serializer(instance).data, status=status.HTTP_200_OK)
