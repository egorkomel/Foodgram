from api.models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag
from django.contrib import admin


class IngredientsInLine(admin.StackedInline):
    model = RecipeIngredient
    min_num = 1


class TagInLine(admin.StackedInline):
    model = RecipeTag
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientsInLine, TagInLine]
    list_display = ('name', 'author',)
    list_filter = ('name', 'author', 'tags',)
    empty_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)


admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
