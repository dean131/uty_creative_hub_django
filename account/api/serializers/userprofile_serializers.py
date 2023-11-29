from rest_framework.serializers import ModelSerializer

from account.models import UserProfile
from base.api.serializers.studyprogram_serializers import StudyProgramModelSerializer


class UserProfileModelSerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

