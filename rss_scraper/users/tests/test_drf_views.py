import pytest
from django.test import RequestFactory

from rss_scraper.users.api.views import UserViewSet
from rss_scraper.users.models import User

pytestmark = pytest.mark.django_db


class TestUserViewSet:
    def test__get_queryset__given_new_user__should_contain_new_user(self, user: User, rf: RequestFactory):
        view = UserViewSet()
        request = rf.get("/fake-url/")
        request.user = user

        view.request = request

        assert user in view.get_queryset()

    def test__user_me_api__given_user__should_return_user_details(self, user: User, rf: RequestFactory):
        view = UserViewSet()
        request = rf.get("/fake-url/")
        request.user = user

        view.request = request

        response = view.me(request)

        assert response.data == {
            "username": user.username,
            "name": user.name,
            "url": f"http://testserver/api/v1/users/{user.username}/",
        }
