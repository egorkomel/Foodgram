from api.models import Recipe
from django_filters.rest_framework import BooleanFilter, CharFilter, FilterSet
from rest_framework.filters import SearchFilter


class IngredientSearchFilter(SearchFilter):
    """Custom search filter for Ingredient model."""

    search_param = 'name'


class RecipeFilter(FilterSet):
    """Custom filter for Recipe model."""

    author = CharFilter(field_name='author_id')
    tags = CharFilter(method='get_tags')
    is_favorited = BooleanFilter(method='get_boolean_fields')
    is_in_shopping_cart = BooleanFilter(method='get_boolean_fields')

    class Meta:
        model = Recipe
        fields = ('tags', 'is_favorited', 'is_in_shopping_cart', 'author',)

    def get_boolean_fields(self, queryset, name, value):
        user = self.request.user
        if value:
            if name == 'is_favorited':
                return queryset.filter(in_favorites__user=user)
            if name == 'is_in_shopping_cart':
                return queryset.filter(in_cart__user=user)
        return queryset

    def get_tags(self, queryset, field_name, value):
        if value:
            return queryset.filter(
                tags__slug__in=self.request.query_params.getlist('tags')
            ).distinct()
        return queryset
