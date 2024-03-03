from django.db.models import Q

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from base.models import BookingTime, Booking
from base.api.serializers.bookingtime_serializers import (
    BookingTimeModelSerializer,
    BookingTimeAvaliableModelSerializer,
)

from myapp.my_utils.custom_response import CustomResponse


class BookingTimeModelViewSet(ModelViewSet):
    queryset = BookingTime.objects.all()
    serializer_class = BookingTimeModelSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'available':
            return BookingTimeAvaliableModelSerializer
        return super().get_serializer_class()

    @action(methods=['GET'], detail=False)
    def available(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        date = self.request.query_params.get('date')
        room_id = self.request.query_params.get('room_id')

        if not date:
            return CustomResponse.bad_request(
                message='Tanggal booking tidak boleh kosong'
            )

        if not room_id:
            return CustomResponse.bad_request(
                message='Room Id tidak boleh kosong'
            )

        # Check if there is any booking on the same date and room
        bookingtime_ids = Booking.objects.filter(
            Q(booking_status='pending') | Q(booking_status='active'),
            booking_date=date,
            room__room_id=room_id,
        ).values_list('bookingtime', flat=True)

        available_bookingtimes = queryset.exclude(
            bookingtime_id__in=bookingtime_ids
        )
        # End of checking
        context = self.get_serializer_context()
        context['available_bookingtimes'] = available_bookingtimes
        serializer = self.get_serializer(
            queryset, 
            many=True,
            context=context,
        )

        if serializer.data == []:
            return CustomResponse.not_found(
                message='Tidak ada available booking times pada tanggal tersebut'
            )

        return CustomResponse.list(
            data=serializer.data,
            message='Available booking times berhasil diambil',
        )
