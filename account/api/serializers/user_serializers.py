from rest_framework import serializers

from account.models import User, UserProfile
from account.api.serializers.userprofile_serializers import UserProfileBookingDetailModelSerializer


class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model: User
        fields = ['user_id', 'full_name', 'email', 'is_active', 'is_admin']


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['full_name', 'email', 'password']
        extra_kwargs = {
            'password': {
                'write_only': True,
            },
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    

class UserBookingDetailModelSerializer(serializers.ModelSerializer):
    userprofile = UserProfileBookingDetailModelSerializer()
    class Meta:
        model = User
        fields = ['full_name', 'userprofile']

    # def get_userprofile(self, obj):
    #     userprofile = UserProfile.objects.filter(user=obj)
    #     if not userprofile:
    #         return None
    #     return UserProfileModelSerializer(userprofile).data