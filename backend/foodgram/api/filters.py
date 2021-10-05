import django_filters as filters
from django_filters.rest_framework import FilterSet

from django.contrib.auth import get_user_model

from .models import Tag

User = get_user_model()


class IngredientFilter(FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')


class RecipeFilter(FilterSet):
    is_favorited = filters.BooleanFilter()
    is_in_shopping_cart = filters.BooleanFilter()
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        conjoined=True,
        queryset=Tag.objects.all(),
    )
