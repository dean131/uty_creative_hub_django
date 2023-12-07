from rest_framework import serializers

from base.models import BookingMember


class BookingMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingMember
        fields = "__all__"