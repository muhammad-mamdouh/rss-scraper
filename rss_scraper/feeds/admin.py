from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from rss_scraper.feeds.models import Feed


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
    readonly_fields = ("id", "last_update_by_source_at", "updated_at", "created_at")

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
                )
            },
        ),
        (
            _("Important Dates"),
            {"fields": ("last_update_by_source_at", "updated_at", "created_at")},
        ),
    )
