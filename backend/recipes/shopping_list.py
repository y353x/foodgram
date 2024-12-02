from datetime import date

from django.http import HttpResponse


def shopping_list(queryset) -> HttpResponse:
    """Формирование файла списка покупок."""
    today = date.today()
    shop_list = f'Список покупок на {today}:'
    for position in queryset:
        row = f'\n{position[0]} - {position[2]} {position[1]}.'
        shop_list += row
    filename = f'shop_list_{today}.txt'
    response = HttpResponse(
        shop_list, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response
