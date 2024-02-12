from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny

from base.api.serializers.studyprogram_serializers import StudyProgramModelSerializer

from base.models import StudyProgram
from myapp.my_utils.custom_response import CustomResponse


class StudyProgramModelViewSet(ModelViewSet):
    queryset = StudyProgram.objects.all()
    serializer_class = StudyProgramModelSerializer
    permission_classes = [AllowAny]
    filterset_fields = '__all__'


    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.list(
            message="Program Studi berhasil diambil",
            data=serializer.data
        )
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return CustomResponse.created(
                message="Study program berhasil ditambahkan",
                data=serializer.data,
                headers=headers
            )
        return CustomResponse.serializers_erros(serializer.errors)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

            return CustomResponse.updated(
                message="Study program berhasil diupdate",
                data=serializer.data
            )
        return CustomResponse.serializers_erros(serializer.errors)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return CustomResponse.deleted(
            message="Study program berhasil dihapus"
        )
