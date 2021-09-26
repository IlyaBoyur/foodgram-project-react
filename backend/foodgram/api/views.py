from django.contrib.auth import get_user_model
from django.db.models import When, Case, Value
from django.db.models.fields import BooleanField
from django.shortcuts import get_object_or_404
from api.paginators import PageLimitPagination
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from djoser import views as djoser_views
from rest_framework import viewsets
from api.models import Ingredient, Tag, Recipe
from api.serializers import IngredientSerializer, TagSerializer, RecipeSerializer


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


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
