import django_filters as filters
from django_filters.rest_framework import FilterSet


class IngredientFilter(FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')


class RecipeFilter(FilterSet):
    pass
