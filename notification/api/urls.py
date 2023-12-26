from django.urls import path, include

from rest_framework.routers import DefaultRouter

from notification.api.views import NotificationModelViewSet


router = DefaultRouter()
router.register('notifications', NotificationModelViewSet, basename='notification')


urlpatterns = [
    path('', include(router.urls)),
]