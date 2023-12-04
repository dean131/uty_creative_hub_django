from rest_framework import serializers

from base.models import BookingTime


class BookingTimeModelSerializer(serializers.ModelSerializer):
    start_time = serializers.TimeField(format="%H:%M")
    end_time = serializers.TimeField(format="%H:%M")
    class Meta:
        model = BookingTime
        fields = '__all__'