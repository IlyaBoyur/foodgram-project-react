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
    for field, value in field_verboses.items():
        assert setup_user._meta.get_field(field).verbose_name == value
    assert setup_user._meta.verbose_name == 'Пользователь'
    assert setup_user._meta.verbose_name_plural == 'Пользователи'


def test_subscription_verbose_names(setup_subscription):
    """Subscription: verbose_name в полях совпадает с ожидаемым"""
    field_verboses = {
        'author': 'Автор',
        'subscriber': 'Подписчик',
    }
    for field, value in field_verboses.items():
        assert setup_subscription._meta.get_field(field).verbose_name == value
    assert setup_subscription._meta.verbose_name == 'Подписка'
    assert setup_subscription._meta.verbose_name_plural == 'Подписки'
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
    for field, value in field_verboses.items():
        assert setup_tag._meta.get_field(field).verbose_name == value
    assert setup_tag._meta.verbose_name == 'Тэг'
    assert setup_tag._meta.verbose_name_plural == 'Тэги'
    assert str(setup_tag) == setup_tag.name


def test_ingredient_verbose_names(setup_ingredient):
    """Ingredient: verbose_name в полях совпадает с ожидаемым"""
    field_verboses = {
        'name': 'Название',
        'measurement_unit': 'Единица измерения',
    }
    for field, value in field_verboses.items():
        assert setup_ingredient._meta.get_field(field).verbose_name == value
    assert setup_ingredient._meta.verbose_name == 'Ингредиент'
    assert setup_ingredient._meta.verbose_name_plural == 'Ингредиенты'
    assert str(setup_ingredient) == (
        f'{setup_ingredient.name}, {setup_ingredient.measurement_unit}'
    )


def test_ingredient_in_recipe_verbose_names(setup_ingredient_in_recipe):
    """Ingredient: verbose_name в полях совпадает с ожидаемым"""
    field_verboses = {
        'ingredient': 'Ингредиент',
        'recipe': 'Рецепт',
    }
    for field, value in field_verboses.items():
        assert (
            setup_ingredient_in_recipe._meta.get_field(field).verbose_name == (
                value
            )
        )
    assert setup_ingredient_in_recipe._meta.verbose_name == (
        'Ингредиент в рецепте'
    )
    assert setup_ingredient_in_recipe._meta.verbose_name_plural == (
        'Ингредиенты в рецептах'
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
        'pub_date': 'Дата публикации',
    }
    for field, value in field_verboses.items():
        assert setup_recipe._meta.get_field(field).verbose_name == value
    assert setup_recipe._meta.verbose_name == 'Рецепт'
    assert setup_recipe._meta.verbose_name_plural == 'Рецепты'
    assert str(setup_recipe) == setup_recipe.name
