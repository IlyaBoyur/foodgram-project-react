from django.contrib.auth import get_user_model
from django.db.models import Count, Q, Value
from django.db.models.fields import BooleanField
from django.db.models.functions import Cast
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser import views as djoser_views
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse, request
from api.filters import IngredientFilter, RecipeFilter
from api.models import Ingredient, Recipe, Subscription, Tag
from api.paginators import PageLimitPagination
from api.serializers import (IngredientSerializer, RecipeSerializer, RecipePartialSerializer, UserSubscribeSerializer,
                             TagSerializer)
from rest_framework.permissions import IsAuthenticated
from wsgiref.util import FileWrapper
from foodgram.settings import SHOPPING_CART_DIR


ERROR_RECIPE_IN_SHOPPING_CART = 'Рецепт {recipe} уже в корзине.'
ERROR_RECIPE_NOT_IN_SHOPPING_CART = 'Рецепта {recipe} нет в корзине.'
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
        return (super().get_queryset().annotate(is_subscribed=Case(
            When(id__in=self.request.user.subscribed_to.values('author_id'),
                 then=True),
            default=False
        )) if not self.request.user.is_anonymous
        else super().get_queryset().annotate(is_subscribed=Value(
            False,
            output_field=BooleanField()
        ))
        )

    @action(["get"], detail=False)
    def me(self, request, *args, **kwargs):
        return Response(
            self.get_serializer(
                get_object_or_404(self.get_queryset(),
                                  id=request.user.id)
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
        if request.user==author:
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


class TokenCreateView(djoser_views.TokenCreateView):
    def _action(self, serializer):
        response = super()._action(serializer)
        response.status_code = status.HTTP_201_CREATED
        return response


class TokenDestroyView(djoser_views.TokenDestroyView):
    def post(self, request):
        response = super().post(request)
        response.status_code = status.HTTP_201_CREATED
        return response


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = PageLimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        return (
            Recipe.objects.annotate(
            is_favorited=Cast(
                Count('users_have_in_favorite',
                      filter=Q(users_have_in_favorite=self.request.user)),
                output_field=BooleanField()),
            is_in_shopping_cart=Cast(
                Count('users_have_in_shopping_cart',
                      filter=Q(users_have_in_shopping_cart=self.request.user)),
                output_field=BooleanField())
            ).select_related('author').prefetch_related('tags','ingredients')
            if not self.request.user.is_anonymous
            else Recipe.objects.annotate(
            is_favorited=Value(False, output_field=BooleanField()),
            is_in_shopping_cart=Value(False, output_field=BooleanField()),
            ).select_related('author').prefetch_related('tags','ingredients')
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
        cart = open(create_shop_list(SHOPPING_CART_DIR
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
                data={'errors': ERROR_RECIPE_IN_SHOPPING_CART.format(recipe=recipe)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        request.user.shopping_cart_recipes.add(recipe)
        return Response(self.get_serializer(recipe).data,
                        status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_from_shopping_cart(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=kwargs.get('pk'))
        if not request.user.shopping_cart_recipes.filter(pk=recipe.pk).exists():
            return Response(
                data={'errors': ERROR_RECIPE_NOT_IN_SHOPPING_CART.format(recipe=recipe)},
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
                data={'errors': ERROR_RECIPE_IN_FAVORITE.format(recipe=recipe)},
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
                data={'errors': ERROR_RECIPE_NOT_IN_FAVORITE.format(recipe=recipe)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        request.user.favorite_recipes.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        if self.action in ('shopping_cart', 'favorite'):
            return RecipePartialSerializer
        return RecipeSerializer
