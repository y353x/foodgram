from django.contrib import admin

from recipes.models import Cart, Favorite, Ingredient, Recipe, Tag


class TagAdmin(admin.ModelAdmin):
    """Админ-зона тегов."""

    list_display = ('id', 'name', 'slug')
    list_filter = ('name', 'slug')
    search_fields = ('name', 'slug')


class IngredientAdmin(admin.ModelAdmin):
    """Админ-зона тегов."""

    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    """Админ-зона рецептов."""

    list_display = ('name', 'author')
    search_fields = ('name', 'author')
    list_filter = ('tags',)
    filter_horizontal = ('tags',)
    readonly_fields = ('get_favorite',)

    def get_favorite(self, obj):
        return obj.favorite.count()

    get_favorite.short_description = 'Добавлено в избранное раз'


class CartAdmin(admin.ModelAdmin):
    """Админ-зона корзины."""

    list_display = ('id', 'recipe', 'user')
    list_filter = ('recipe', 'user')
    search_fields = ('recipe', 'user')


class FavoriteAdmin(admin.ModelAdmin):
    """Админ-зона избранного."""

    list_display = ('id', 'recipe', 'user')
    list_filter = ('recipe', 'user')
    search_fields = ('recipe', 'user')


admin.site.register(Tag, TagAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Ingredient, IngredientAdmin)
