import random

from django.db import transaction
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions

from rest_framework_simplejwt.tokens import RefreshToken

from account.api.serializers.user_serializers import (
    UserRegisterSerializer,
)
from account.api.serializers.userprofile_serializers import (
    UserProfileModelSerializer,
)

from account.models import OTPCode, User
from myapp.my_utils.send_email import send_otp


class LoginApiView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

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
        # END EMAIL VALIDATOR

        user = authenticate(request, username=email, password=password)

        if user is None:
            return Response(
                {
                    'success': False,
                    'message': 'Invalid credentials',
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
            return Response(
                {
                    'success': False,
                    'message': 'Password is required',
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
        
        if password != confirm_password:
            return Response(
                {
                    'success': False,
                    'message': 'Password and confirm password must be same',
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
        
        # EMAIL VALIDATOR
        if not email_dest:
            return Response(
                {
                    'success': False,
                    'message': 'Email is required',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if '@' not in email_dest:
            return Response(
                {
                    'success': False,
                    'message': 'Email must be contain "@"',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if User.objects.filter(email=email_dest, is_active=True).exists():
            return Response(
                {
                    'success': False,
                    'message': 'Email is already exists',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        # END EMAIL VALIDATOR

        otp_obj = OTPCode.objects.filter(user__email=email_dest, user__is_active=False).first()
        if otp_obj:
            otp_obj.code = otp_code
            otp_obj.save()

            send_otp(email_dest, name, otp_code)

            return Response(
                {
                    'success': True,
                    'message': 'OTP Code has been sent to your email',
                },
                status=status.HTTP_201_CREATED,
            )

        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            otp_obj = OTPCode.objects.create(
                code=otp_code,
                user=user,
            )

            send_otp(email_dest, name, otp_code)

            return Response(
                {
                    'success': True,
                    'message': 'OTP Code has been sent to your email',
                },
                status=status.HTTP_201_CREATED,
            )
        
        errors = serializer.errors.items()
        return Response(
            {
                'success': False,
                'message': [key for key, val in errors][0] + ': ' +  [val for key, val in errors][0][0],
                # 'message': [msg for msg in serializer.errors.values()][0][0],
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    

class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(
            {
                'success': True,
                'message': 'Successfully logged out',
            },
            status=status.HTTP_200_OK,
        )
    

class ConfirmEmailAPIView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        otp_code = request.data.get('otp')
        email = request.data.get('email')

        otp_obj = OTPCode.objects.filter(code=otp_code, user__email=email).first()
        if not otp_obj:
            return Response(
                {
                    'success': False,
                    'message': 'OTP is not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if otp_obj.expire > timezone.now():
            user = otp_obj.user 
            user.is_active = True
            user.save()
            return Response(
                {
                    'success': True,
                    'message': 'Successfully confirmed OTP Code',
                },
                status=status.HTTP_200_OK,
            )
            
        return Response(
            {
                'status': False,
                'message': 'OTP Code is expired'
            }
        )