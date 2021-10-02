from wsgiref.util import FileWrapper

from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.db.models.expressions import Value
from django.db.models.fields import IntegerField
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser import views as djoser_views
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from foodgram.settings import SHOPPING_CART_DIR

from .filters import IngredientFilter, RecipeFilter
from .models import Ingredient, Recipe, Subscription, Tag
from .paginators import PageLimitPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeReadPartialSerializer,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          TagSerializer, UserSubscribeSerializer)

ERROR_RECIPE_IN_CART = 'Рецепт {recipe} уже в корзине.'
ERROR_RECIPE_NOT_IN_CART = 'Рецепта {recipe} нет в корзине.'
ERROR_RECIPE_IN_FAVORITE = 'Рецепт {recipe} уже в избранном.'
ERROR_RECIPE_NOT_IN_FAVORITE = 'Рецепта {recipe} нет в избранном.'
ERROR_SUBSCRIBE_SELF = 'Невозможно подписаться на самого себя.'
ERROR_SUBSCRIBE_AGAIN = 'Вы уже подписаны на {author}.'
ERROR_UNSUBSCRIBE_AGAIN = 'Вы не подписаны на {author}.'
PDF_INGREDIENT_LINE = '{name} ({unit}) - {amount}\n'
PDF_HEAD_LINE = 'Список покупок для {name} {surname}\n\n'
PDF_CELL_WIDTH = 200
PDF_CELL_HEGHT = 10
PDF_ALIGN_CENTER = 'C'
PDF_ALIGN_LEFT = 'L'
PDF_FONT_FAMILY = 'DejaVu'
PDF_FONT_STYLE = ''
PDF_FONT_NAME = 'DejaVuSansCondensed.ttf'

User = get_user_model()


