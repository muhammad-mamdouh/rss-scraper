from unittest.mock import ANY

import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from rss_scraper.users.models import User

pytestmark = pytest.mark.django_db


def test__user_me_api__with_authenticated_user__should_return_user_details(
    api_client: APIClient, user: User
):
    api_client.force_login(user=user)
    response = api_client.get(reverse("api:user-me"))

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "username": user.username,
        "name": user.name,
        "email": user.email,
        "date_joined": ANY,
    }


def test__user_me_api__with_anonymous_user__should_return_403(api_client: APIClient):
    response = api_client.get(reverse("api:user-me"))

    assert response.status_code == status.HTTP_403_FORBIDDEN
