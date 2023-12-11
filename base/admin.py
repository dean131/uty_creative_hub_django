from django.contrib import admin

from .models import (
    Article,
    Booking,
    BookingTime,
    Faculty,
    Room,
    RoomFacility,
    StudyProgram,
    RoomImage,
    BookingMember,
)


class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'room', 'booking_status', 'bookingtime', 'booking_date']


class BookingTimeAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'duration']


admin.site.register(Faculty)
admin.site.register(StudyProgram)
admin.site.register(Room)
admin.site.register(BookingTime, BookingTimeAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(Article)
admin.site.register(RoomFacility)
admin.site.register(RoomImage)
admin.site.register(BookingMember)
