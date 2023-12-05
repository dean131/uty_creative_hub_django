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
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):

        self.request.data._mutable = True

        email = self.request.data.get('email')
        if not email:
            return CustomResponse.bad_request(
                message='Email is required.'
            )
        user = User.objects.filter(email=email, is_active=False, is_verified=False).first()
        if not user:
            return CustomResponse.bad_request(
                message='User is not found.'
            )
        self.request.user = user
        self.request.data.update({'user': user.user_id})

        self.request.data._mutable = False

        serializer = self.get_serializer(data=self.request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            self.request.user.is_active = True
            self.request.user.save()
            headers = self.get_success_headers(serializer.data)
            return CustomResponse.created(
                message='User profile created successfully',
                data=serializer.data,
                headers=headers,
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
