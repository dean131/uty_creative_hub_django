import datetime

from django.db.models import Q

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from myapp.my_utils.custom_response import CustomResponse
from base.models import Booking, BookingTime
from base.api.serializers.booking_serializers import (
    BookingModelSerializer,
    BookingDetailModelSerializer,
)
from notification.models import Notification


class BookingModelViewSet(ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingModelSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BookingDetailModelSerializer
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

    @action(methods=['POST'], detail=False)
    def initialize(self, request, *args, **kwargs):
        user = request.user
        bookingtime_id = request.data.get('bookingtime_id')
        room_id = request.data.get('room_id')
        date = request.data.get('booking_date')

        if user.verification_status != 'verified':
            return CustomResponse.bad_request(
                message='Can\'t initiate booking, your account is not verified yet',
            )

        request.data.update({
            'user': request.user.user_id,
            'bookingtime': bookingtime_id,
            'room': room_id
        })

        # Check if there is any booking on the same date and room
        queryset = BookingTime.objects.all()
        bookeds = queryset.filter(
            Q(booking__booking_status='pending') | Q(booking__booking_status='active'),
            booking__booking_date=date, 
            booking__room__room_id=room_id,
        )

        conflict_times = []
        for booked in bookeds:
            conflicted = queryset.filter(
                Q(start_time__gte=booked.start_time, start_time__lte=booked.end_time) |
                Q(end_time__gte=booked.start_time, end_time__lte=booked.end_time) | 
                Q(start_time__lte=booked.start_time, end_time__gte=booked.end_time) |
                Q(start_time__gte=booked.start_time, end_time__lte=booked.end_time)
            )
            for conflict in conflicted:
                conflict_times.append(conflict.bookingtime_id)

        if conflict_times:
            return CustomResponse.bad_request(
                message='Can\'t initiate booking, there is a conflict with other booking',
            )
        # End of checking

        booking = self.get_queryset().filter(
            user=user,
            booking_status='initiated',
        ).first()

        if booking:
            booking.booking_needs = ""
            booking.bookingmember_set.filter().exclude(user=user).delete()
            serializer = self.get_serializer(booking, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return CustomResponse.created(
                    message='Booking initiate successfully',
                    data=serializer.data,
                )
            return CustomResponse.bad_request(
                message='Booking update failed'
            )
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return CustomResponse.created(
                message='Booking initiate successfully',
                data=serializer.data,
                headers=headers,
            )
        return CustomResponse.serializers_erros(errors=serializer.errors)
    
    def create(self, request, *args, **kwargs):
        booking_needs = request.data.get('booking_needs')

        booking = self.get_queryset().filter(
            user=request.user,
            booking_status='initiated',
        ).first()
        
        booking.booking_needs = booking_needs
        booking.save()

        return CustomResponse.ok(
            message='Booking created successfully',
        )
    
    @action(methods=['POST'], detail=True)
    def confirm(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.booking_status = 'pending'
            instance.created_at = datetime.datetime.now()
            instance.save()

            bookingmembers = instance.bookingmember_set.filter().exclude(user=request.user)
            for bookingmember in bookingmembers:
                Notification.objects.create(
                    user=bookingmember.user,
                    notification_title='Add to booking',
                    notification_body=f'You have been added to a booking by {request.user.full_name}',
                )

            return CustomResponse.ok(
                message='Booking confirmed successfully',
            )
        except:
            return CustomResponse.not_found(
                message='Booking not found',
            )
    
    @action(methods=['GET'], detail=False)
    def history(self, request, *args, **kwargs):
        user = request.user
        booking_status = request.query_params.get("booking_status")

        if not booking_status:
            return CustomResponse.bad_request(
                message='Booking status is required',
            )

        queryset = self.get_queryset().filter(booking_status=booking_status, user=user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.list(
            message='Booking history fetched successfully',
            data=serializer.data
        )
