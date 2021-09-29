import pytest
from api.models import IngredientInRecipe, Recipe, Ingredient, Tag, Subscription
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


EMAIL = 'test.user@mail.com'
PASSWORD = 'TestUserPassword'
USERNAME = 'TestUser'
FIRST_NAME = 'TestUserFirstName'
LAST_NAME = 'TestUserLastName'
EMAIL_OTHER = 'test@mail_other'
PASSWORD_OTHER = 'TestUserPasswordOther'
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
def user_credentials():
    return {
        'email': EMAIL,
        'username': USERNAME,
        'password': PASSWORD,
        'first_name': FIRST_NAME,
        'last_name': LAST_NAME,
    }


@pytest.fixture()
def setup_user(django_user_model, user_credentials):
    return django_user_model.objects.create_user(**user_credentials)


@pytest.fixture()
def setup_user_other(django_user_model):
    return django_user_model.objects.create_user(
        email=EMAIL_OTHER,
        password=PASSWORD_OTHER,
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


@pytest.fixture()
def setup_ingredient_in_recipe(setup_recipe, setup_ingredient):
    return IngredientInRecipe.objects.create(
        ingredient=setup_ingredient,
        recipe=setup_recipe,
        amount=INGREDIENT_AMOUNT,
    )


@pytest.fixture()
def guest_client():
    return APIClient()


@pytest.fixture()
def user_client(setup_user, db):
    token = Token.objects.create(user=setup_user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    return client


@pytest.fixture()
def user_client_other(setup_user_other, db):
    token = Token.objects.create(user=setup_user_other)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    return client


@pytest.fixture()
def user_client_recipe_in_cart(setup_user, setup_recipe, db):
    client = APIClient()
    client.force_authenticate(user=setup_user)
    setup_user.shopping_cart_recipes.add(setup_recipe)
    return client


@pytest.fixture()
def user_client_recipe_in_favorite(setup_user, setup_recipe, db):
    client = APIClient()
    client.force_authenticate(user=setup_user)
    setup_user.favorite_recipes.add(setup_recipe)
    return client
