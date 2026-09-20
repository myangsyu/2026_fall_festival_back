import pytest
from django.test import Client


@pytest.fixture
def auth_headers(settings):
    return {"HTTP_AUTHORIZATION": f"Bearer {settings.ADMIN_API_TOKEN}"}


@pytest.fixture
def client():
    return Client()
