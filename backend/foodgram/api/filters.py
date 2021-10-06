import django_filters as filters
from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet

from .models import Tag

BOOLEAN_TO_RANGE = {
    False: 'exact',
    True: 'gt',
}

User = get_user_model()


class IngredientFilter(FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')


class RecipeFilter(FilterSet):
    is_favorited = filters.BooleanFilter(method='filter_bool_to_range')
    is_in_shopping_cart = filters.BooleanFilter(method='filter_bool_to_range')
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    def filter_bool_to_range(self, queryset, name, value):
        """Select number fieeld differently for `false` and for 'true'"""
        lookup = '__'.join([name, BOOLEAN_TO_RANGE[value]])
        return queryset.filter(**{lookup: 0})
