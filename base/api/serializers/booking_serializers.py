from rest_framework.serializers import ModelSerializer

from base.models import Booking


class BookingModelSerializer(ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'