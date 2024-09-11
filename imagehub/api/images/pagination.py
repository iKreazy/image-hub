from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class ImagePagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'limit'
    max_page_size = 100
    page_query_param = 'p'

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'results': data
        })

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'required': ['count', 'results'],
            'properties': {
                'count': {
                    'type': 'integer',
                    'example': 123,
                },
                'results': schema,
            },
        }
