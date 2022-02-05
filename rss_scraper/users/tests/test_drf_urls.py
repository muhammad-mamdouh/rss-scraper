import pytest
from django.urls import resolve, reverse

from rss_scraper.users.models import User

pytestmark = pytest.mark.django_db


def test__user_detail_api_url__given_valid_username__should_resolve_to_detail_api(user: User):
    assert (
        reverse("api:user-detail", kwargs={"username": user.username})
        == f"/api/v1/users/{user.username}/"
    )
    assert resolve(f"/api/v1/users/{user.username}/").view_name == "api:user-detail"


def test__user_list_api_url__given_nothing__should_resolve_to_users_list_api():
    assert reverse("api:user-list") == "/api/v1/users/"
    assert resolve("/api/v1/users/").view_name == "api:user-list"


def test__user_me_api_url__given_nothing__should_resolve_to_user_me_api():
    assert reverse("api:user-me") == "/api/v1/users/me/"
    assert resolve("/api/v1/users/me/").view_name == "api:user-me"
