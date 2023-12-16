from rest_framework import serializers

from account.models import UserProfile


class UserProfileModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class UserProfileBookingDetailModelSerializer(serializers.ModelSerializer):
    studyprogram = serializers.SerializerMethodField()
    class Meta:
        model = UserProfile
        fields = ['student_id_number', 'studyprogram']

    def get_studyprogram(self, obj):
        return obj.studyprogram.study_program_name

