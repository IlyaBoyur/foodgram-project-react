from django.urls import reverse


def test_routes(setup_user, setup_ingredient, setup_tag, setup_recipe,
                subtests):
    """URL-адрес, рассчитанный через имя,
    соответствует ожидаемому видимому URL."""
    routes = {
        # Static URLs
        '/api/auth/token/login': reverse('login'),
        '/api/auth/token/logout': reverse('logout'),
        '/api/users/': reverse('users-list'),
        '/api/users/me/': reverse('users-me'),
        '/api/users/set_password/': reverse('users-set-password'),
        '/api/ingredients/': reverse('ingredients-list'),
        '/api/tags/': reverse('tags-list'),
        '/api/recipes/': reverse('recipes-list'),
        # Non static generated URLs
        f'/api/users/{setup_user.id}/': reverse('users-detail',
                                                args=[setup_user.id]),
        f'/api/ingredients/{setup_ingredient.id}/':
            reverse('ingredients-detail', args=[setup_ingredient.id]),
        f'/api/tags/{setup_tag.id}/': reverse('tags-detail',
                                              args=[setup_tag.id]),
        f'/api/recipes/{setup_recipe.id}/': reverse('recipes-detail',
                                                    args=[setup_recipe.id]),
    }
    for url, reversed_url in routes.items():
        with subtests.test(url=url, reversed_url=reversed_url):
            assert url == reversed_url
