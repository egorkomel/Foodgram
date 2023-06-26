from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    validate_unicode_slug)
from django.db import models
from users.models import User


class Tag(models.Model):
    """Tag model."""

    name = models.CharField(max_length=30, unique=True)
    color = models.CharField(max_length=7, unique=True)
    slug = models.SlugField(
        unique=True, blank=False, validators=[validate_unicode_slug, ]
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    """Ingredient model."""

    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=10)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    """Recipe model."""

    tags = models.ManyToManyField(
        Tag,
        related_name='tags',
        through='RecipeTag'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='ingredients',
        through='RecipeIngredient'
    )
    is_favorited = models.ManyToManyField(
        User,
        related_name='favorites',
        through='FavoriteRecipe'
    )
    is_in_shopping_cart = models.ManyToManyField(
        User,
        related_name='in_shopping_cart',
        through='RecipeInShoppingCart'
    )
    name = models.CharField(max_length=30)
    image = models.ImageField(upload_to='recipes/')
    text = models.TextField()
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                limit_value=1,
                message='Время приготвления не может быть меньше 1 минут.'
            ),
            MaxValueValidator(
                limit_value=360,
                message='Время приготвления не может быть больше 6 часов.'
            )
        ]
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeTag(models.Model):
    """Model for ManyToMany relation Recipe and Tag."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tags = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.recipe} {self.tags}'

    class Meta:
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'tags',),
                name='recipe_tags'
            )
        ]


class RecipeIngredient(models.Model):
    """Model for ManyToMany relation Recipe and Ingredient."""

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients'
    )
    ingredients = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='in_recipe'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                limit_value=1,
                message='Количество ингредиента не может быть меньше 1.'
            )
        ]
    )

    def __str__(self):
        return f'{self.recipe} {self.ingredients} {self.amount}'

    class Meta:
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredients',),
                name='recipe_ingredients'
            )
        ]


class FavoriteRecipe(models.Model):
    """Model of Favorite Recipes."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe_in_favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_favorites'
    )

    def __str__(self):
        return f'{self.recipe} {self.recipe}'

    class Meta:
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe',),
                name='user_recipe'
            )
        ]


class RecipeInShoppingCart(models.Model):
    """Model of recipes in shopping cart."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes_in_cart'
    )
    recipe_in_cart = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_cart'
    )

    def __str__(self):
        return f'{self.user} {self.recipe_in_cart}'

    class Meta:
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe_in_cart',),
                name='user_recipe_in_cart'
            )
        ]
