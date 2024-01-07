from rest_framework import serializers

from base.models import BookingMember

from account.api.serializers.user_serializers import (
    UserBookingDetailSerializer
)


class BookingMemberModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingMember
        fields = "__all__"


class BookingMemberBookingDetailSerializer(serializers.ModelSerializer):
    user = UserBookingDetailSerializer()
    class Meta:
        model = BookingMember
        exclude = ['booking', 'created_at']

    