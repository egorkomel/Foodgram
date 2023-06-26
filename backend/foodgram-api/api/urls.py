from api.views import (FavoriteRecipeViewSet, IngredientViewSet,
                       RecipeInShoppingCartViewSet, RecipeViewSet, TagViewSet)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path(
        'recipes/download_shopping_cart/',
        RecipeInShoppingCartViewSet.as_view({
            'get': 'list'
        })
    ),
    path('', include(router.urls)),
    path('recipes/<int:recipe_id>/favorite/', FavoriteRecipeViewSet.as_view({
        'post': 'create',
        'delete': 'destroy',
    })),
    path(
        'recipes/<int:recipe_in_cart>/shopping_cart/',
        RecipeInShoppingCartViewSet.as_view({
            'post': 'create',
            'delete': 'destroy',
        })
    ),
]
