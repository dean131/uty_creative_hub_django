from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import (
    bookingtime_views,
    booking_view,
    room_views,
    article_views,
    rating_views,
)

router = DefaultRouter()
router.register('bookingtimes', bookingtime_views.BookingTimeModelViewSet, basename='bookingtime')
router.register('bookings', booking_view.BookingModelViewSet, basename='booking')
router.register('rooms', room_views.RoomModelViewSet, basename='room')
router.register('articles', article_views.ArticleModelViewSet, basename='article')
router.register('ratings', rating_views.RatingModelViewSet, basename='rating')

urlpatterns = [
    path('', include(router.urls))
]