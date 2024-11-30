from django.contrib import admin

from api.constants import ADMIN_EXTRA_FIELDS
from recipes.models import (Cart, Favorite, Ingredient, IngredientRecipe,
                            Recipe, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админ-зона тегов."""

    list_display = ('id', 'name', 'slug')
    list_filter = ('name', 'slug')
    search_fields = ('name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админ-зона тегов."""

    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


class RecipeInline(admin.TabularInline):
    """Класс для корректного внесения рецептов."""

    model = IngredientRecipe
    extra = ADMIN_EXTRA_FIELDS  # Количество развернутых полей ингедиента.


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админ-зона рецептов."""

    list_display = ('name', 'author')
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)
    filter_horizontal = ('tags',)
    readonly_fields = ('get_favorite',)
    inlines = [RecipeInline]

    @admin.display(
        description='Добавлено в избранное раз'
    )
    def get_favorite(self, obj):
        return obj.favorites.count()


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Админ-зона корзины."""

    list_display = ('id', 'recipe', 'user')
    list_filter = ('recipe', 'user')
    search_fields = ('recipe__name', 'user__username')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админ-зона избранного."""

    list_display = ('id', 'recipe', 'user')
    list_filter = ('recipe', 'user')
    search_fields = ('recipe__name', 'user__username')
