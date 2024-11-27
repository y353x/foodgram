from django.contrib import admin

from recipes.models import User


class UserAdmin(admin.ModelAdmin):
    """
    Админ-зона пользователей.
    """
    list_display = ('id', 'username', 'email', 'first_name', 'role')
    list_filter = ('email', 'username')
    search_fields = ('email', 'username')


admin.site.register(User, UserAdmin)
