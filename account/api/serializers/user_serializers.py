from rest_framework import serializers

from account.models import User
from account.api.serializers.userprofile_serializers import (
    UserProfileBookingDetailModelSerializer,
    UserProfileModelSerializer,
    UserProfileUserDetailModelSerializer
)


class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {
                'write_only': True,
            },
        }


class UserDetailModelSerializer(UserModelSerializer):
    userprofile = serializers.SerializerMethodField()

    def get_userprofile(self, obj):
        if obj.userprofile:
            return UserProfileUserDetailModelSerializer(obj.userprofile).data
        return None


class UserListSerializer(UserModelSerializer):
    userprofile = serializers.SerializerMethodField()

    def get_userprofile(self, obj):
        if obj.userprofile:
            return UserProfileModelSerializer(obj.userprofile).data
        return None


class UserRegisterSerializer(UserModelSerializer):
    class Meta:
        model = User
        fields = ['full_name', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    

class UserBookingDetailModelSerializer(serializers.ModelSerializer):
    userprofile = UserProfileBookingDetailModelSerializer()
    class Meta:
        model = User
        fields = ['full_name', 'email', 'userprofile']