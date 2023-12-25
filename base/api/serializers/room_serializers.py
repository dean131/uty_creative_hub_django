from rest_framework import serializers

from base.api.serializers.rating_serializers import RatingDetailModelSerializer
from base.api.serializers.roomfacility_serializers import RoomFacilityModelSerializer
from base.api.serializers.roomimage_serializers import RoomImageModelSerializer
from base.models import Room, Rating, RoomFacility


class RoomModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'


class RoomBookingHistoryModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['room_name']


class RoomListModelSerializer(serializers.ModelSerializer):
    roomimages = serializers.SerializerMethodField()
    class Meta:
        model = Room
        fields = [
            "room_id",
            "room_name",
            "floor",
            "room_type",
            "room_capacity",
            "room_rating",
            "total_raters",
            "created_at",
            "roomimages",
        ]

    def get_roomimages(self, obj):
        roomimages = obj.roomimage_set.all()
        return RoomImageModelSerializer(roomimages, many=True, context=self.context).data


class RoomDetailModelSerializer(serializers.ModelSerializer):
    ratings = serializers.SerializerMethodField()
    facilities = serializers.SerializerMethodField()
    roomimages = serializers.SerializerMethodField()
    class Meta:
        model = Room
        fields = [
            "room_id",
            "room_name",
            "floor",
            "room_type",
            "room_capacity",
            "room_description",
            "room_rating",
            "total_raters",
            "created_at",
            "ratings",
            "facilities",
            "roomimages",
        ]

    def get_ratings(self, obj):
        ratings = obj.rating_set.all()
        return RatingDetailModelSerializer(ratings, many=True).data
    
    def get_facilities(self, obj):
        facilities = RoomFacility.objects.filter(room=obj)
        return RoomFacilityModelSerializer(facilities, many=True, context=self.context).data
    
    def get_roomimages(self, obj):
        roomimages = obj.roomimage_set.all()
        return RoomImageModelSerializer(roomimages, many=True, context=self.context).data
    

class RoomDetailBookingModelSerializer(serializers.ModelSerializer):
    room_images = serializers.SerializerMethodField()
    is_rated = serializers.SerializerMethodField()
    class Meta:
        model = Room
        fields = ['room_name', 'is_rated', 'room_capacity', 'room_images']

    def get_room_images(self, obj):
        room_image = obj.roomimage_set.all()
        return RoomImageModelSerializer(room_image, many=True, context=self.context).data
    
    def get_is_rated(self, obj):
        user = self.context.get('request').user
        rating = Rating.objects.filter(user=user, room=obj)
        if rating.exists():
            return True
        return False



