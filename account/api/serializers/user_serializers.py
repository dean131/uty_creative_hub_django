from rest_framework import serializers

from account.models import User
from account.api.serializers.userprofile_serializers import (
    UserProfileBookingDetailModelSerializer,
    UserProfileModelSerializer,
    UserProfileUserDetailModelSerializer
)

from myapp.my_utils.string_formater import name_formater


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
    first_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'user_id',
            'userprofile',
            'full_name',
            'first_name',
            'email',
            'is_active',
            'is_admin',
            'verification_status',
        ]

    def get_userprofile(self, obj):
        if obj.userprofile:
            return UserProfileUserDetailModelSerializer(obj.userprofile, context=self.context).data
        return None
    
    def get_first_name(self, obj):
        return name_formater(obj.full_name)


class UserListSerializer(UserModelSerializer):
    userprofile = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()

    def get_userprofile(self, obj):
        if obj.userprofile:
            return UserProfileModelSerializer(obj.userprofile, context=self.context).data
        return None
    
    def get_first_name(self, obj):
        return name_formater(obj.full_name)


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