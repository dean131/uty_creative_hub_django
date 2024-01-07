from django.db import transaction

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action

from account.models import UserProfile, User
from myapp.my_utils.custom_response import CustomResponse
from account.api.serializers.userprofile_serializers import (
    UserProfileSerializer
)


class UserProfileViewSet(ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

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
        # _mutable = request.data._mutable
        # request.data._mutable = True

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
      
    @action(methods=['post'], detail=False)
    def update_profile(self, request, *args, **kwargs):
        full_name = request.data.get('full_name')
        whatsapp_number = request.data.get('whatsapp_number')
        birth_date = request.data.get('birth_date')
        profile_pic = request.FILES.get('profile_pic')

        user = request.user
        userprofile = self.queryset.filter(user=user).first()

        if full_name:
            user.full_name = full_name

        if whatsapp_number:
            userprofile.whatsapp_number = whatsapp_number

        if birth_date:
            userprofile.birth_date = birth_date

        if profile_pic:
            userprofile.profile_pic = profile_pic

        userprofile = userprofile.save()
        user.save()

        serializer = self.get_serializer(userprofile)

        return CustomResponse.updated(
            message='Profile updated successfully',
            data=serializer.data,
        )

        
        
