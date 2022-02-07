import pytest
from django.urls import resolve, reverse

pytestmark = pytest.mark.django_db


def test__user_me_api_url__given_nothing__should_resolve_to_user_me_api():
    assert reverse("api:user-me") == "/api/v1/users/me/"
    assert resolve("/api/v1/users/me/").view_name == "api:user-me"
