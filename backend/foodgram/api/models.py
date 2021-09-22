from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        'Адрес электронной почты',
        max_length=254,
        unique=True,
    )
    username = models.CharField(
        'Уникальный юзернейм',
        max_length=150,
        validators=(
            validators.RegexValidator(r'^[\w.@+-]+\Z',
                                      message='Введите допустимое имя'),
        ),
        unique=True,
    )
    password = models.CharField(
        'Пароль',
        max_length=150
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
    )
    shopping_cart_recipes = models.ManyToManyField(
        to='Recipe',
        blank=True,
        related_name='users_have_in_shopping_cart',
        verbose_name='Корзина',
    )
    favorite_recipes = models.ManyToManyField(
        to='Recipe',
        blank=True,
        related_name='users_have_in_favorite',
        verbose_name='Избранное',
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = (
            'username',
        )


class Subscription(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор',
    )
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribed_to',
        verbose_name='Подписчик',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = (
            'author',
        )


class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=200,
        unique=True,
    )
    color = models.PositiveIntegerField(
        'Цвет в HEX',
        blank=True,
        null=True,
        validators=(
            validators.MaxValueValidator(0xFFFFFF,
                                         'Превышен максимум для цвета'),
        ),
    )
    slug = models.SlugField(
        'Уникальный слаг',
        max_length=200,
        unique=True,
        validators=(
            validators.RegexValidator(r'^[-a-zA-Z0-9_]+$',
                                      message='Введите допустимый слаг'),
        ),
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = (
            'name',
        )


class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        max_length=200,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=200,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = (
            'name',
        )


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        'Название',
        max_length=200,
    )
    image = models.URLField(
        'Ссылка на картинку на сайте',
    )
    text = models.TextField(
        'Описание',
    )
    cooking_time = models.PositiveIntegerField(
        'Время приготовления (в минутах)',
        validators=(
            validators.MinValueValidator(1, 'Минимальное время: 1 минута'),
        ),
    )
    ingredients = models.ManyToManyField(
        to=Ingredient,
        blank=True,
        through='IngredientInRecipe',
        related_name='recipes',
        verbose_name='Список ингредиентов',
    )
    tags = models.ManyToManyField(
        to=Tag,
        related_name='recipes',
        verbose_name='Список тегов',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = (
            'name',
        )


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
    )
    amount = models.PositiveIntegerField(
        'Количество',
        validators=(
            validators.MinValueValidator(1, 'Минимальное количество: 1'),
        ),
    )

    class Meta:
        ordering = (
            'recipe',
        )
