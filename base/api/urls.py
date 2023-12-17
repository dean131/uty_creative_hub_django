from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import (
    booking_views,
    bookingtime_views,
    room_views,
    article_views,
    rating_views,
    bookingmember_views,
    faculty_views,
    roomimage_views,
    studyprogram_views,
)

router = DefaultRouter()
router.register('bookingtimes', bookingtime_views.BookingTimeModelViewSet, basename='bookingtime')
router.register('bookings', booking_views.BookingModelViewSet, basename='booking')
router.register('rooms', room_views.RoomModelViewSet, basename='room')
router.register('articles', article_views.ArticleModelViewSet, basename='article')
router.register('ratings', rating_views.RatingModelViewSet, basename='rating')
router.register('bookingmembers', bookingmember_views.BookingMemberModelViewSet, basename='bookingmember')
router.register('faculties', faculty_views.FacultyModelViewSet, basename='faculty')
router.register('roomimages', roomimage_views.RoomImageModelViewSet, basename='roomimage')
router.register('studyprograms', studyprogram_views.StudyProgramModelViewSet, basename='studyprogram')

urlpatterns = [
    path('', include(router.urls))
]