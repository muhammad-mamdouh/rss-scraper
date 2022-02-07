from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from rss_scraper.feeds.enums import ItemStatus
from rss_scraper.utils.models import AbstractTimeStampedModel

User = get_user_model()


class Feed(AbstractTimeStampedModel):
    """
    RSS Feed DB Model.

    Stores feed content which will be scraped automatically. Feeds are unique per user.
    Also feeds can be followed and unfollowed by the creator so feeds can be updated automatically
        and (s)he receive updates on the feed content.
    """

    url = models.URLField(help_text=_("Page url given by the user to be scraped."))
    title = models.CharField(
        max_length=255, blank=True, help_text=_("Feed page title.")
    )
    description = models.TextField(blank=True, help_text=_("Feed page description."))
    image = models.URLField(blank=True, help_text=_("Feed page image url"))
    auto_update_is_active = models.BooleanField(
        default=True,
        help_text=_(
            "Determines whether the feed content will be automatically updated in the background periodically."
        ),
    )
    is_followed = models.BooleanField(
        default=True,
        help_text=_(
            "Does this feed followed by the user? so its content will updated and (s)he will be notified."
        ),
    )
    last_update_by_source_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When was the last time this feed updated by the source site."),
    )
    e_tag = models.CharField(
        max_length=255,
        blank=True,
        help_text=_(
            "ETag and Last-Modified Headers aka `last_update_by_source_at` can be used to save resources bandwidth."
        ),
    )

    # relationships
    user = models.ForeignKey(
        User, related_name=_("feeds"), blank=True, null=True, on_delete=models.SET_NULL
    )

    class Meta:
        unique_together = ("url", "user")
        ordering = ("-updated_at",)

    def __str__(self):
        return (
            f"{self.__class__.__name__}(id={self.id}, url={self.url}, user={self.user})"
        )

    def follow(self):
        self.is_followed = True
        self.save()

    def unfollow(self):
        self.is_followed = False
        self.save()

    def activate_auto_update(self):
        self.auto_update_is_active = True
        self.save()


class Item(AbstractTimeStampedModel):
    """
    RSS Feed Item DB Model.

    Items are being created from the scraped feeds content.
    """

    url = models.URLField()
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    status = models.PositiveSmallIntegerField(
        choices=ItemStatus.choices,
        default=ItemStatus.NEW,
        help_text=_(
            "The status of the item. Initially it is at the new state, users can mark it as read."
        ),
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("The date and time at which the item was published."),
    )

    # relationships
    feed = models.ForeignKey(Feed, related_name=_("items"), on_delete=models.CASCADE)

    class Meta:
        ordering = ("-published_at", "-updated_at")

    def __str__(self):
        return (
            f"{self.__class__.__name__}(id={self.id}, url={self.url}, feed={self.feed})"
        )

    def mark_as_read(self):
        self.status = ItemStatus.READ
        self.save()
