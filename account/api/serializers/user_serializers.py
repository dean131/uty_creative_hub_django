from rest_framework.serializers import ModelSerializer

from account import models


class UserModelSerializer(ModelSerializer):
    class Meta:
        model: models.User
        fields = ['user_id', 'full_name', 'email', 'is_active', 'is_admin']


class UserRegisterSerializer(ModelSerializer):
    class Meta:
        model = models.User
        fields = ['full_name', 'email', 'password']
        extra_kwargs = {
            'password': {
                'write_only': True,
            },
        }

    def create(self, validated_data):
        user = models.User.objects.create_user(**validated_data)
        return user