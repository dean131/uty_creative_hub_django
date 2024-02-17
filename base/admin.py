from django.contrib import admin

from .models import (
    Article,
    ArticleImage,
    Booking,
    BookingTime,
    Faculty,
    Room,
    RoomType,
    RoomFacility,
    StudyProgram,
    RoomImage,
    BookingMember,
    Rating,
    Committee,
    Banner,
)


class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'room', 'booking_status', 'bookingtime', 'booking_date']


class BookingTimeAdmin(admin.ModelAdmin):
    list_display = ['bookingtime_id', '__str__']


admin.site.register(RoomType)
admin.site.register(ArticleImage)
admin.site.register(Faculty)
admin.site.register(StudyProgram)
admin.site.register(Room)
admin.site.register(BookingTime, BookingTimeAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(Article)
admin.site.register(RoomFacility)
admin.site.register(RoomImage)
admin.site.register(BookingMember)
admin.site.register(Rating)
admin.site.register(Committee)
admin.site.register(Banner)

