from django_filters.rest_framework import FilterSet
import django_filters as filters


class IngredientFilter(FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')


class RecipeFilter(FilterSet):
    pass
