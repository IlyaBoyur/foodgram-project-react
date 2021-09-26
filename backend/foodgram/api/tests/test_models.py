def test_user_verbose_names(setup_user):
    """User: verbose_name в полях совпадает с ожидаемым"""
    field_verboses = {
        'email': 'Адрес электронной почты',
        'username': 'Уникальный юзернейм',
        'first_name': 'Имя',
        'last_name': 'Фамилия',
        'shopping_cart_recipes': 'Корзина',
        'favorite_recipes': 'Избранное',
    }
    verbose_name = 'Пользователь'
    verbose_name_plural = 'Пользователи'
    for field, value in field_verboses.items():
        assert setup_user._meta.get_field(field).verbose_name == value
    assert setup_user._meta.verbose_name == verbose_name
    assert setup_user._meta.verbose_name_plural == verbose_name_plural


def test_subscription_verbose_names(setup_subscription):
    """Subscription: verbose_name в полях совпадает с ожидаемым"""
    field_verboses = {
        'author': 'Автор',
        'subscriber': 'Подписчик',
    }
    verbose_name = 'Подписка'
    verbose_name_plural = 'Подписки'
    for field, value in field_verboses.items():
        assert setup_subscription._meta.get_field(field).verbose_name == value
    assert setup_subscription._meta.verbose_name == verbose_name
    assert setup_subscription._meta.verbose_name_plural == verbose_name_plural
    assert str(setup_subscription) == (
        f'{setup_subscription.subscriber.username} -> '
        f'{setup_subscription.author.username}'
    )


def test_tag_verbose_names(setup_tag):
    """Tag: verbose_name в полях совпадает с ожидаемым"""
    field_verboses = {
        'name': 'Название',
        'color': 'Цвет в HEX',
        'slug': 'Уникальный слаг',
    }
    verbose_name = 'Тэг'
    verbose_name_plural = 'Тэги'
    for field, value in field_verboses.items():
        assert setup_tag._meta.get_field(field).verbose_name == value
    assert setup_tag._meta.verbose_name == verbose_name
    assert setup_tag._meta.verbose_name_plural == verbose_name_plural
    assert str(setup_tag) == setup_tag.name


def test_ingredient_verbose_names(setup_ingredient):
    """Ingredient: verbose_name в полях совпадает с ожидаемым"""
    field_verboses = {
        'name': 'Название',
        'measurement_unit': 'Единица измерения',
    }
    verbose_name = 'Ингредиент'
    verbose_name_plural = 'Ингредиенты'
    for field, value in field_verboses.items():
        assert setup_ingredient._meta.get_field(field).verbose_name == value
    assert setup_ingredient._meta.verbose_name == verbose_name
    assert setup_ingredient._meta.verbose_name_plural == verbose_name_plural
    assert str(setup_ingredient) == (
        f'{setup_ingredient.name}, {setup_ingredient.measurement_unit}'
    )


def test_recipe_verbose_names(setup_recipe):
    """Recipe: verbose_name в полях совпадает с ожидаемым"""
    field_verboses = {
        'author': 'Автор рецепта',
        'name': 'Название',
        'image': 'Ссылка на картинку на сайте',
        'text': 'Описание',
        'cooking_time': 'Время приготовления (в минутах)',
        'ingredients': 'Список ингредиентов',
    }
    verbose_name = 'Рецепт'
    verbose_name_plural = 'Рецепты'
    for field, value in field_verboses.items():
        assert setup_recipe._meta.get_field(field).verbose_name == value
    assert setup_recipe._meta.verbose_name == verbose_name
    assert setup_recipe._meta.verbose_name_plural == verbose_name_plural
    assert str(setup_recipe) == setup_recipe.name

