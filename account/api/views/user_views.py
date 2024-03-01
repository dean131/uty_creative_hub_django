import random

from django.db import transaction
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout

from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action

from rest_framework_simplejwt.tokens import RefreshToken

from account.api.serializers.user_serializers import (
    UserSerializer,
    UserRegisterSerializer,
    UserListSerializer,
    UserDetailSerializer
)
from account.api.serializers.userprofile_serializers import (
    UserProfileSerializer,
)

from account.models import OTPCode, User
from myapp.custom_pagination import CustomPaginationSerializer
from myapp.my_utils.custom_response import CustomResponse
from account.tasks import send_otp_celery


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = '__all__'
    ordering_fields = '__all__'
    pagination_class = CustomPaginationSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        if self.action == 'retrieve':
            return UserDetailSerializer
        return super().get_serializer_class()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return CustomResponse.retrieve(
            message='Successfully retrieved data',
            data=serializer.data,
        )
        
    # @transaction.atomic
    @action(methods=['POST'], detail=False, permission_classes=[permissions.AllowAny])
    def register(self, request, *args, **kwargs):
        email_dest = request.data.get('email')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        otp_code = random.randint(1000, 9999)

        # PASSWORD VALIDATOR
        if not password:
            return CustomResponse.bad_request(
                message='Password is required',
            )
        
        if not confirm_password:
            return CustomResponse.bad_request(
                message='Confirm password is required',
            )
        
        if password != confirm_password:
            return CustomResponse.bad_request(
                message='Password and confirm password must be same',
            )
        
        if len(password) < 8:
            return CustomResponse.bad_request(
                message='Password must be at least 8 characters',
            )
        # END PASSWORD VALIDATOR
        
        # EMAIL VALIDATOR
        if not email_dest:
            return CustomResponse.bad_request(
                message='Email is required',
            )
        
        if '@' not in email_dest:
            return CustomResponse.bad_request(
                message='Email must be contain @',
            )
        
        if User.objects.filter(email=email_dest, is_active=True).exists():
            return CustomResponse.bad_request(
                message='Email already exists',
            )
        # END EMAIL VALIDATOR

        otp_obj = OTPCode.objects.update_or_create(user__email=email_dest, user__is_active=False).first()
        if otp_obj:
            otp_obj.code = otp_code
            otp_obj.save()
            otp_obj.user.set_password(password)
            otp_obj.user.save()
            send_otp_celery.delay(email_dest, otp_code)
            return CustomResponse.ok(
                message='OTP Code has been sent to your email',
            )

        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            otp_obj = OTPCode.objects.create(
                code=otp_code,
                user=user,
            )
            send_otp_celery.delay(email_dest, otp_code)
            return CustomResponse.ok(
                message='OTP Code has been sent to your email',
            )
        return CustomResponse.serializers_erros(errors=serializer.errors)

    @action(methods=['POST'], detail=False, permission_classes=[permissions.AllowAny])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        # EMAIL VALIDATOR
        if not email:
            return CustomResponse.bad_request(
                message='Email is required',
            )
        
        if '@' not in email:
            return CustomResponse.bad_request(
                message='Email must be contain @',
            )
        
        user = User.objects.filter(email=email).first()
        if not user:
            return CustomResponse.bad_request(
                message='Email is not found',
            )
        
        if user.is_active == False:
            return CustomResponse.bad_request(
                message='Please complete your registration first',
            )
        # END EMAIL VALIDATOR

        # PASSWORD VALIDATOR
        if not password:
            return CustomResponse.bad_request(
                message='Password is required',
            )
        
        if len(password) < 8:
            return CustomResponse.bad_request(
                message='Password must be at least 8 characters',
            )
        # END PASSWORD VALIDATOR
        
        if not user.check_password(password):
            return CustomResponse.bad_request(
                message='Password is wrong',
            )

        authenticated_user = authenticate(request, username=email, password=password)
        if user is None:
            return CustomResponse.bad_request(
                message='User is not found',
            )
        
        refresh = RefreshToken.for_user(authenticated_user)
        refresh['full_name'] = authenticated_user.full_name
        refresh['email'] = authenticated_user.email
        refresh['is_active'] = authenticated_user.is_active
        refresh['is_admin'] = authenticated_user.is_admin
        refresh['verification_status'] = authenticated_user.verification_status

        try:
            refresh['userprofile'] = UserProfileSerializer(authenticated_user.userprofile).data
        except:
            pass

        login(request, authenticated_user)

        return Response(
            {
                'success': True,
                'message': 'Successfully logged in',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        )

    @action(methods=['POST'], detail=False, permission_classes=[permissions.AllowAny])
    def confirm_otp(self, request, *args, **kwargs):
        otp_code = request.data.get('otp')
        email = request.data.get('email')

        otp_obj = OTPCode.objects.filter(code=otp_code, user__email=email).first()
        if not otp_obj:
            return CustomResponse.bad_request(
                message='OTP Code is invalid',
            )

        if timezone.now() > otp_obj.expire:
            return CustomResponse.bad_request(
                message='OTP Code is expired',
            )
            
        serializer = self.get_serializer(otp_obj.user)
        return CustomResponse.retrieve(
            message='Email is verified',
            data=serializer.data,
        )

    @action(methods=['POST'], detail=False)
    def logout(self, request):
        logout(request)
        return CustomResponse.ok(
            message='Successfully logged out',
        )

    @action(methods=['POST'], detail=False)
    def change_password(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        # PASSWORD VALIDATOR
        if not old_password:
            return CustomResponse.bad_request(
                message='Old password is required',
            )
        
        if not new_password:
            return CustomResponse.bad_request(
                message='New password is required',
            )
        
        if not confirm_password:
            return CustomResponse.bad_request(
                message='Confirm password is required',
            )
        
        if new_password != confirm_password:
            return CustomResponse.bad_request(
                message='New password and confirm password must be same',
            )
        
        if len(new_password) < 8:
            return CustomResponse.bad_request(
                message='New password must be at least 8 characters',
            )
        # END PASSWORD VALIDATOR

        user = request.user
        if not user.check_password(old_password):
            return CustomResponse.bad_request(
                message='Old password is wrong',
            )
        
        user.set_password(new_password)
        user.save()

        return CustomResponse.ok(
            message='Password has been changed',
        )

    @action(methods=['POST'], detail=False)
    def change_email(self, request):
        otp_code = request.data.get('otp_code')
        email = request.data.get('email')

        user = request.user
        otp_obj = OTPCode.objects.filter(user=user).first()
        if otp_obj.code != otp_code:
            return CustomResponse.bad_request(
                message='OTP Code is invalid',
            )

        if timezone.now() > otp_obj.expire:
            return CustomResponse.bad_request(
                message='OTP Code is expired',
            )
        
        user = request.user
        user.email = email
        user.save()
            
        serializer = self.get_serializer(otp_obj.user)
        return CustomResponse.retrieve(
            message='Email is changed',
            data=serializer.data,
        )

    @action(methods=['POST'], detail=False)
    def password_validation(self, request):
        password = request.data.get('password')
        user = request.user

        # PASSWORD VALIDATOR
        if not password:
            return CustomResponse.bad_request(
                message='Password is required',
            )
        
        if len(password) < 8:
            return CustomResponse.bad_request(
                message='Password must be at least 8 characters',
            )
        
        if not user.check_password(password):
            return CustomResponse.bad_request(
                message='Password is wrong',
            )
        # END PASSWORD VALIDATOR

        return CustomResponse.ok(
            message='Password is valid',
        )

    @action(methods=['POST'], detail=False)
    def get_otp_email_validation(self, request):
        email = request.data.get('email')
        otp_code = random.randint(1000, 9999)

        # EMAIL VALIDATOR
        if not email:
            return CustomResponse.bad_request(
                message='Email is required',
            )
        
        if '@' not in email:
            return CustomResponse.bad_request(
                message='Email must be contain @',
            )
        
        user = User.objects.filter(email=email, is_active=False).first()
        if not user:
            return CustomResponse.bad_request(
                message='Email is not found',
            )
        # END EMAIL VALIDATOR

        otp_obj = OTPCode.objects.filter(user__email=email, user__is_active=False).first()
        if otp_obj:
            otp_obj.code = otp_code
            otp_obj.save()
            send_otp_celery.delay(email, otp_code)
            return CustomResponse.ok(
                message='OTP Code has been sent to your email',
            )
        return CustomResponse.not_found(
            message='OTP Code is not Found',
        )

    @action(methods=['POST'], detail=False, permission_classes=[permissions.AllowAny])
    def get_otp_forgot_password(self, request):
        email = request.data.get('email')
        otp_code = random.randint(1000, 9999)

        # EMAIL VALIDATOR
        if not email:
            return CustomResponse.bad_request(
                message='Email is required',
            )
        
        if '@' not in email:
            return CustomResponse.bad_request(
                message='Email must be contain @',
            )
        
        user = User.objects.filter(email=email, is_active=True).first()
        if not user:
            return CustomResponse.bad_request(
                message='Email is not found',
            )
        # END EMAIL VALIDATOR

        otp_obj = OTPCode.objects.filter(user__email=email, user__is_active=True).first()
        if otp_obj:
            otp_obj.code = otp_code
            otp_obj.save()

            send_otp_celery.delay(email, otp_code, user.full_name)

            return CustomResponse.ok(
                message='OTP Code has been sent to your email',
            )
        
        return CustomResponse.not_found(
            message='OTP Code is not Found',
        )    

    @action(methods=['POST'], detail=False, permission_classes=[permissions.AllowAny])
    def get_otp_change_email(self, request):
        email = request.data.get('email')
        otp_code = random.randint(1000, 9999)

        # EMAIL VALIDATOR
        if not email:
            return CustomResponse.bad_request(
                message='Email is required',
            )
        
        if '@' not in email:
            return CustomResponse.bad_request(
                message='Email must be contain @',
            )
        # END EMAIL VALIDATOR

        user = request.user
        otp_obj = OTPCode.objects.filter(user=user).first()
        if otp_obj:
            otp_obj.code = otp_code
            otp_obj.save()

            send_otp_celery.delay(email, otp_code, user.full_name)

            return CustomResponse.ok(
                message='OTP Code has been sent to your email',
            )
        
        return CustomResponse.not_found(
            message='OTP Code is not Found',
        )

    @action(methods=['POST'], detail=False, permission_classes=[permissions.AllowAny])
    def forgot_password(self, request):
        email = request.data.get('email')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        # EMAIL VALIDATOR
        if not email:
            return CustomResponse.bad_request(
                message='Email is required',
            )
        
        if '@' not in email:
            return CustomResponse.bad_request(
                message='Email must be contain @',
            )
        
        user = User.objects.filter(email=email, is_active=True).first()
        if not user:
            return CustomResponse.bad_request(
                message='Email is not found',
            )
        # END EMAIL VALIDATOR

        # PASSWORD VALIDATOR
        if not new_password:
            return CustomResponse.bad_request(
                message='New password is required',
            )
        
        if not confirm_password:
            return CustomResponse.bad_request(
                message='Confirm password is required',
            )
        
        if new_password != confirm_password:
            return CustomResponse.bad_request(
                message='New password and confirm password must be same',
            )
        
        if len(new_password) < 8:
            return CustomResponse.bad_request(
                message='New password must be at least 8 characters',
            )
        # END PASSWORD VALIDATOR

        user = User.objects.filter(email=email, is_active=True).first()
        if not user:
            return CustomResponse.bad_request(
                message='Email is not found',
            )
        
        user.set_password(new_password)
        user.save()

        return CustomResponse.ok(
            message='Password has been changed',
        )

    @action(methods=['POST'], detail=False, permission_classes=[permissions.AllowAny])
    def get_otp_change_privacy_key(self, request):
        email = request.data.get('email')
        otp_code = random.randint(1000, 9999)

        # EMAIL VALIDATOR
        if not email:
            return CustomResponse.bad_request(
                message='Email is required',
            )
        
        if '@' not in email:
            return CustomResponse.bad_request(
                message='Email must be contain @',
            )
        # END EMAIL VALIDATOR

        otp_obj = OTPCode.objects.filter(user__email=email).first()
        if otp_obj:
            otp_obj.code = otp_code
            otp_obj.save()

            send_otp_celery.delay(email, otp_code, otp_obj.user.full_name)

            return CustomResponse.ok(
                message='OTP Code has been sent to your email',
            )
        
        return CustomResponse.not_found(
            message='OTP Code is not Found',
        )

    @action(methods=['POST'], detail=True)
    def change_verification_status(self, request, *args, **kwargs):
        user = self.get_object()
        verification_status = request.data.get('verification_status')

        if not verification_status:
            return CustomResponse.bad_request(
                message='Verification status is required',
            )
        
        if verification_status not in ['verified', 'rejected', 'suspend']:
            return CustomResponse.bad_request(
                message='Verification status is invalid',
            )
        
        user.verification_status = verification_status
        user.save()
        return CustomResponse.ok(
            message='User status has been changed',
        )










