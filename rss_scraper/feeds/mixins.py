from django.http import HttpRequest
from rest_framework import serializers


class DisableAdminAddPermission:
    def has_add_permission(self, request: HttpRequest, *args, **kwargs) -> bool:
        return False


class DisableAdminDeletePermission:
    def has_delete_permission(self, request: HttpRequest, *args, **kwargs) -> bool:
        return False


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` and/or `exclude` argument that
    controls which fields should be displayed and/or which fields to be excluded.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop("fields", None)
        exclude = kwargs.pop("exclude", [])

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        for field_name in exclude:
            self.fields.pop(field_name)
