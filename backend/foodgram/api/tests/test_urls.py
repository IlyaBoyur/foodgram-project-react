from django.urls import reverse
import pytest


TOKEN_LOGIN_URL = reverse('token_login')
TOKEN_LOGOUT_URL = reverse('token_logout')
USERS_URL = reverse('users-list')
USERS_ME_URL = reverse('users-me')
USERS_SET_PASSWORD_URL = reverse('users-set-password')


@pytest.mark.django_db
def test_users_url_exists_at_desired_location(guest_client, user_client,
                                              setup_user):
        """Страницы возвращают ожидаемый код ответа
        соответствующему клиенту."""
        USERS_DETAIL_URL = reverse('users-detail',
                                   args=[setup_user.id])
        USERS_DETAIL_NON_EXISTS_URL = reverse('users-detail',
                                              args=[100])
        urls = [
            [USERS_URL, guest_client, 200],
            [USERS_URL, user_client, 200],
            [USERS_DETAIL_URL, guest_client, 401],
            [USERS_DETAIL_URL, user_client, 200],
            [USERS_DETAIL_NON_EXISTS_URL, guest_client, 401],
            [USERS_DETAIL_NON_EXISTS_URL, user_client, 404],
            [USERS_ME_URL, guest_client, 401],
            [USERS_ME_URL, user_client, 200],
        ]
        for url, client, response_code in urls:
                assert client.get(url).status_code == response_code
