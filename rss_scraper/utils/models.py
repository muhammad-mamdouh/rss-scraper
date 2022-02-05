from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.fields import AutoCreatedField, AutoLastModifiedField


class AbstractTimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    ``created_at`` and ``updated_at`` fields.

    Based on model_utils implementation.

    """

    created_at = AutoCreatedField(_("created_at"))
    updated_at = AutoLastModifiedField(_("updated_at"))

    def save(self, *args, **kwargs):
        """
        Overriding the save method in order to make sure that
        updated_at field is updated even if it is not given as
        a parameter to the update field argument.
        """
        update_fields = kwargs.get("update_fields", None)
        if update_fields:
            kwargs["update_fields"] = set(update_fields).union({"updated_at"})

        super().save(*args, **kwargs)

    class Meta:
        abstract = True
