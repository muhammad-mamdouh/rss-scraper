import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


def test__swagger_ui__given_normal_user__should_be_accessible(client, user):
    url = reverse("api-docs")
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test__swagger_ui__given_anonymous_user__should_not_be_accessible(client):
    url = reverse("api-docs")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
