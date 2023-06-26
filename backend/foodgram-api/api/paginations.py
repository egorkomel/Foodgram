from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """Custom pagination class for view."""

    page_size = 6
    page_query_param = 'page'
    max_page_size = 1000
