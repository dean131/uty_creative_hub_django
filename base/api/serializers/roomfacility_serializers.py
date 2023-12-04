from rest_framework import serializers

from base.models import RoomFacility


class RoomFacilityModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomFacility
        fields = '__all__'