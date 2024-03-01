from django.db.models import Q

from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions

from notification.models import Notification
from notification.api.serializers import NotificationModelSerializer

from myapp.my_utils.custom_response import CustomResponse

class NotificationModelViewSet(ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationModelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        if not request.user.is_admin:
            user = request.user
            queryset = queryset.filter(
                Q(user__user_id=user.user_id) | Q(user__user_id=None),
                created_at__gte=user.created_at
            ).order_by('-created_at')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.list(
            message='Notification list retrieved successfully.',
            data=serializer.data
        )
