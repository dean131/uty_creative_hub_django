from django.db import transaction

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action

from account.models import UserProfile, User
from myapp.my_utils.custom_response import CustomResponse
from account.api.serializers.userprofile_serializers import UserProfileModelSerializer


class UserProfileModelViewSet(ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileModelSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Part of the registration process.
        """
        email = request.data.get('email')
        full_name = request.data.get('full_name')

        if not email:
            return CustomResponse.bad_request(
                message='Email is required.'
            )
        
        user = User.objects.filter(email=email, is_active=False, verification_status='unverified').first()
        if not user:
            return CustomResponse.bad_request(
                message='User is not found.'
            )
        
        user.full_name = full_name
        user.save()
        
        request.user = user
        faculty_id = request.data.get('faculty_id')
        studyprogram_id = request.data.get('studyprogram_id')
        request.data.update({
            'user': user.user_id,
            'faculty': faculty_id,
            'studyprogram': studyprogram_id,
        })
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            request.user.is_active = True
            request.user.save()
            return CustomResponse.ok(
                message='Registration submitted successfully',
            )
        return CustomResponse.serializers_erros(errors=serializer.errors)
    
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return CustomResponse.retrieve(
                message='User profile fetched successfully',
                data=serializer.data
            )
        except:
            return CustomResponse.not_found(
                message='User profile not found',
            )
    
    @action(methods=['post'], detail=True)
    def update_profile(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                self.perform_update(serializer)

                if getattr(instance, '_prefetched_objects_cache', None):
                    # If 'prefetch_related' has been applied to a queryset, we need to
                    # forcibly invalidate the prefetch cache on the instance.
                    instance._prefetched_objects_cache = {}

                return CustomResponse.updated(
                    message='User profile updated successfully',
                    data=serializer.data,
                )
            return CustomResponse.serializers_erros(errors=serializer.errors)
        except:
            return CustomResponse.not_found(
                message='User profile not found',
            )
