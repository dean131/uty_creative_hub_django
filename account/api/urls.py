from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import auth_views, userprofile_views


router = DefaultRouter()
router.register('userprofiles', userprofile_views.UserProfileModelViewSet, basename='userprofile')

urlpatterns = [
    path('', include(router.urls)), 

    path("login/", auth_views.LoginApiView.as_view(), name="login"),
    path('register/', auth_views.RegisterAPIView.as_view(), name='register'),
    path('logout/', auth_views.LogoutAPIView.as_view(), name='logout'),
    path('confirm_email/', auth_views.ConfirmEmailAPIView.as_view(), name='confirm_email'),
    path('resend_otp_confirm_email/', auth_views.ResendOTPConfirmEmailAPIView.as_view(), name='resend_otp_confirm_email'),
    path('change_password/', auth_views.ChangePasswordAPIView.as_view(), name='change_password'),
]
