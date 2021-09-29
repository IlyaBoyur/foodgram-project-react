import pytest
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from api.models import Ingredient, Tag


User = get_user_model()

TOKEN_LOGIN_URL = reverse('token_login')
TOKEN_LOGOUT_URL = reverse('token_logout')
USERS_URL = reverse('users-list')
USERS_SET_PASSWORD_URL = reverse('users-set-password')
USERS_ME_URL = reverse('users-me')
INGREDIENTS_URL = reverse('ingredients-list')
TAGS_URL = reverse('tags-list')


# Users
def get_user_by_client(client):
    return Token.objects.get(
        key=client._credentials['HTTP_AUTHORIZATION'][6:]
    ).user


def assert_user_schema(schema, user, is_registration=False):
    assert schema['id'] == user.id
    assert schema['email'] == user.email
    assert schema['username'] == user.username
    assert schema['first_name'] == user.first_name
    assert schema['last_name'] == user.last_name
    assert schema.get('password') is None
    if not is_registration:
        assert schema['is_subscribed'] == False


@pytest.mark.django_db
def test_users_list(guest_client, setup_user, setup_user_other):
    """Запрос списка пользователей возвращает ожидаемые данные."""
    response = guest_client.get(USERS_URL)
    assert 2 == response.data['count']
    assert 'previous' in response.data
    assert 'next' in response.data
    assert response.data['results'][0]['id'] == setup_user.id
    assert response.data['results'][1]['id'] == setup_user_other.id


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
def test_users_registered_guest_can_login(user_client, user_credentials):
    """Запрос на авторизацию возвращает ожидаемые данные."""
    user_client.credentials()
    response = user_client.post(TOKEN_LOGIN_URL,
                                {
                                    'email': user_credentials['email'],
                                    'password': user_credentials['password'],
                                },
                                format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert Token.objects.get(key=response.data["auth_token"]).user.email == (
        user_credentials['email']
    )

    
@pytest.mark.django_db
def test_users_authenticated_user_can_logout(user_client):
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


# Ingredients
@pytest.mark.django_db
def test_ingredients_list(setup_ingredient, guest_client):
    """Запрос списка ингредиентов возвращает ожидаемые данные."""
    assert 1 == Ingredient.objects.count()
    assert guest_client.get(INGREDIENTS_URL).data[0]['id'] == (
        setup_ingredient.id
    )


@pytest.mark.django_db
def test_ingredients_by_id(setup_ingredient, guest_client):
    """Запрос ингредиента по ID возвращает ожидаемые данные."""
    INGREDIENTS_DETAIL_URL = reverse('ingredients-detail',
                                     args=[setup_ingredient.id])
    response = guest_client.get(INGREDIENTS_DETAIL_URL, format='json')
    assert response.data['id'] == setup_ingredient.id
    assert  response.data['name'] == setup_ingredient.name
    assert response.data['measurement_unit'] == (
        setup_ingredient.measurement_unit
    )


# Tags
@pytest.mark.django_db
def test_tags_list(setup_tag, guest_client):
    """Запрос списка тэгов возвращает ожидаемые данные."""
    assert 1 == Tag.objects.count()
    assert guest_client.get(TAGS_URL).data[0]['id'] == setup_tag.id


@pytest.mark.django_db
def test_tags_by_id(setup_tag, guest_client):
    """Запрос тэга по ID возвращает ожидаемые данные."""
    TAGS_DETAIL_URL = reverse('tags-detail', args=[setup_tag.id])
    response = guest_client.get(TAGS_DETAIL_URL, format='json')
    assert response.data['id'] == setup_tag.id
    assert  response.data['name'] == setup_tag.name
    value = hex(setup_tag.color)[2:].upper()
    assert response.data['color'] == '#' + '0'*(6-len(value)) + value
    assert response.data['slug'] == setup_tag.slug


@pytest.mark.django_db
def test_tags_by_id_non_exists(guest_client):
    """Запрос несуществующего тэга по ID возвращает ожидаемые данные."""
    TAGS_DETAIL_NON_EXISTS_URL = reverse('tags-detail', args=[100500])
    response = guest_client.get(TAGS_DETAIL_NON_EXISTS_URL, format='json')
    assert response.data.get('detail') is not None


def test_recipes_favorite(user_client, setup_recipe):
    """Авторизованный пользователь может добавить Рецепт в избранное."""
    RECIPES_FAVORITE = reverse('recipes-favorite',
                               args=[setup_recipe.id])
    assert (
        user_client.get(RECIPES_FAVORITE).data['id']
        in get_user_by_client(user_client).favorite_recipes.values_list(
            'id',
            flat=True,
        )
    )


def test_recipes_favorite_delete(user_client_recipe_in_favorite,
                                      setup_recipe):
    """Авторизованный пользователь может удалить Рецепт из избранного."""
    RECIPES_FAVORITE = reverse('recipes-favorite',
                               args=[setup_recipe.id])
    assert (
        user_client_recipe_in_favorite.delete(RECIPES_FAVORITE).status_code
        == status.HTTP_204_NO_CONTENT
    )


def test_recipes_favorite_add_twice(user_client_recipe_in_favorite,
                                    setup_recipe):
    """Рецепт нельзя добавить Рецепт в избранное повторно."""
    RECIPES_FAVORITE = reverse('recipes-favorite',
                               args=[setup_recipe.id])
    assert (
        user_client_recipe_in_favorite.get(RECIPES_FAVORITE).status_code
        == status.HTTP_400_BAD_REQUEST
    )


def test_recipes_favorite_delete_twice(user_client, setup_recipe):
    """Рецепт нельзя удалить Рецепт из избранного, если его там нет."""
    RECIPES_FAVORITE = reverse('recipes-favorite',
                               args=[setup_recipe.id])
    assert (
        user_client.delete(RECIPES_FAVORITE).status_code
        == status.HTTP_400_BAD_REQUEST
    )

def test_recipes_shopping_cart(user_client, setup_recipe):
    """Авторизованный пользователь может добавить Рецепт в корзину."""
    RECIPES_SHOPPING_CART = reverse('recipes-shopping-cart',
                                    args=[setup_recipe.id])
    assert (
        user_client.get(RECIPES_SHOPPING_CART, format='json').data['id']
        in get_user_by_client(user_client).shopping_cart_recipes.values_list(
            'id',
            flat=True
        )
    )

def test_recipes_shopping_cart_add_twice(user_client, setup_recipe):
    """Нельзя добавить Рецепт в корзину повторно."""
    RECIPES_SHOPPING_CART = reverse('recipes-shopping-cart',
                                    args=[setup_recipe.id])
    user_client.get(RECIPES_SHOPPING_CART)
    assert (
        user_client.get(RECIPES_SHOPPING_CART).status_code
        == status.HTTP_400_BAD_REQUEST
    )


def test_recipes_shopping_cart_delete(user_client_recipe_in_cart,
                                      setup_recipe):
    """Авторизованный пользователь может удалить Рецепт из корзины."""
    RECIPES_SHOPPING_CART = reverse('recipes-shopping-cart',
                                    args=[setup_recipe.id])
    assert (
        user_client_recipe_in_cart.delete(RECIPES_SHOPPING_CART).status_code
        == status.HTTP_204_NO_CONTENT
    )


def test_recipes_shopping_cart_delete_twice(user_client, setup_recipe):
    """Нельзя удалить Рецепт из корзины, если его там нет."""
    RECIPES_SHOPPING_CART = reverse('recipes-shopping-cart',
                                    args=[setup_recipe.id])
    assert (
        user_client.delete(RECIPES_SHOPPING_CART).status_code
        == status.HTTP_400_BAD_REQUEST
    )
