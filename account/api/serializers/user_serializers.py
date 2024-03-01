from rest_framework import serializers

from account.models import User
from account.api.serializers.userprofile_serializers import (
    UserProfileBookingDetailSerializer,
    UserProfileSerializer,
    UserProfileUserDetailSerializer
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {
                'write_only': True,
            },
        }


class UserDetailSerializer(UserSerializer):
    userprofile = serializers.SerializerMethodField()

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
        try:
            return UserProfileUserDetailSerializer(obj.userprofile, context=self.context).data
        except:
            pass
        return None


class UserListSerializer(serializers.ModelSerializer):
    userprofile = serializers.SerializerMethodField()
    
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
        try:
            return UserProfileSerializer(obj.userprofile, context=self.context).data
        except:
            pass
        return None


class UserRegisterSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ['full_name', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    

class UserBookingDetailSerializer(serializers.ModelSerializer):
    userprofile = UserProfileBookingDetailSerializer()
    class Meta:
        model = User
        fields = ['full_name', 'email', 'userprofile']