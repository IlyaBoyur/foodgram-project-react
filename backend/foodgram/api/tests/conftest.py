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
