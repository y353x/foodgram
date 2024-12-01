from django.contrib import admin
from shortlink.models import ShortLink


@admin.register(ShortLink)
class ShortLinkAdmin(admin.ModelAdmin):
    """Админ-зона коротких ссылок."""

    list_display = ('id', 'full', 'short')
    list_filter = ('full', 'short')
    search_fields = ('full', 'short')
