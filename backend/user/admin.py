from django.contrib import admin

from recipes.models import User
from user.models import Follow


class UserAdmin(admin.ModelAdmin):
    """Админ-зона пользователей."""

    list_display = ('id', 'username', 'email', 'first_name', 'role')
    list_filter = ('email', 'username')
    search_fields = ('email', 'username')


class FollowAdmin(admin.ModelAdmin):
    """Админ-зона подписок."""

    list_display = ('id', 'user', 'author')
    list_filter = ('user', 'author')
    search_fields = ('user', 'author')


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
