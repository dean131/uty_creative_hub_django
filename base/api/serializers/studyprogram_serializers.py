from rest_framework.serializers import ModelSerializer

from base.models import StudyProgram


class StudyProgramModelSerializer(ModelSerializer):
    class Meta:
        model = StudyProgram
        fields = '__all__'