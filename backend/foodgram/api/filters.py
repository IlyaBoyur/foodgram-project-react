import django_filters as filters
from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet

from .models import Tag

BOOLEAN_CHOICES = (
    (0, 'False'),
    (1, 'True'),
)

User = get_user_model()


class IngredientFilter(FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')


class RecipeFilter(FilterSet):
    is_favorited = filters.ChoiceFilter(choices=BOOLEAN_CHOICES)
    is_in_shopping_cart = filters.ChoiceFilter(choices=BOOLEAN_CHOICES)
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        conjoined=True,
        queryset=Tag.objects.all(),
    )
