from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from base.api.serializers.banner_serializers import BannerSerializer
from base.models import Banner
from myapp.my_utils.custom_response import CustomResponse


class BannerModelViewSet(ModelViewSet):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.list(
            message='Banner list fetched successfully',
            data=serializer.data
        )















