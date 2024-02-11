from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from myapp.my_utils.custom_response import CustomResponse
from base.api.serializers.article_serializers import (
    ArticleSerializer,
    ArticleListSerializer,
)
from base.models import Article

from myapp.custom_pagination import CustomPaginationSerializer


class ArticleModelViewSet(ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPaginationSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return ArticleListSerializer
        return self.serializer_class

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.list(
            message='Articles retrieved successfully',
            data=serializer.data,
        )
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return CustomResponse.retrieve(
            message='Article retrieved successfully',
            data=serializer.data
        )