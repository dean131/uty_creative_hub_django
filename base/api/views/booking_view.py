import datetime

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from myapp.my_utils.custom_response import CustomResponse
from base.models import Booking, BookingTime, Room
from base.api.serializers.booking_serializers import (
    BookingModelSerializer,
    BookingDetailModelSerializer,
)


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

    def create(self, request, *args, **kwargs):
        user = self.request.user
        bookingtime_id = request.data.get('bookingtime_id')
        room_id = request.data.get('room_id')
        print(request.data)

        request.data.update({
            'user': request.user.user_id,
            'bookingtime': bookingtime_id,
            'room': room_id
        })

        booking = self.get_queryset().filter(
            user=user,
            booking_status='created',
        ).first()

        if booking:
            serializer = self.get_serializer(booking, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return CustomResponse.created(
                    message='Booking created successfully',
                    data=serializer.data,
                )
            return CustomResponse.bad_request(
                message='Booking update failed.'
            )
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return CustomResponse.created(
                message='Booking created successfully',
                data=serializer.data,
                headers=headers,
            )
        return CustomResponse.serializers_erros(errors=serializer.errors)
    
    @action(methods=['POST'], detail=True)
    def confirm(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.booking_status = 'pending'
            instance.created_at = datetime.datetime.now()
            instance.save()
            return CustomResponse.ok(
                message='Booking confirmed successfully',
            )
        except:
            return CustomResponse.not_found(
                message='Booking not found',
            )
    
    @action(methods=['GET'], detail=False)
    def history(self, request, *args, **kwargs):
        user = self.request.user
        booking_status = self.request.query_params.get("booking_status")

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
