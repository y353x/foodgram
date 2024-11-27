from django.contrib import admin

from shortlink.models import ShortLink


class ShortLinkAdmin(admin.ModelAdmin):
    """Админ-зона коротких ссылок."""

    list_display = ('id', 'full', 'short')
    list_filter = ('full', 'short')
    search_fields = ('full', 'short')


admin.site.register(ShortLink, ShortLinkAdmin)
