from django.db.models import Q

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from base.api.serializers.bookingtime_serializers import BookingTimeModelSerializer
from base.models import BookingTime


class BookingTimeModelViewSet(ModelViewSet):
    queryset = BookingTime.objects.all()
    serializer_class = BookingTimeModelSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['GET'])
    def available(self, request, *args, **kwargs):
        date = self.request.query_params.get('date')
        room_id = self.request.query_params.get('room_id')

        if not date:
            return Response(
                {
                    'success': False,
                    'message': 'Date is required',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if not room_id:
            return Response(
                {
                    'success': False,
                    'message': 'Room id is required',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Check if there is any booking on the same date and room
        queryset = self.get_queryset()
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
        # End of checking

        availables = queryset.filter(~Q(bookingtime_id__in=conflict_times))
        serializer = self.get_serializer(availables, many=True)

        return Response(
            {
                'success': True,
                'message': 'Booking time retrieved successfully',
                'data': serializer.data,
            },
            status=status.HTTP_200_OK,
        )


