import tempfile

from api.filters import IngredientSearchFilter, RecipeFilter
from api.models import (FavoriteRecipe, Ingredient, Recipe,
                        RecipeInShoppingCart, Tag)
from api.paginations import StandardResultsSetPagination
from api.serializers import (FavoriteRecipeSerializer, GetRecipeSerializer,
                             IngredientSrializer, PostRecipeSerializer,
                             RecipeInShoppingCartSerializer, TagSerializer)
from django.db.models import F, Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, response, status, viewsets
from rest_framework.permissions import AllowAny
from users.models import User


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Ingredient."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSrializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet for Recipe."""

    queryset = Recipe.objects.all()
    pagination_class = StandardResultsSetPagination
    permission_classes = (AllowAny,)
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return GetRecipeSerializer
        return PostRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class FavoriteRecipeViewSet(viewsets.ModelViewSet):
    """Viewset for add/delete recipe into favorites."""

    serializer_class = FavoriteRecipeSerializer
    perimisson_classes = (permissions.IsAuthenticated,)
    queryset = FavoriteRecipe.objects.all()
    http_method_names = ('post', 'delete',)
    lookup_field = 'recipe_id'

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('recipe_id'))
        return serializer.save(
            user=self.request.user,
            recipe=recipe
        )

    def get_serializer_context(self):
        return {
            'recipe_id': self.kwargs['recipe_id'],
            'request': self.request
        }

    def destroy(self, request, *args, **kwargs):
        recipe = get_object_or_404(
            Recipe,
            pk=self.kwargs.get('recipe_id')
        )
        serializer = self.serializer_class
        serializer.destroy(self, self.request.user, recipe.id)
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class RecipeInShoppingCartViewSet(viewsets.ModelViewSet):
    """Viewset for add/delete recipe in shopping cart
    and downloading recipe ingredients shopping list.
    """

    serializer_class = RecipeInShoppingCartSerializer
    perimisson_classes = (permissions.IsAuthenticated,)
    queryset = RecipeInShoppingCart.objects.all()
    http_method_names = ('post', 'delete', 'get', )
    lookup_field = 'recipe_in_cart'

    def perform_create(self, serializer):
        recipe = get_object_or_404(
            Recipe,
            pk=self.kwargs.get('recipe_in_cart')
        )
        return serializer.save(
            user=self.request.user,
            recipe_in_cart=recipe
        )

    def destroy(self, request, *args, **kwargs):
        recipe = get_object_or_404(
            Recipe,
            pk=self.kwargs.get('recipe_in_cart')
        )
        serializer = self.serializer_class
        serializer.destroy(self, self.request.user, recipe.id)
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        """Makes shopping list and send it to user."""
        user = get_object_or_404(User, pk=request.user.id)
        recipes = RecipeInShoppingCart.objects.filter(
            user=user
        ).values_list('recipe_in_cart')
        ingredients_for_recipes_in_cart = Recipe.objects.filter(
            pk__in=recipes
        ).values(
            'ingredients__name', 'ingredients__measurement_unit',
        ).annotate(
            amount=Sum(F('ingredients__in_recipe__amount'))
        ).order_by('ingredients__name')
        try:
            with tempfile.NamedTemporaryFile(
                mode='w',
                encoding='utf-8',
                delete=False,
            ) as shopping_list:
                for ingredient in ingredients_for_recipes_in_cart:
                    shopping_list.write(
                        f"{ingredient['ingredients__name']} "
                        f"{ingredient['ingredients__measurement_unit']} --> "
                        f"{ingredient['amount']}\n"
                    )
            return FileResponse(
                open(shopping_list.name, mode='rb'),
                as_attachment=True,
                filename=f'{user.username}_shopping_list.txt'
            )
        finally:
            shopping_list.close()

    def get_serializer_context(self):
        if self.action in ('list',):
            return {
                'request': self.request
            }
        return {
            'recipe_in_cart': self.kwargs['recipe_in_cart'],
            'request': self.request
        }
