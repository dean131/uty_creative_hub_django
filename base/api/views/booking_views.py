import json
import datetime

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from myapp.my_utils.custom_response import CustomResponse
from base.models import Booking, BookingMember
from base.api.serializers.booking_serializers import (
    BookingSerializer,
    BookingDetailModelSerializer,
    BookingHistorySerializer,
)


class BookingModelViewSet(ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BookingDetailModelSerializer
        if self.action == 'history':
            return BookingHistorySerializer
        return super().get_serializer_class()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.list(
            message='Booking list fetched successfully',
            data=serializer.data
        )

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return CustomResponse.retrieve(
                message='Booking fetched successfully',
                data=serializer.data
            )
        except:
            return CustomResponse.not_found(
                message='Booking not found',
            )

    # @transaction.atomic
    def create(self, request, *args, **kwargs):
        bookingtime_id_list = json.loads(request.data.get('bookingtime_id_list'))
        booking_needs = request.data.get('booking_needs')

        bookinginit = self.get_queryset().filter(
            user=request.user,
            booking_status='initiated',
        ).first()

        if not bookinginit:
            return CustomResponse.bad_request(
                message='Booking is not initiated yet',
            )
        

        for bookingtime_id in bookingtime_id_list:
            request.data.update({
                'user': request.user.user_id,
                'bookingtime': bookingtime_id,
                'booking_needs': booking_needs,
                'booking_status': 'pending',
                'booking_date': bookinginit.booking_date,
                'room': bookinginit.room.room_id,
            })
          
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                booking = serializer.save()
                bookingmembers = bookinginit.bookingmember_set.exclude(
                    user=request.user
                )
                for bookingmember in bookingmembers:
                    BookingMember.objects.create(
                        booking=booking,
                        user=bookingmember.user
                    )
            else:
                return CustomResponse.serializers_erros(serializer.errors)
            
        bookinginit.delete()
        return CustomResponse.ok(
            message='Booking created successfully',
        )

    @action(methods=['POST'], detail=False)
    def initialize(self, request, *args, **kwargs):
        room_id = request.data.get('room_id')
        booking_date = request.data.get('booking_date')
        bookingtime_id_list = request.data.get('bookingtime_id_list')

        bookings = self.get_queryset().filter(
            booking_date=booking_date,
            room__room_id=room_id,
        ).values_list('bookingtime', flat=True)

        if bookings.filter(bookingtime_id__in=bookingtime_id_list).exists():
            return CustomResponse.bad_request(
                message='Booking is already exists',
            )
        
        bookinginit = self.get_queryset().filter(
            booking_status='initiated',
            user=request.user,
        ).first()

        if bookinginit: bookinginit.delete() 

        request.data.update({
            'user': request.user.user_id,
            'room': room_id,    
            'booking_status': 'initiated',
        })
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return CustomResponse.created(
                message='Booking initialized successfully',
                data=serializer.data,
                headers=headers
            )
        return CustomResponse.serializers_erros(serializer.errors)
    
    @action(methods=['POST'], detail=False)
    def validate(self, request, *args, **kwargs):
        if request.user.verification_status != 'verified':
            return CustomResponse.bad_request(
                message='User is not verified',
            )

        return CustomResponse.ok(
            message='User is verified',
        )

    @action(methods=['GET'], detail=False)
    def history(self, request, *args, **kwargs):
        user = request.user
        booking_status = request.query_params.get("booking_status")

        if not booking_status:
            return CustomResponse.bad_request(
                message='Booking status is required',
            )

        queryset = self.get_queryset().filter(
            booking_status=booking_status, 
            user=user,
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.list(
            message='Booking history fetched successfully',
            data=serializer.data
        )

    @action(methods=['POST'], detail=True)
    def scan(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            date_time = datetime.datetime.now()
            booking_date = instance.booking_date
            booking_start_time = instance.bookingtime.start_time
            booking_end_time = instance.bookingtime.end_time

            start_date_time = datetime.datetime.combine(booking_date, booking_start_time)
            end_date_time = datetime.datetime.combine(booking_date, booking_end_time)
            
            is_time_valid = (date_time >= start_date_time) and (date_time <= end_date_time)
            if not is_time_valid:
                return CustomResponse.bad_request(
                    message='Booking time is not valid',
                )
            
            return CustomResponse.ok(
                message='Booking time is valid',
            )
        except:
            return CustomResponse.not_found(
                message='Booking not found',
            )

