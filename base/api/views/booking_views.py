import json
import datetime

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from myapp.custom_pagination import CustomPaginationSerializer
from myapp.my_utils.custom_response import CustomResponse
from base.models import Booking, BookingMember, CeleryTask, BookingTime
from base.api.serializers.booking_serializers import (
    BookingSerializer,
    BookingDetailModelSerializer,
    BookingHistorySerializer,
)

from paho.mqtt import publish
from django.conf import settings
from django.db.models import Q
from django.db import transaction

from celery.result import AsyncResult

from notification.tasks import create_notification


class BookingModelViewSet(ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = '__all__'
    ordering_fields = '__all__'
    pagination_class = CustomPaginationSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BookingDetailModelSerializer
        if self.action == 'history':
            return BookingHistorySerializer
        return super().get_serializer_class()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return CustomResponse.retrieve(
            message='Booking berhasil diambil',
            data=serializer.data
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
                message='Booking belum diinisialisasi',
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
            message='Booking berhasil dibuat',
        )

    @action(methods=['POST'], detail=False)
    def initialize(self, request, *args, **kwargs):
        room_id = request.data.get('room_id')
        booking_date = request.data.get('booking_date')
        bookingtime_id_list = request.data.get('bookingtime_id_list')

        bookings = self.get_queryset().filter(
            Q(booking_status='pending') | Q(booking_status='active'),
            booking_date=booking_date,
            room__room_id=room_id,
            bookingtime_id__in=bookingtime_id_list
        )

        if bookings:
            return CustomResponse.bad_request(
                message='Booking tidak tersedia',
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
                message='Booking berhasil diinisialisasi',
                data=serializer.data,
                headers=headers
            )
        return CustomResponse.serializers_erros(serializer.errors)
    
    @action(methods=['POST'], detail=False)
    def validate(self, request, *args, **kwargs):
        user_status_messages = {
            'verified': 'Status akun sudah terverifikasi',
            'rejected': 'Status akun ditolak',
            'suspend': 'Status akun ditangguhkan',
            'unverified': 'Status akun belum terverifikasi',
        }

        user_status = request.user.verification_status
        if user_status == 'verified':
            return CustomResponse.ok(
                message=user_status_messages[user_status],
            )
        return CustomResponse.bad_request(
            message=user_status_messages.get(user_status, 'Status akun tidak valid'),
        )

    @action(methods=['GET'], detail=False)
    def history(self, request, *args, **kwargs):
        user = request.user
        booking_status = request.query_params.get("booking_status")

        if not booking_status:
            return CustomResponse.bad_request(
                message='Booking status diperlukan',
            )

        if booking_status in  ["rejected", "canceled"]:
            queryset = self.get_queryset().filter(
                Q(booking_status="rejected") | Q(booking_status="canceled"),
                user=user,
            )
        else:
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
            message='Booking berhasil diambil',
            data=serializer.data
        )

    @action(methods=['POST'], detail=True)
    def change_booking_status(self, request, *args, **kwargs):
        booking = self.get_object()
        booking_status = request.data.get('booking_status')

        if not booking_status:
            return CustomResponse.bad_request(
                message='Booking status diperlukan',
            )
        
        booking_status_list = [
            'initiated', 
            'pending', 
            'active', 
            'rejected', 
            'canceled', 
            'completed'
        ]
        
        if booking_status not in booking_status_list:
            return CustomResponse.bad_request(
                message='Booking status tidak valid',
            )
        
        booking.booking_status = booking_status
        booking.save()
        booking.user.verrifcation_status = 'suspend'
        booking.user.save()
        return CustomResponse.ok(
            message='Booking status berhasil diubah',
        )
    
    @action(methods=['POST'], detail=True)
    def cancel_booking(self, request, *args, **kwargs):
        booking = self.get_object()
        cancellation_reason = request.data.get('cancellation_reason')
        
        booking.booking_status = 'canceled'
        booking.cancellation_reason = cancellation_reason
        booking.save()
        return CustomResponse.ok(
            message='Booking berhasil dibatalkan',
        )

    @action(methods=['POST'], detail=False)
    def scan(self, request, *args, **kwargs):
        user = request.user
        now = datetime.datetime.now()
        date_now =  now.date()
        time_now = now.time()

        booking = Booking.objects.filter(
            user=user, 
            booking_date=date_now, 
            booking_status='active',
        ).order_by('bookingtime__start_time').first()

        if not booking:
            return CustomResponse.bad_request(
                message='Booking tidak ditemukan',
            )
        
        bookingtime = booking.bookingtime
        start_time = bookingtime.start_time
        end_time = bookingtime.end_time
        
        if time_now < start_time:
            return CustomResponse.bad_request(
                message=f'Waktu booking belum dimulai, waktu booking dimulai pada {start_time}',
            )
        
        if time_now > end_time:
            return CustomResponse.bad_request(
                message='Waktu booking sudah berakhir',
            )
        
        # Pesan yang akan dipublish
        message = 'True'

        # Melakukan publish pesan
        publish.single(
            settings.MQTT_TOPIC, 
            message, 
            hostname=settings.MQTT_SERVER, 
            port=settings.MQTT_PORT,
        )
    
        return CustomResponse.ok(
            message='Berhasil scan QR Code',
        )

    @transaction.atomic
    @action(methods=['POST'], detail=True)
    def reschedule(self, request, *args, **kwargs):
        booking = self.get_object()
        new_booking_date = request.data.get('booking_date')
        new_bookingtime = request.data.get('bookingtime')

        if not new_bookingtime:
            return CustomResponse.bad_request(
                message='Waktu baru diperlukan',
            )
        
        bookingtime = BookingTime.objects.filter(bookingtime_id=new_bookingtime).first()

        if not new_booking_date:
            return CustomResponse.bad_request(
                message='Tanggal baru diperlukan',
            )
        
        if str(booking.booking_date) == new_booking_date and booking.bookingtime == bookingtime:
            return CustomResponse.bad_request(
                message='Booking tidak dapat direschedule ke waktu yang sama',
            )
        
        if booking.booking_status not in ['pending', 'active']:
            return CustomResponse.bad_request(
                message='Booking tidak dapat direschedule',
            )
        
        # Check if time is booked
        booking_exists = Booking.objects.filter(
            booking_date=new_booking_date, 
            bookingtime=bookingtime
        ).exclude(booking_id=booking.booking_id).first()
        if booking_exists:
            return CustomResponse.bad_request(
                message=f'Gagal direschedule, booking telah ada. Kode booking: {booking_exists.booking_id}',
            )
        
        celerytasks = CeleryTask.objects.filter(booking=booking)
        if celerytasks.exists():
            for celerytask in celerytasks:
                task = AsyncResult(celerytask.task_id)
                task.revoke()
        celerytasks.delete()

        booking.reschedule(new_booking_date, bookingtime)

        create_notification.delay(
            title='Reschedule Booking',
            body=f'Booking {booking.booking_id} berhasil direschedule',
            user_id=booking.user.user_id,
            booking_id=None,
            write=True,
        )
            
        return CustomResponse.ok(
            message='Booking berhasil direschedule',
        )
