import pytest
from django.urls import reverse
from rest_framework import status

from rss_scraper.users.models import User

pytestmark = pytest.mark.django_db


class TestUserAdmin:
    def test__changelist_view__given_valid_admin_user__should_return_200_ok(self, admin_client):
        url = reverse("admin:users_user_changelist")
        response = admin_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test__changelist_search_view__given_valid_admin_user__should_return_200_ok(self, admin_client):
        url = reverse("admin:users_user_changelist")
        response = admin_client.get(url, data={"q": "test"})

        assert response.status_code == status.HTTP_200_OK

    def test__add_user__given_valid_admin_user__should_return_200_ok(self, admin_client):
        url = reverse("admin:users_user_add")
        response = admin_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        response = admin_client.post(
            url,
            data={
                "username": "test",
                "password1": "My_R@ndom-P@ssw0rd",
                "password2": "My_R@ndom-P@ssw0rd",
            },
        )

        assert response.status_code == 302
        assert User.objects.filter(username="test").exists()

    def test__change_user_view__given_valid_user__should_return_200_ok(self, admin_client):
        user = User.objects.get(username="admin")
        url = reverse("admin:users_user_change", kwargs={"object_id": user.pk})
        response = admin_client.get(url)

        assert response.status_code == status.HTTP_200_OK
