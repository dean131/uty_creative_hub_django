from rest_framework.serializers import ModelSerializer

from base.models import Booking
from account.api.serializers.user_serializers import UserBookingDetailModelSerializer
from base.api.serializers.room_serializers import RoomDetailBookingModelSerializer
from base.api.serializers.bookingtime_serializers import BookingTimeModelSerializer


class BookingModelSerializer(ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'


class BookingDetailModelSerializer(ModelSerializer):
    user = UserBookingDetailModelSerializer()
    room = RoomDetailBookingModelSerializer()
    bookingtime = BookingTimeModelSerializer()
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
        ]