from django.contrib import admin

from .models import Cart, Favorite, Ingredient, Recipe, RecipeIngredient, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    list_editable = ('name', 'color', 'slug')
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_editable = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'name', 'image', 'text', 'cooking_time',
                    'count_favorites')
    list_editable = ('author', 'name', 'image', 'text', 'cooking_time')
    empty_value_display = '-пусто-'
    list_filter = ('author', 'name', 'tags')
    readonly_fields = ('count_favorites',)

    @admin.display(description='В избранном')
    def count_favorites(self, obj):
        return obj.favorite.count()


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount')
    list_editable = ('recipe', 'ingredient', 'amount')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'user')
    list_editable = ('recipe', 'user')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'user')
    list_editable = ('recipe', 'user')
