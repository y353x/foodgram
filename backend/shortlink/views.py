from django.shortcuts import redirect, render
from django.http import HttpResponsePermanentRedirect, HttpResponse

from shortlink.models import ShortLink


def s_link_redirect(request, short_link) -> HttpResponse:
    """Переадресация по короткой ссылке."""
    temp_short_url = request.build_absolute_uri()
    if ShortLink.objects.filter(short=temp_short_url).exists():
        full_url = ShortLink.objects.get(short=temp_short_url)
        try_url = f'localhost{full_url}'
        print(try_url)
        print(full_url)
        # return render(request, try_url, {})
        # return HttpResponsePermanentRedirect(f'{full_url}')
        return redirect(f'{full_url}', permanent=True)
