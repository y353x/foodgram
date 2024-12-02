from rest_framework.pagination import PageNumberPagination

from api.constants import PAGE_QUERY_PARAM, PAGE_SIZE


class ApiPagination(PageNumberPagination):
    """
    Переопределение пагинации для использования
    limit из запроса.
    """

    page_size_query_param = PAGE_QUERY_PARAM
    page_size = PAGE_SIZE
