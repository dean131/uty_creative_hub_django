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
)


class BookingTimeAdmin(admin.ModelAdmin):
    list_display = ['bookingtime_id', 'start_time', 'end_time', 'duration']


admin.site.register(Faculty)
admin.site.register(StudyProgram)
admin.site.register(Room)
admin.site.register(BookingTime, BookingTimeAdmin)
admin.site.register(Booking)
admin.site.register(Article)
admin.site.register(RoomFacility)
admin.site.register(RoomImage)
