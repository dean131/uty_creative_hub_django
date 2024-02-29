from rest_framework import serializers

from base.models import Rating


class RatingModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'


class RatingDetailModelSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    class Meta:
        model = Rating
        fields = '__all__'

    def get_user(self, obj):
        return obj.booking.user.full_name