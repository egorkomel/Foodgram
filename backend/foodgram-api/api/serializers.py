from api.fields import Base64ImageField
from api.models import (FavoriteRecipe, Ingredient, Recipe, RecipeIngredient,
                        RecipeInShoppingCart, Tag)
from django.shortcuts import get_object_or_404
from rest_framework import exceptions, permissions, serializers
from users.models import Follow, User


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag model."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSrializer(serializers.ModelSerializer):
    """Serializer for Ingredient model."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Serializer for RecipeIngredientAmount model."""

    id = serializers.IntegerField(source='ingredients.id')
    amount = serializers.IntegerField()
    name = serializers.CharField(source='ingredients.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredients.measurement_unit', read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class UserInfoSerializer(serializers.ModelSerializer):
    """Serializer for info about User."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        """Get is_subscribed field."""
        if not self.context:
            return False
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return Follow.objects.filter(
            user=user,
            following_id=obj.id
        ).exists()


class GetRecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipe model with method GET."""

    author = UserInfoSerializer(
        many=False, read_only=True, default=serializers.CurrentUserDefault()
    )
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients', many=True
    )
    tags = TagSerializer(many=True, required=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    perimisson_classes = (permissions.AllowAny,)
    favorites_count = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
            'pub_date',
            'favorites_count',
        )

    def get_is_favorited(self, obj):
        """Get is_favorited field."""
        if not self.context:
            return False
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return FavoriteRecipe.objects.filter(
            user=user,
            recipe_id=obj.id
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """Get is_in_shopping_cart field."""
        if not self.context:
            return False
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return RecipeInShoppingCart.objects.filter(
            user=user,
            recipe_in_cart=obj.id
        ).exists()

    def get_favorites_count(self, obj):
        """Get the number of additions of recipes to favorites."""
        return FavoriteRecipe.objects.filter(
            recipe=obj
        ).count()


class PostRecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipe model with method POST."""

    author = UserInfoSerializer(
        many=False, default=serializers.CurrentUserDefault()
    )
    ingredients = RecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = Base64ImageField()
    perimisson_classes = (permissions.IsAuthenticated,)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def to_representation(self, instance):
        serializer = GetRecipeSerializer(instance)
        return serializer.data

    def validate(self, data):
        if not self.initial_data['ingredients']:
            raise serializers.ValidationError(
                {"ingredients": "Нужен хотя бы один ингредиент."}
            )
        if not self.initial_data['tags']:
            raise serializers.ValidationError(
                {"tags": "Нужен хотя бы один тег."}
            )
        unique_ingredients_id = []
        ingredients = self.initial_data.get('ingredients')
        for ingredient in ingredients:
            if not Ingredient.objects.filter(pk=ingredient['id']):
                raise serializers.ValidationError(
                    'Такой ингредиент не существует.'
                )
            if ingredient['id'] in unique_ingredients_id:
                raise serializers.ValidationError(
                    'Ингредиент уже добавлен.'
                )
            unique_ingredients_id.append(ingredient['id'])
            if int(ingredient.get('amount')) <= 0:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть больше 0.'
                )
        return data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        recipes_for_create = []
        for ingredient in ingredients:
            current_ingredient = get_object_or_404(
                Ingredient, pk=ingredient.get('ingredients')['id']
            )
            recipes_for_create.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredients=current_ingredient,
                    amount=ingredient['amount']
                )
            )
        RecipeIngredient.objects.bulk_create(recipes_for_create)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        ingredients = validated_data.pop('ingredients')
        RecipeIngredient.objects.filter(recipe=instance).delete()
        recipes_for_update = []
        for ingredient in ingredients:
            current_ingredient = get_object_or_404(
                Ingredient, pk=ingredient.get('ingredients')['id']
            )
            recipes_for_update.append(
                RecipeIngredient(
                    recipe=instance,
                    ingredients=current_ingredient,
                    amount=ingredient['amount']
                )
            )
        RecipeIngredient.objects.bulk_create(recipes_for_update)
        instance.save()
        return instance


class ShortInfoRecipe(serializers.ModelSerializer):
    """Serializer for short info about Recipe."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Serializer for FavoriteRecipe model."""

    recipe = ShortInfoRecipe(read_only=True)
    perimisson_classes = (permissions.IsAuthenticated,)

    class Meta:
        model = FavoriteRecipe
        exclude = ('user',)

    def validate(self, data):
        request = self.context.get('request')
        user = request.user
        if not user.is_authenticated:
            raise exceptions.NotAuthenticated()
        recipe_id = self.context.get('recipe_id')
        favorite = FavoriteRecipe.objects.filter(
            user=user,
            recipe=recipe_id
        )
        if request.method == 'POST':
            if favorite.exists():
                raise serializers.ValidationError(
                    'Уже добавлено избранное.'
                )
        if request.method == 'DELETE':
            if not favorite.exists():
                raise serializers.ValidationError(
                    'Уже убрано из избранного.'
                )
        return data

    def destroy(self, user, recipe_id):
        if not user.is_authenticated:
            raise exceptions.NotAuthenticated()
        recipe = get_object_or_404(
            Recipe,
            pk=recipe_id
        )
        favorite_recipe = FavoriteRecipe.objects.filter(
            user=user,
            recipe=recipe
        )
        if not favorite_recipe.exists():
            raise serializers.ValidationError(
                'Уже убрано из избранного.'
            )
        return favorite_recipe.delete()


class RecipeInShoppingCartSerializer(serializers.ModelSerializer):
    """Serializer for RecipeInShoppingCart model."""

    recipe_in_cart = ShortInfoRecipe(read_only=True)
    perimisson_classes = (permissions.IsAuthenticated,)

    class Meta:
        model = RecipeInShoppingCart
        exclude = ('user',)

    def validate(self, data):
        request = self.context.get('request')
        user = request.user
        if not user.is_authenticated:
            raise exceptions.NotAuthenticated()
        recipe_id = self.context.get('recipe_in_cart')
        recipe_in_cart = RecipeInShoppingCart.objects.filter(
            user=user,
            recipe_in_cart=recipe_id
        )
        if request.method == 'POST':
            if recipe_in_cart.exists():
                raise serializers.ValidationError(
                    'Уже добавлено в список покупок.'
                )
        if request.method == 'DELETE':
            if not recipe_in_cart.exists():
                raise serializers.ValidationError(
                    'Уже убрано из списка покупок.'
                )
        return data

    def destroy(self, user, recipe_id):
        if not user.is_authenticated:
            raise exceptions.NotAuthenticated()
        recipe = get_object_or_404(
            Recipe,
            pk=recipe_id
        )
        recipe_in_cart = RecipeInShoppingCart.objects.filter(
            user=user,
            recipe_in_cart=recipe
        )
        if not recipe_in_cart.exists():
            raise serializers.ValidationError(
                'Уже убрано из списка покупок.'
            )
        return recipe_in_cart.delete()
