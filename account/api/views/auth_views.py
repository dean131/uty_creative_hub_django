import random

from django.db import transaction
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout

from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status, permissions

from rest_framework_simplejwt.tokens import RefreshToken

from account.api.serializers.user_serializers import (
    UserModelSerializer,
    UserRegisterSerializer,
)
from account.api.serializers.userprofile_serializers import (
    UserProfileModelSerializer,
)

from account.models import OTPCode, User
from myapp.my_utils.send_email import send_otp
from myapp.my_utils.custom_response import CustomResponse


class UserModelViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserModelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return CustomResponse.retrieve(
                message='Successfully retrieved data',
                data=serializer.data,
            )
        except:
            return CustomResponse.not_found(
                message='User not found.'
            )


class LoginApiView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        # EMAIL VALIDATOR
        if not email:
            return Response(
                {
                    'success': False,
                    'message': 'Email is required',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if '@' not in email:
            return Response(
                {
                    'success': False,
                    'message': 'Email must be contain @',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        user = User.objects.filter(email=email).first()
        if not user:
            return Response(
                {
                    'success': False,
                    'message': 'Email is not found',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if user.is_active == False:
            return Response(
                {
                    'success': False,
                    'message': 'Your account is not active.',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if user.is_verified == False:
            return CustomResponse.bad_request(
                message='Your account is not verified.',
            )
        # END EMAIL VALIDATOR

        # PASSWORD VALIDATOR
        if not password:
            return Response(
                {
                    'success': False,
                    'message': 'Password is required',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if len(password) < 8:
            return Response(
                {
                    'success': False,
                    'message': 'Password must be at least 8 characters',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        # END PASSWORD VALIDATOR

        user = authenticate(request, username=email, password=password)

        if user is None:
            return Response(
                {
                    'success': False,
                    'message': 'User is not found',
                }, 
                status=status.HTTP_401_UNAUTHORIZED
            )  
        
        if not user.check_password(password):
            return Response(
                {
                    'success': False,
                    'message': 'Password is wrong',
                }, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        refresh = RefreshToken.for_user(user)

        refresh['full_name'] = user.full_name
        refresh['email'] = user.email
        refresh['is_active'] = user.is_active
        refresh['is_admin'] = user.is_admin

        try:
            refresh['userprofile'] = UserProfileModelSerializer(user.userprofile).data
        except:
            pass

        login(request, user)

        return Response(
            {
                'success': True,
                'message': 'Successfully logged in',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        )
    

class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @transaction.atomic
    def post(self, request):
        name = request.data.get('full_name')
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

        otp_obj = OTPCode.objects.filter(user__email=email_dest, user__is_active=False).first()
        if otp_obj:
            otp_obj.code = otp_code
            otp_obj.save()

            send_otp(email_dest, name, otp_code)

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

            send_otp(email_dest, name, otp_code)

            return CustomResponse.ok(
                message='OTP Code has been sent to your email',
            )
        
        return CustomResponse.serializers_erros(errors=serializer.errors)
    

class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return CustomResponse.ok(
            message='Successfully logged out',
        )
    

class ConfirmEmailAPIView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        otp_code = request.data.get('otp')
        email = request.data.get('email')

        otp_obj = OTPCode.objects.filter(code=otp_code, user__email=email).first()
        if not otp_obj:
            return CustomResponse.bad_request(
                message='OTP Code is invalid',
            )

        if timezone.now() < otp_obj.expire:
            return CustomResponse.ok(
                message='Email is active',
            )
            
        return CustomResponse.bad_request(
            message='OTP Code is expired',
        )
    

class ChangePasswordAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        # PASSWORD VALIDATOR
        if not old_password:
            return Response(
                {
                    'success': False,
                    'message': 'Old password is required',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if not new_password:
            return Response(
                {
                    'success': False,
                    'message': 'New password is required',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if not confirm_password:
            return Response(
                {
                    'success': False,
                    'message': 'Confirm password is required',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if new_password != confirm_password:
            return Response(
                {
                    'success': False,
                    'message': 'New password and confirm password must be same',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if len(new_password) < 8:
            return Response(
                {
                    'success': False,
                    'message': 'New password must be at least 8 characters',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        # END PASSWORD VALIDATOR

        user = request.user
        if not user.check_password(old_password):
            return Response(
                {
                    'success': False,
                    'message': 'Old password is wrong',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        user.set_password(new_password)
        user.save()

        return Response(
            {
                'success': True,
                'message': 'Password changed successfully',
            },
            status=status.HTTP_200_OK,
        )


class ResendOTPConfirmEmailAPIView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
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

            send_otp(email, user.full_name, otp_code)

            return CustomResponse.ok(
                message='OTP Code has been sent to your email',
            )
        
        return CustomResponse.not_found(
            message='OTP Code is not Found',
        )


class ForgotPasswordAPIView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
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

            send_otp(email, user.full_name, otp_code)

            return CustomResponse.ok(
                message='OTP Code has been sent to your email',
            )
        
        return CustomResponse.not_found(
            message='OTP Code is not Found',
        )






