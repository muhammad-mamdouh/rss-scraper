from django.http import HttpRequest


class DisableAdminAddPermission:
    def has_add_permission(self, request: HttpRequest, *args, **kwargs) -> bool:
        return False


class DisableAdminDeletePermission:
    def has_delete_permission(self, request: HttpRequest, *args, **kwargs) -> bool:
        return False
