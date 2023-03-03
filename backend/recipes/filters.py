import django_filters.rest_framework as filters
from rest_framework.filters import SearchFilter

from .models import Recipes, Tags


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(field_name='is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart'
    )
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tags.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )

    class Meta:
        model = Recipes
        fields = ('is_favorited', 'is_in_shopping_cart', 'tags', 'author',)


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'
