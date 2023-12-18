from django.db.models import Q

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from base.models import BookingTime, Booking
from base.api.serializers.bookingtime_serializers import (
    BookingTimeModelSerializer
)

from myapp.my_utils.custom_response import CustomResponse


class BookingTimeModelViewSet(ModelViewSet):
    queryset = BookingTime.objects.all()
    serializer_class = BookingTimeModelSerializer
    permission_classes = [IsAuthenticated]

    @action(methods=['GET'], detail=False)
    def available(self, request, *args, **kwargs):
        date = self.request.query_params.get('date')
        room_id = self.request.query_params.get('room_id')

        if not date:
            return CustomResponse.bad_request(
                message='Date is required'
            )

        if not room_id:
            return CustomResponse.bad_request(
                message='Room ID is required'
            )

        # Check if there is any booking on the same date and room
        queryset = Booking.objects.all()
        bookingtime_ids = queryset.filter(
            Q(booking_status='pending') |
            Q(booking_status='active'),
            booking_date=date,
            room__room_id=room_id,
        ).values_list('bookingtime', flat=True)

        available_bookingtimes = self.get_queryset().exclude(
            bookingtime_id__in=bookingtime_ids
        )
        # End of checking

        serializer = self.get_serializer(
            available_bookingtimes, 
            many=True
        )

        if serializer.data == []:
            return CustomResponse.not_found(
                message='No available booking times found'
            )

        return CustomResponse.list(
            data=serializer.data,
            message='Available booking times retrieved successfully',
        )
