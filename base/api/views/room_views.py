from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from myapp.my_utils.custom_response import CustomResponse
from base.api.serializers.room_serializers import (
    RoomModelSerializer,
    RoomDetailModelSerializer,
    RoomListModelSerializer,
)
from base.models import Room


class RoomModelViewSet(ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomModelSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RoomDetailModelSerializer
        elif self.action == 'list':
            return RoomListModelSerializer
        return self.serializer_class

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.list(
            message='Rooms retrieved successfully',
            data=serializer.data,
        )
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return CustomResponse.retrieve(
            message='Room retrieved successfully',
            data=serializer.data,
        )


        
        
