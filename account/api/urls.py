from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import user_views, userprofile_views


router = DefaultRouter()
router.register('users', user_views.UserViewSet, basename='user')
router.register('userprofiles', userprofile_views.UserProfileViewSet, basename='userprofile')

urlpatterns = [
    path('', include(router.urls)), 
]
