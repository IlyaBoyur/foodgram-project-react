from django.urls import reverse
import pytest


TOKEN_LOGIN_URL = reverse('token_login')
TOKEN_LOGOUT_URL = reverse('token_logout')
USERS_URL = reverse('users-list')
USERS_ME_URL = reverse('users-me')
USERS_SET_PASSWORD_URL = reverse('users-set-password')
INGREDIENTS_URL = reverse('ingredients-list')
TAGS_URL = reverse('tags-list')
RECIPES_URL = reverse('recipes-list')


@pytest.mark.django_db
def test_users_url_exists_at_desired_location(guest_client, user_client,
                                              setup_user, subtests):
    """Страницы возвращают ожидаемый код ответа соответствующему клиенту."""
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
        with subtests.test(url=url):
            assert client.get(url).status_code == response_code


@pytest.mark.django_db
def test_ingredients_url_exists_at_desired_location(guest_client,
                                                    setup_ingredient,
                                                    subtests):
    """Страницы возвращают ожидаемый код ответа соответствующему клиенту."""
    INGREDIENTS_DETAIL_URL = reverse('ingredients-detail',
                                     args=[setup_ingredient.id])
    urls = [
        [INGREDIENTS_URL, guest_client, 200],
        [INGREDIENTS_DETAIL_URL, guest_client, 200],
    ]
    for url, client, response_code in urls:
        with subtests.test(url=url):
            assert client.get(url).status_code == response_code


@pytest.mark.django_db
def test_tags_url_exists_at_desired_location(guest_client,
                                             setup_tag,
                                             subtests):
    """Страницы возвращают ожидаемый код ответа соответствующему клиенту."""
    TAGS_DETAIL_URL = reverse('tags-detail', args=[setup_tag.id])
    TAGS_DETAIL_NON_EXISTS_URL = reverse('tags-detail', args=[100500])
    urls = [
        [TAGS_URL, guest_client, 200],
        [TAGS_DETAIL_URL, guest_client, 200],
        [TAGS_DETAIL_NON_EXISTS_URL, guest_client, 404],
    ]
    for url, client, response_code in urls:
        with subtests.test(url=url):
            assert client.get(url).status_code == response_code


@pytest.mark.django_db
def test_recipes_url_exists_at_desired_location(guest_client,
                                                user_client,
                                                setup_recipe,
                                                subtests):
    """Страницы возвращают ожидаемый код ответа соответствующему клиенту."""
    RECIPES_DETAIL_URL = reverse('recipes-detail', args=[setup_recipe.id])
    RECIPES_SHOPPING_CART = reverse('recipes-shopping-cart',
                                    args=[setup_recipe.id])
    RECIPES_NON_EXISTS_SHOPPING_CART = reverse('recipes-shopping-cart',
                                               args=[100500])
    RECIPES_FAVORITE = reverse('recipes-favorite',
                               args=[setup_recipe.id])
    RECIPES_NON_EXISTS_FAVORITE = reverse('recipes-favorite',
                                          args=[100500])
    urls = [
        [RECIPES_URL, guest_client, 200],
        [RECIPES_DETAIL_URL, guest_client, 200],
        [RECIPES_SHOPPING_CART, user_client, 201],
        [RECIPES_NON_EXISTS_SHOPPING_CART, user_client, 404],
        [RECIPES_FAVORITE, user_client, 201],
        [RECIPES_NON_EXISTS_FAVORITE, user_client, 404],
    ]
    for url, client, response_code in urls:
        with subtests.test(url=url):
            assert client.get(url).status_code == response_code
