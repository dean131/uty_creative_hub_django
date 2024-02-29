from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from base.api.serializers.rating_serializers import RatingModelSerializer
from base.models import Rating
from myapp.my_utils.custom_response import CustomResponse


class RatingModelViewSet(ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingModelSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # if self.get_queryset().filter(
        #     user=request.user,
        #     room__room_id=request.data.get('room_id'),
        #     ).exists():
        #     return CustomResponse.bad_request(
        #         message='You have rated this article before',
        #     )
            
        # request.data.update({
        #     'user': request.user.user_id,
        #     'room': request.data.get('room_id'),
        # })
        request.data['booking'] = request.data.get('booking')
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return CustomResponse.created(
                message='Rating created successfully',
                data=serializer.data,
                headers=headers,
            )
        return CustomResponse.serializers_erros(errors=serializer.errors)
    