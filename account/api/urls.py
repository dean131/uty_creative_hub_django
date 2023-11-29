from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import auth_views, user_profile_views


router = DefaultRouter()
router.register('userprofiles', user_profile_views.UserProfileModelViewSet, basename='userprofile')

urlpatterns = [
    path('', include(router.urls)), 

    path("login/", auth_views.LoginApiView.as_view(), name="login"),
    path('register/', auth_views.RegisterAPIView.as_view(), name='register'),
    path('logout/', auth_views.LogoutAPIView.as_view(), name='logout'),
    path('confirm_email/', auth_views.ConfirmEmailAPIView.as_view(), name='confirm_email'),
]