from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from rss_scraper.feeds.mixins import (
    DisableAdminAddPermission,
    DisableAdminDeletePermission,
)
from rss_scraper.feeds.models import Feed, Item


@admin.register(Item)
class ItemModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "url",
        "feed",
        "status",
        "published_at",
        "updated_at",
    )
    list_filter = ("status",)
    search_fields = ("id", "url", "title", "feed__id", "feed__title")
    ordering = ("-id",)
    readonly_fields = ("id", "feed", "published_at", "updated_at", "created_at")

    fieldsets = (
        (None, {"fields": ("id", "url", "feed")}),
        (
            "Extra Info",
            {
                "fields": (
                    "title",
                    "description",
                    "status",
                )
            },
        ),
        (
            _("Important Dates"),
            {"fields": ("published_at", "updated_at", "created_at")},
        ),
    )


class ItemModelStackedInline(
    DisableAdminAddPermission, DisableAdminDeletePermission, admin.StackedInline
):
    model = Item
    fields = ("url", "title", "published_at", "updated_at", "created_at")
    readonly_fields = fields
    extra = 0


@admin.register(Feed)
class FeedModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "url",
        "user",
        "auto_update_is_active",
        "is_followed",
        "last_update_by_source_at",
        "updated_at",
    )
    list_filter = ("is_followed", "auto_update_is_active")
    search_fields = ("id", "url", "title", "user__id", "user__email")
    raw_id_fields = ("user",)
    ordering = ("-id",)
    readonly_fields = (
        "id",
        "e_tag",
        "last_update_by_source_at",
        "updated_at",
        "created_at",
    )
    inlines = (ItemModelStackedInline,)

    fieldsets = (
        (None, {"fields": ("id", "url", "user")}),
        (
            "Extra Info",
            {
                "fields": (
                    "title",
                    "description",
                    "image",
                    "is_followed",
                    "auto_update_is_active",
                    "e_tag",
                )
            },
        ),
        (
            _("Important Dates"),
            {"fields": ("last_update_by_source_at", "updated_at", "created_at")},
        ),
    )
