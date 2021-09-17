import pytest
from api.models import Recipe, Ingredient, Tag, Subscription


EMAIL = 'test@mail'
USERNAME = 'TestUser'
FIRST_NAME = 'TestUserName'
LAST_NAME = 'TestUserSurname'
EMAIL_OTHER = 'test@mail_other'
USERNAME_OTHER = 'TestUserOther'
FIRST_NAME_OTHER = 'TestUserNameOther'
LAST_NAME_OTHER = 'TestUserSurnameOther'

RECIPE_NAME = 'TestRecipe'
RECIPE_IMAGE = 'http://TestRecipeImage'
RECIPE_TEXT = 'TestRecipeText'
RECIPE_COOKING_TIME = 100500

INGREDIENT_NAME = 'TestIngredient'
INGREDIENT_MU = 'TestUnit'
INGREDIENT_AMOUNT = 42

TAG_NAME = 'TestTag'
TAG_COLOR = 0xFFFFFF
TAG_SLUG = 'test-slug'


@pytest.fixture()
def setup_user(django_user_model):
    return django_user_model.objects.create_user(
        email=EMAIL,
        username=USERNAME,
        first_name=FIRST_NAME,
        last_name=LAST_NAME,
    )


@pytest.fixture()
def setup_user_other(django_user_model):
    return django_user_model.objects.create_user(
        email=EMAIL_OTHER,
        username=USERNAME_OTHER,
        first_name=FIRST_NAME_OTHER,
        last_name=LAST_NAME_OTHER,
    )


@pytest.fixture()
def setup_subscription(setup_user, setup_user_other):
    return Subscription.objects.create(
        author=setup_user,
        subscriber=setup_user_other,
    )


@pytest.fixture()
def setup_ingredient(db):
    return Ingredient.objects.create(
        name=INGREDIENT_NAME,
        measurement_unit=INGREDIENT_MU,
    )


@pytest.fixture()
def setup_tag(db):
    return Tag.objects.create(
        name=TAG_NAME,
        color=TAG_COLOR,
        slug=TAG_SLUG,
    )


@pytest.fixture()
def setup_recipe(setup_user, setup_ingredient, setup_tag):
    recipe = Recipe.objects.create(
        author=setup_user,
        name=RECIPE_NAME,
        image=RECIPE_IMAGE,
        text=RECIPE_TEXT,
        cooking_time=RECIPE_COOKING_TIME,
    )
    recipe.tags.add(setup_tag)
    recipe.ingredients.add(setup_ingredient,
                           through_defaults={'amount': INGREDIENT_AMOUNT})
    return recipe


def test_user_verbose_names(setup_user):
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


def test_tag_verbose_names(setup_tag):
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


def test_ingredient_verbose_names(setup_ingredient):
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


def test_recipe_verbose_names(setup_recipe):
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
