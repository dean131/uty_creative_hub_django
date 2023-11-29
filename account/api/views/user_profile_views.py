from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from account.models import UserProfile
from account.api.serializers.userprofile_serializers import (
    UserProfileModelSerializer,
)


class UserProfileModelViewSet(ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileModelSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        return Response(
            {
                'success': False,
                'message': 'Method not allowed',
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            {
                'success': True,
                'message': 'User profile retrieved successfully',
                'data': serializer.data,
            },
            status=status.HTTP_200_OK,
        )
        
    def create(self, request, *args, **kwargs):
        request.data.update({'user': request.user.user_id})
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                {
                    'success': True,
                    'message': 'User profile created successfully',
                    'data': serializer.data,
                },
                status=status.HTTP_201_CREATED,
                headers=headers,
            )
        
        errors = serializer.errors.items()
        return Response(
            {
                'success': False,
                'message': [key for key, val in errors][0] + ': ' +  [val for key, val in errors][0][0],
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    @action(methods=['post'], detail=True)
    def update_profile(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(
            {
                'success': True,
                'message': 'User profile updated successfully',
                'data': serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    
    def destroy(self, request, *args, **kwargs):
        return Response(
            {
                'success': False,
                'message': 'Method not allowed',
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )













