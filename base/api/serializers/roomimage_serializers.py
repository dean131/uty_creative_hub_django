from rest_framework import serializers

from base.models import RoomImage


class RoomImageModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomImage
        fields = ['roomimage_id', 'room_image']