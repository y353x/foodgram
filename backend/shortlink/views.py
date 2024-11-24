from django.shortcuts import redirect

from shortlink.models import ShortLink


def s_link_redirect(request, short_link):
    """Переадресация по короткой ссылке."""
    temp_short_url = request.build_absolute_uri()
    if ShortLink.objects.filter(short=temp_short_url).exists():
        full_url = ShortLink.objects.get(short=temp_short_url)
        return redirect(f'{full_url}', permanent=True)
