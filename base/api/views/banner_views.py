from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from base.api.serializers.banner_serializers import BannerSerializer
from base.models import Banner
from myapp.my_utils.custom_response import CustomResponse


class BannerModelViewSet(ModelViewSet):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['banner_id', 'created_at']
    ordering_fields = ['banner_id', 'created_at']


    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.list(
            message='Banner berhasil diambil',
            data=serializer.data
        )
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return CustomResponse.created(
                message='Banner berhasil dibuat',
                data=serializer.data,
                headers=headers,
            )
        return CustomResponse.serializers_erros(serializer.errors)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return CustomResponse.deleted(
            message='Banner berhasil dihapus',
        )















