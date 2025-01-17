from rest_framework import serializers

from account.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class UserProfileBookingDetailSerializer(serializers.ModelSerializer):
    studyprogram = serializers.SerializerMethodField()
    faculty = serializers.SerializerMethodField()
    class Meta:
        model = UserProfile
        fields = ['student_id_number', 'whatsapp_number', 'faculty', 'studyprogram']

    def get_studyprogram(self, obj):
        return obj.studyprogram.study_program_name
    
    def get_faculty(self, obj):
        return obj.faculty.faculty_name


class UserProfileUserDetailSerializer(UserProfileBookingDetailSerializer):
    class Meta:
        model = UserProfile
        exclude = ['user']
    
