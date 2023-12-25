from rest_framework import serializers

from base.models import BookingTime


class BookingTimeModelSerializer(serializers.ModelSerializer):
    start_time = serializers.TimeField(format="%H:%M")
    end_time = serializers.TimeField(format="%H:%M")
    class Meta:
        model = BookingTime
        fields = '__all__'


class BookingTimeAvaliableModelSerializer(BookingTimeModelSerializer):
    is_available = serializers.SerializerMethodField()

    def get_is_available(self, obj):
        available_bookingtimes = self.context.get('available_bookingtimes')
        if obj in available_bookingtimes:
            return True
        return False