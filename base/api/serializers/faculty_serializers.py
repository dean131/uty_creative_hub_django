from rest_framework import serializers

from base.models import Faculty
from base.api.serializers.studyprogram_serializers import StudyProgramModelSerializer


class FacultyModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = '__all__'

