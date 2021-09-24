from django.urls import reverse


def test_routes(setup_user, subtests):
    """URL-адрес, рассчитанный через имя,
    соответствует ожидаемому видимому URL."""
    routes = {
        # Static URLs
        '/api/auth/token/login/': reverse('token_login'),
        '/api/auth/token/logout/': reverse('token_logout'),
        '/api/users/': reverse('users-list'),
        '/api/users/me/': reverse('users-me'),
        '/api/users/set_password/': reverse('users-set-password'),
        # Non static generated URLs
        f'/api/users/{setup_user.id}/': reverse('users-detail',
                                                args=[setup_user.id]),
    }
    for url, reversed_url in routes.items():
        with subtests.test(url=url, reversed_url=reversed_url):
            assert url == reversed_url
