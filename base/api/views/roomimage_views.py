from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from myapp.my_utils.custom_response import CustomResponse
from base.api.serializers.roomimage_serializers import (
    RoomImageModelSerializer,
    RoomImageCreateModelSerializer,
)
from base.models import RoomImage


class RoomImageModelViewSet(ModelViewSet):
    queryset = RoomImage.objects.all()
    serializer_class = RoomImageModelSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['roomimage_id', 'room', 'created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return RoomImageCreateModelSerializer
        return super().get_serializer_class()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.list(
            message='RoomImages retrieved successfully',
            data=serializer.data,
        )
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return CustomResponse.created(
                message='RoomImage created successfully',
                data=serializer.data,
                headers=headers
            )
        return CustomResponse.serializers_erros(serializer.errors)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return CustomResponse.deleted(
            message='RoomImage deleted successfully'
        )
        

    



