from rest_framework import serializers

from base.models import Banner


class BannerModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'