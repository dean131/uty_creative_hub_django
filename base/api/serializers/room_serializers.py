from rest_framework import serializers

from base.api.serializers.rating_serializers import RatingModelSerializer
from base.api.serializers.roomfacility_serializers import RoomFacilityModelSerializer
from base.api.serializers.roomimage_serializers import RoomImageModelSerializer
from base.models import Room, Rating, RoomFacility


class RoomModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'


class RoomDetailModelSerializer(serializers.ModelSerializer):
    ratings = serializers.SerializerMethodField()
    facilities = serializers.SerializerMethodField()
    roomimages = serializers.SerializerMethodField()
    class Meta:
        model = Room
        fields = '__all__'

    def get_ratings(self, obj):
        ratings = obj.rating_set.all()
        return RatingModelSerializer(ratings, many=True).data
    
    def get_facilities(self, obj):
        facilities = RoomFacility.objects.filter(room=obj)
        return RoomFacilityModelSerializer(facilities, many=True, context=self.context).data
    
    def get_roomimages(self, obj):
        roomimages = obj.roomimage_set.all()
        return RoomImageModelSerializer(roomimages, many=True, context=self.context).data