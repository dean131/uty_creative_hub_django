from rest_framework import serializers

from base.models import Booking
from account.api.serializers.user_serializers import (
    UserBookingDetailSerializer,
)

from base.api.serializers.room_serializers import (
    RoomDetailBookingModelSerializer,
    RoomBookingHistoryModelSerializer
)
from base.api.serializers.bookingtime_serializers import BookingTimeModelSerializer
from base.api.serializers.bookingmember_serializers import BookingMemberBookingDetailSerializer

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'


class BookingHistorySerializer(serializers.ModelSerializer):
    room = RoomBookingHistoryModelSerializer()
    bookingtime = BookingTimeModelSerializer()
    booking_day = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = '__all__'

    def get_booking_day(self, obj):
        day = obj.booking_date.strftime("%A")
        match_day = {
            'Monday': 'Senin',
            'Tuesday': 'Selasa',
            'Wednesday': 'Rabu',
            'Thursday': 'Kamis',
            'Friday': 'Jumat',
            'Saturday': 'Sabtu',
            'Sunday': 'Minggu',
        }
        return match_day[day]


class BookingDetailModelSerializer(serializers.ModelSerializer):
    user = UserBookingDetailSerializer()
    room = RoomDetailBookingModelSerializer()
    bookingtime = BookingTimeModelSerializer()
    bookingmember = serializers.SerializerMethodField()
    booking_day = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'booking_id',
            'booking_day',
            'booking_date',
            'booking_status',
            'booking_needs',
            'created_at',
            'bookingtime',
            'user',
            'room',
            'bookingmember',
        ]

    def get_bookingmember(self, obj):
        bookingmembers = obj.bookingmember_set.filter()
        return BookingMemberBookingDetailSerializer(bookingmembers, many=True).data
    
    def get_booking_day(self, obj):
        day = obj.booking_date.strftime("%A")
        match_day = {
            'Monday': 'Senin',
            'Tuesday': 'Selasa',
            'Wednesday': 'Rabu',
            'Thursday': 'Kamis',
            'Friday': 'Jumat',
            'Saturday': 'Sabtu',
            'Sunday': 'Minggu',
        }
        return match_day[day]