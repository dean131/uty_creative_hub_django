import datetime

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
        time_now = datetime.datetime.now().time()
        date_now = self.context['request'].query_params.get('date')

        available_bookingtimes = self.context.get('available_bookingtimes')
        if obj not in available_bookingtimes:
            return False
        
        if date_now == datetime.datetime.now().strftime("%Y-%m-%d"):
            if obj.start_time <= time_now:
                return False
        
        return True