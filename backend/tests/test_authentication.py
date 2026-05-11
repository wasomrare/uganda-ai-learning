"""Authentication API tests."""
import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestLogin:
    def test_valid_login(self, api_client, super_admin):
        url = '/api/v1/auth/login/'
        response = api_client.post(url, {'username': 'superadmin_test', 'password': 'TestAdmin@123'})
        assert response.status_code == 200
        data = response.json()
        assert 'access' in data.get('data', {})
        assert 'refresh' in data.get('data', {})

    def test_invalid_credentials(self, api_client, super_admin):
        url = '/api/v1/auth/login/'
        response = api_client.post(url, {'username': 'superadmin_test', 'password': 'WrongPassword'})
        assert response.status_code in (400, 401)

    def test_missing_password(self, api_client):
        url = '/api/v1/auth/login/'
        response = api_client.post(url, {'username': 'someuser'})
        assert response.status_code == 400


@pytest.mark.django_db
class TestTokenRefresh:
    def test_refresh_token(self, api_client, super_admin):
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = str(RefreshToken.for_user(super_admin))
        url = '/api/v1/auth/refresh/'
        response = api_client.post(url, {'refresh': refresh})
        assert response.status_code == 200


@pytest.mark.django_db
class TestLogout:
    def test_logout_requires_auth(self, api_client):
        url = '/api/v1/auth/logout/'
        response = api_client.post(url, {'refresh': 'fake-token'})
        assert response.status_code in (401, 400)

    def test_successful_logout(self, admin_client, super_admin):
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = str(RefreshToken.for_user(super_admin))
        url = '/api/v1/auth/logout/'
        response = admin_client.post(url, {'refresh': refresh})
        assert response.status_code == 200
