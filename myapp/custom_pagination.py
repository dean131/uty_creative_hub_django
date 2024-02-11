from rest_framework import pagination
from rest_framework.response import Response

class CustomPaginationSerializer(pagination.PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'success': True,
            'message': 'Data berhasil diambil',
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'data': data  
        })
