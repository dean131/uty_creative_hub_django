from django.db import models


class Faculty(models.Model):
    faculty_id = models.AutoField(primary_key=True)
    faculty_name = models.CharField(max_length=255)


class StudyProgram(models.Model):
    study_program_id = models.AutoField(primary_key=True)
    study_program_name = models.CharField(max_length=255)
    
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

