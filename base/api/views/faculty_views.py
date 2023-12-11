from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from base.api.serializers.faculty_serializers import FacultyRegisterModelSerializer
from base.models import Faculty
from myapp.my_utils.custom_response import CustomResponse


class FacultyModelViewSet(ModelViewSet):
    queryset = Faculty.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = FacultyRegisterModelSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.list(
            message="List of all faculties fetched successfully",
            data=serializer.data
        )
        

