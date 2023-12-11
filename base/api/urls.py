from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import (
    bookingtime_views,
    booking_view,
    room_views,
    article_views,
    rating_views,
    bookingmember_views,
    faculty_views,
)

router = DefaultRouter()
router.register('bookingtimes', bookingtime_views.BookingTimeModelViewSet, basename='bookingtime')
router.register('bookings', booking_view.BookingModelViewSet, basename='booking')
router.register('rooms', room_views.RoomModelViewSet, basename='room')
router.register('articles', article_views.ArticleModelViewSet, basename='article')
router.register('ratings', rating_views.RatingModelViewSet, basename='rating')
router.register('bookingmembers', bookingmember_views.BookingMemberModelViewSet, basename='bookingmember')
router.register('faculties', faculty_views.FacultyModelViewSet, basename='faculty')

urlpatterns = [
    path('', include(router.urls))
]