from rest_framework import serializers

from base.models import BookingMember

from account.api.serializers.user_serializers import (
    UserBookingDetailModelSerializer
)


class BookingMemberModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingMember
        fields = "__all__"


class BookingMemberBookingDetailSerializer(serializers.ModelSerializer):
    user = UserBookingDetailModelSerializer()
    class Meta:
        model = BookingMember
        exclude = ['booking', 'created_at']

    