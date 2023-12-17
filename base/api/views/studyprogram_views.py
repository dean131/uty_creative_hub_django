from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny

from base.api.serializers.studyprogram_serializers import StudyProgramModelSerializer

from base.models import StudyProgram
from myapp.my_utils.custom_response import CustomResponse


class StudyProgramModelViewSet(ModelViewSet):
    queryset = StudyProgram.objects.all()
    serializer_class = StudyProgramModelSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        faculty_id = request.query_params.get('faculty_id', None)
        if faculty_id is not None:
            queryset = queryset.filter(faculty__faculty_id=faculty_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.list(
            message="List of all study programs fetched successfully",
            data=serializer.data
        )