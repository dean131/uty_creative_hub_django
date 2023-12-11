from rest_framework import serializers

from base.models import Faculty
from base.api.serializers.studyprogram_serializers import StudyProgramModelSerializer


class FacultyRegisterModelSerializer(serializers.ModelSerializer):
    studyprograms = serializers.SerializerMethodField()
    class Meta:
        model = Faculty
        fields = ['faculty_id', 'faculty_name', 'studyprograms']

    def get_studyprograms(self, obj):
        studyprograms = obj.studyprogram_set.filter()
        return StudyProgramModelSerializer(studyprograms, many=True).data

