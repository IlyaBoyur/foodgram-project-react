import pytest
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token


User = get_user_model()

TOKEN_LOGIN_URL = reverse('token_login')
TOKEN_LOGOUT_URL = reverse('token_logout')
USERS_URL = reverse('users-list')
USERS_SET_PASSWORD_URL = reverse('users-set-password')
USERS_ME_URL = reverse('users-me')


def assert_user_schema(schema, user, is_registration=False):
    assert schema['id'] == user.id
    assert schema['email'] == user.email
    assert schema['username'] == user.username
    assert schema['first_name'] == user.first_name
    assert schema['last_name'] == user.last_name
    assert None == schema.get('password')
    if not is_registration:
        assert schema['is_subscribed'] == False


@pytest.mark.django_db
def test_users_list(guest_client, setup_user, setup_user_other):
    """Запрос списка пользователей возвращает ожидаемые данные."""
    response = guest_client.get(USERS_URL)
    assert 2 == response.data['count']
    assert 'previous' in response.data
    assert 'next' in response.data
    assert setup_user.username in response.data['results'][0].values()
    assert setup_user_other.username in response.data['results'][1].values()


@pytest.mark.django_db
def test_users_new_account(guest_client, user_credentials):
    """Запрос на регистрацию создает пользователя."""
    assert User.objects.count() == 0
    guest_client.post(USERS_URL, user_credentials, format='json')
    assert User.objects.count() == 1


@pytest.mark.django_db
def test_users_create_account(guest_client, user_credentials):
    """Запрос на регистрацию возвращает ожидаемые данные."""
    response = guest_client.post(USERS_URL, user_credentials, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert_user_schema(
        response.data,
        User.objects.get(username=user_credentials['username']),
        is_registration=True,
    )


@pytest.mark.django_db
def test_users_by_id(setup_user, user_client):
    """Запрос пользователя по ID возвращает ожидаемые данные."""
    USERS_DETAIL_URL = reverse('users-detail',
                                args=[setup_user.id])
    assert_user_schema(
        user_client.get(USERS_DETAIL_URL, format='json').data,
        setup_user
    )


@pytest.mark.django_db
def test_users_me(setup_user, guest_client):
    """Запрос текущего пользователя возвращает ожидаемые данные."""
    guest_client.credentials(
        HTTP_AUTHORIZATION='Token ' + Token.objects.create(user=setup_user).key
    )
    assert_user_schema(
        guest_client.get(USERS_ME_URL, format='json').data,
        setup_user,
    )


@pytest.mark.django_db
def test_users_registered_guest_can_login(setup_user, user_credentials,
                                          guest_client):
    """Запрос на авторизацию возвращает ожидаемые данные."""
    response = guest_client.post(TOKEN_LOGIN_URL,
                                 {
                                     'email': user_credentials['email'],
                                     'password': user_credentials['password'],
                                 },
                                 format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["auth_token"] == (
        Token.objects.get(user=setup_user).key
    )

    
@pytest.mark.django_db
def test_users_registered_guest_can_logout(user_client):
    """Запрос на разлогирование возвращает ожидаемые данные."""
    response = user_client.post(TOKEN_LOGOUT_URL, data=None, format='json')
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_users_set_password(user_client, user_credentials):
    """Запрос на смену пароля возвращает ожидаемые данные."""
    response = user_client.post(
        USERS_SET_PASSWORD_URL,
        {
            'current_password': user_credentials['password'],
            'new_password': 'password_for_this_test_only',
        },
        format='json',
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT