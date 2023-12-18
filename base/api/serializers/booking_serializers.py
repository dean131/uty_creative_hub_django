from rest_framework import serializers

from base.models import Booking
from account.api.serializers.user_serializers import (
    UserBookingDetailModelSerializer,
)

from base.api.serializers.room_serializers import RoomDetailBookingModelSerializer
from base.api.serializers.bookingtime_serializers import BookingTimeModelSerializer
from base.api.serializers.bookingmember_serializers import BookingMemberBookingDetailSerializer

class BookingModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'


class BookingDetailModelSerializer(serializers.ModelSerializer):
    user = UserBookingDetailModelSerializer()
    room = RoomDetailBookingModelSerializer()
    bookingtime = BookingTimeModelSerializer()
    bookingmember = serializers.SerializerMethodField()
    class Meta:
        model = Booking
        fields = [
            'booking_id',
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