class UserViewSet(djoser_views.UserViewSet):
    http_method_names = ['get', 'post', 'delete']
    pagination_class = PageLimitPagination

    def get_queryset(self):
        return (
            super().get_queryset().annotate(
                is_subscribed=Count(
                    'subscribers',
                    filter=Q(subscribers__subscriber=self.request.user)
                ),
            ) if self.request.user.is_authenticated
            else super().get_queryset().annotate(
                is_subscribed=Value(0, output_field=IntegerField())
            )
        )

    def get_serializer_class(self):
        if self.action in ('subscriptions', 'subscribe'):
            return UserSubscribeSerializer
        return super().get_serializer_class()

    @action(["get"], detail=False)
    def me(self, request, *args, **kwargs):
        return Response(
            self.get_serializer(
                get_object_or_404(self.get_queryset(), id=request.user.id)
            ).data
        )

    def destroy(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(('get',), detail=False,
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request, *args, **kwargs):
        queryset = self.filter_queryset(
            self.get_queryset().filter(
                id__in=request.user.subscribed_to.values('author_id')
            )
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(
                self.get_serializer(page, many=True).data
            )
        return Response(self.get_serializer(queryset, many=True).data)

    @action(('get',), detail=True,
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, *args, **kwargs):
        author = get_object_or_404(User, id=kwargs.get('id'))
        if request.user == author:
            return Response(
                data={'errors': ERROR_SUBSCRIBE_SELF},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.user.subscribed_to.filter(author=author).exists():
            return Response(
                data={'errors': ERROR_SUBSCRIBE_AGAIN.format(author=author)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        Subscription.objects.create(author=author, subscriber=request.user)
        return Response(
            self.get_serializer(author).data,
            status=status.HTTP_201_CREATED,
        )

    @subscribe.mapping.delete
    def delete_subscription(self, request, *args, **kwargs):
        author = get_object_or_404(User, id=kwargs.get('id'))
        if not request.user.subscribed_to.filter(author=author).exists():
            return Response(
                data={'errors': ERROR_UNSUBSCRIBE_AGAIN.format(author=author)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        Subscription.objects.filter(
            subscriber=request.user,
            author=author,
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrReadOnly, IsAuthenticatedOrReadOnly)
    pagination_class = PageLimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        return (
            Recipe.objects.annotate(
                is_favorited=Count(
                    'users_have_in_favorite',
                    filter=Q(users_have_in_favorite=self.request.user)
                ),
                is_in_shopping_cart=Count(
                    'users_have_in_shopping_cart',
                    filter=Q(users_have_in_shopping_cart=self.request.user)
                )
            ).prefetch_related('tags', 'ingredients')
            if self.request.user.is_authenticated
            else Recipe.objects.annotate(
                is_favorited=Value(0, output_field=IntegerField()),
                is_in_shopping_cart=Value(0, output_field=IntegerField()),
            ).prefetch_related('tags', 'ingredients')
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        return Response(
            RecipeReadSerializer(
                self.get_queryset().get(id=serializer.instance.id),
            ).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance,
                                         data=request.data,
                                         partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            RecipeReadSerializer(
                self.get_queryset().get(id=serializer.instance.id),
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(('get',), detail=False,
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request, *args, **kwargs):
        def create_shop_list(pdf_name):
            ingredients = {}
            for recipe in self.get_serializer(
                self.get_queryset().filter(is_in_shopping_cart=True),
                many=True,
            ).data:
                for ingredient in recipe['ingredients']:
                    name = ingredient["name"]
                    unit = ingredient["measurement_unit"]
                    amount = ingredients.setdefault((name, unit), 0)
                    ingredients[(name, unit)] = amount + ingredient["amount"]

            from fpdf import FPDF
            pdf = FPDF()
            pdf.add_page()
            pdf.add_font(PDF_FONT_FAMILY,
                         PDF_FONT_STYLE,
                         PDF_FONT_NAME,
                         uni=True)
            pdf.set_font(PDF_FONT_FAMILY, size=14)
            pdf.multi_cell(
                PDF_CELL_WIDTH,
                PDF_CELL_HEGHT,
                txt=PDF_HEAD_LINE.format(name=request.user.first_name,
                                         surname=request.user.last_name),
                align=PDF_ALIGN_CENTER
            )
            for name, unit, amount in ((key, value, ingredients[key, value])
                                       for key, value in ingredients):
                pdf.multi_cell(
                    PDF_CELL_WIDTH,
                    PDF_CELL_HEGHT,
                    txt=PDF_INGREDIENT_LINE.format(name=name.capitalize(),
                                                   unit=unit,
                                                   amount=str(amount)),
                    align=PDF_ALIGN_LEFT,
                )
            pdf.output(pdf_name)
            return pdf_name
        cart = open(
            create_shop_list(SHOPPING_CART_DIR
                             + f'{request.user.username}_cart.pdf'),
            'rb',
        )
        return HttpResponse(
            FileWrapper(cart),
            status=status.HTTP_200_OK,
        )

    @action(('get',), detail=True,
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=kwargs.get('pk'))
        if request.user.shopping_cart_recipes.filter(pk=recipe.pk).exists():
            return Response(
                data={'errors': ERROR_RECIPE_IN_CART.format(recipe=recipe)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        request.user.shopping_cart_recipes.add(recipe)
        return Response(self.get_serializer(recipe).data,
                        status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_from_shopping_cart(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=kwargs.get('pk'))
        if not request.user.shopping_cart_recipes.filter(
            pk=recipe.pk
        ).exists():
            return Response(
                data={'errors': ERROR_RECIPE_NOT_IN_CART.format(
                    recipe=recipe
                )},
                status=status.HTTP_400_BAD_REQUEST,
            )
        request.user.shopping_cart_recipes.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(('get',), detail=True,
            permission_classes=[IsAuthenticated])
    def favorite(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=kwargs.get('pk'))
        if request.user.favorite_recipes.filter(pk=recipe.pk).exists():
            return Response(
                data={'errors': ERROR_RECIPE_IN_FAVORITE.format(
                    recipe=recipe
                )},
                status=status.HTTP_400_BAD_REQUEST,
            )
        request.user.favorite_recipes.add(recipe)
        return Response(self.get_serializer(recipe).data,
                        status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_from_favorite(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=kwargs.get('pk'))
        if not request.user.favorite_recipes.filter(pk=recipe.pk).exists():
            return Response(
                data={'errors': ERROR_RECIPE_NOT_IN_FAVORITE.format(
                    recipe=recipe
                )},
                status=status.HTTP_400_BAD_REQUEST,
            )
        request.user.favorite_recipes.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        if self.action in ('create', 'update'):
            return RecipeWriteSerializer
        elif self.action in ('shopping_cart', 'favorite'):
            return RecipeReadPartialSerializer
        return RecipeReadSerializer
