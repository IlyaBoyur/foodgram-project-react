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
User = get_user_model()


class UserViewSet(djoser_views.UserViewSet):
    http_method_names = ['get', 'post']
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
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
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
