from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from recipes.models import User
from user.models import Follow


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админ-зона пользователей."""

    list_display = ('id', 'username', 'email', 'first_name',
                    'role', 'get_follower', 'get_recipes')
    list_filter = ('email', 'username')
    search_fields = ('email', 'username')

    @admin.display(
        description='Подписчиков'
    )
    def get_follower(self, obj):
        return obj.follower.count()

    @admin.display(
        description='Рецепты автора'
    )
    def get_recipes(self, obj):
        return obj.recipes.count()


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Админ-зона подписок."""

    list_display = ('id', 'user', 'author')
    list_filter = ('user', 'author')
    search_fields = ('user__username', 'author__username')
