from rest_framework.pagination import PageNumberPagination,LimitOffsetPagination
class PaginaProductos(PageNumberPagination):
    page_size=24
    page_size_query_param="page_size"
    max_page_size=100
class PaginaCatalogoCompacta(LimitOffsetPagination):
    default_limit=50
    max_limit=100
